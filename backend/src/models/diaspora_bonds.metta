;; Nimo Diaspora Bonds Implementation
;; This file contains the MeTTa implementation for the diaspora impact bonds system

;; =============================
;; BOND DATA STRUCTURES
;; =============================

;; Impact bond core structure
(= (ImpactBond $id $creator_id $title $target_amount $created_at)
   (Bond $id $creator_id $title $target_amount $created_at))

;; Bond metadata
(= (BondMetadata $id $key $value)
   (HasMetadata $id $key $value))

;; Bond status
(= (BondStatus $id "active")
   (IsActive $id))
(= (BondStatus $id "funded")
   (IsFunded $id))
(= (BondStatus $id "completed")
   (IsCompleted $id))
(= (BondStatus $id "canceled")
   (IsCanceled $id))

;; Bond cause categorization
(= (BondCause $id $cause)
   (SupportsCause $id $cause))

;; Bond investment record
(= (BondInvestment $id $investor_id $amount $timestamp)
   (InvestedIn $id $investor_id $amount $timestamp))

;; Bond milestone
(= (BondMilestone $bond_id $milestone_id $description $evidence $timestamp)
   (HasMilestone $bond_id $milestone_id $description $evidence $timestamp))

;; Milestone verification
(= (MilestoneVerification $milestone_id $verifier_id $timestamp)
   (MilestoneVerifiedBy $milestone_id $verifier_id $timestamp))

;; Bond NFT representation
(= (BondNFT $bond_id $nft_id $metadata)
   (RepresentedByNFT $bond_id $nft_id $metadata))

;; =============================
;; BOND OPERATIONS
;; =============================

;; Create a new impact bond
(= (create-impact-bond $id $creator_username $title $target_amount)
   (let (($creator_id (GetUserID $creator_username))
         ($timestamp (CurrentTimestamp)))
     (ImpactBond $id $creator_id $title $target_amount $timestamp)
     (BondStatus $id "active")
     (BondMetadata $id "description" $title)
     (BondMetadata $id "funded_amount" 0)
     $id))

;; Link bond to cause
(= (link-bond-to-cause $bond_id $cause)
   (BondCause $bond_id $cause))

;; Add bond metadata
(= (add-bond-metadata $bond_id $key $value)
   (BondMetadata $bond_id $key $value))

;; Invest in a bond
(= (purchase-impact-bond $bond_id $investor_username $amount)
   (let* (($investor_id (GetUserID $investor_username))
          ($timestamp (CurrentTimestamp))
          ($status_query (BondStatus $bond_id $status))
          ($funded_amount_query (BondMetadata $bond_id "funded_amount" $current_funded))
          ($target_amount_query (ImpactBond $bond_id $creator_id $title $target_amount $created_at))
          ($new_funded_amount (+ $current_funded $amount)))
     (if (not (Equal $status "active"))
         (Error "Cannot invest in a bond that is not active")
         (if (> $new_funded_amount $target_amount)
             (Error "Investment would exceed target amount")
             (let ()
               (BondInvestment $bond_id $investor_id $amount $timestamp)
               (BondMetadata $bond_id "funded_amount" $new_funded_amount)
               ;; Create NFT receipt for investor
               (let (($nft_id (GenerateNFTID $bond_id $investor_id))
                     ($metadata (GenerateNFTMetadata $bond_id $investor_username $amount)))
                 (BondNFT $bond_id $nft_id $metadata)
                 ;; Update bond status if fully funded
                 (if (= $new_funded_amount $target_amount)
                     (BondStatus $bond_id "funded")
                     null)
                 $nft_id))))))

;; Record a bond milestone
(= (record-bond-milestone $bond_id $description $evidence)
   (let (($milestone_id (GenerateMilestoneID))
         ($timestamp (CurrentTimestamp)))
     (BondMilestone $bond_id $milestone_id $description $evidence $timestamp)
     $milestone_id))

;; Verify a bond milestone
(= (verify-bond-milestone $bond_id $milestone_description $verifier_name)
   (let* (($verifier_id (GetUserID $verifier_name))
          ($timestamp (CurrentTimestamp))
          ($milestone_query (BondMilestone $bond_id $milestone_id $milestone_description $evidence $created_at)))
     (MilestoneVerification $milestone_id $verifier_id $timestamp)
     ;; Check if all milestones are verified and mark bond as completed if needed
     (check-bond-completion $bond_id)
     $milestone_id))

;; Check if all milestones are verified to mark bond as completed
(= (check-bond-completion $bond_id)
   (let* (($milestones (FindAll (BondMilestone $bond_id $milestone_id $description $evidence $timestamp)))
          ($all_verified (AllMilestonesVerified $milestones))
          ($status_query (BondStatus $bond_id $status)))
     (if (and $all_verified (= $status "funded"))
         (BondStatus $bond_id "completed")
         null)))

;; Check if all milestones are verified
(= (AllMilestonesVerified $milestones)
   (FoldLeft $milestones true (lambda ($acc $milestone)
                                 (and $acc (IsMilestoneVerified $milestone)))))

;; Check if a milestone is verified
(= (IsMilestoneVerified $milestone)
   (let (($milestone_id (GetMilestoneID $milestone)))
     (not (IsNull (MilestoneVerification $milestone_id $verifier_id $timestamp)))))

;; Cancel a bond (creator only)
(= (cancel-bond $bond_id $creator_username $reason)
   (let* (($creator_id (GetUserID $creator_username))
          ($bond_query (ImpactBond $bond_id $bond_creator_id $title $target_amount $created_at))
          ($status_query (BondStatus $bond_id $status)))
     (if (not (Equal $creator_id $bond_creator_id))
         (Error "Only the creator can cancel a bond")
         (if (or (Equal $status "completed") (Equal $status "canceled"))
             (Error "Cannot cancel a completed or already canceled bond")
             (let ()
               (BondStatus $bond_id "canceled")
               (BondMetadata $bond_id "cancellation_reason" $reason)
               (BondMetadata $bond_id "canceled_at" (CurrentTimestamp))
               ;; Process refunds would happen here in a full implementation
               true)))))

;; Generate NFT for bond investment
(= (GenerateNFTID $bond_id $investor_id)
   (let (($random (RandomString 8)))
     (ConcatStrings "nft-" $bond_id "-" $investor_id "-" $random)))

;; Generate NFT metadata
(= (GenerateNFTMetadata $bond_id $investor_username $amount)
   (let* (($bond_query (ImpactBond $bond_id $creator_id $title $target_amount $created_at))
          ($creator_query (Identity $creator_id $creator_username $created_at))
          ($metadata (CreateObject)))
     (ObjectSet $metadata "title" (ConcatStrings "Impact Investment: " $title))
     (ObjectSet $metadata "description" (ConcatStrings "Investment of " $amount " by " $investor_username " in " $title " created by " $creator_username))
     (ObjectSet $metadata "bond_id" $bond_id)
     (ObjectSet $metadata "investor" $investor_username)
     (ObjectSet $metadata "creator" $creator_username)
     (ObjectSet $metadata "amount" $amount)
     (ObjectSet $metadata "timestamp" (CurrentTimestamp))
     $metadata))

;; =============================
;; BOND QUERIES
;; =============================

;; Get bond details
(= (get-bond-details $bond_id)
   (let* (($bond_query (ImpactBond $bond_id $creator_id $title $target_amount $created_at))
          ($status_query (BondStatus $bond_id $status))
          ($metadata (CollectBondMetadata $bond_id))
          ($investments (CollectBondInvestments $bond_id))
          ($milestones (CollectBondMilestones $bond_id))
          ($causes (CollectBondCauses $bond_id)))
     (BondDetails $bond_id $creator_id $title $target_amount $created_at $status 
                  $metadata $investments $milestones $causes)))

;; Get bonds by creator
(= (get-bonds-by-creator $username)
   (let (($creator_id (GetUserID $username)))
     (FindAll (ImpactBond $id $creator_id $title $target_amount $created_at))))

;; Get bonds by investor
(= (get-bonds-by-investor $username)
   (let* (($investor_id (GetUserID $username))
          ($investments (FindAll (BondInvestment $bond_id $investor_id $amount $timestamp))))
     (map $investments GetBondFromInvestment)))

;; Get bonds by cause
(= (get-bonds-by-cause $cause)
   (let (($cause_bonds (FindAll (BondCause $bond_id $cause))))
     (map $cause_bonds GetBondFromCause)))

;; Get bond milestones
(= (get-bond-milestones $bond_id)
   (CollectBondMilestones $bond_id))

;; Get bond investments
(= (get-bond-investments $bond_id)
   (CollectBondInvestments $bond_id))

;; Get bond NFTs
(= (get-bond-nfts $bond_id)
   (FindAll (BondNFT $bond_id $nft_id $metadata)))

;; Get investor NFTs
(= (get-investor-nfts $username)
   (let* (($investor_id (GetUserID $username))
          ($investments (FindAll (BondInvestment $bond_id $investor_id $amount $timestamp))))
     (FlatMap $investments GetNFTsForInvestment)))

;; =============================
;; UTILITY FUNCTIONS
;; =============================

;; Generate milestone ID
(= (GenerateMilestoneID)
   (let (($random (RandomString 16)))
     (ConcatString "milestone-" $random)))

;; Get milestone ID from milestone atom
(= (GetMilestoneID $milestone)
   (let (($query (BondMilestone $bond_id $milestone_id $description $evidence $timestamp)))
     $milestone_id))

;; Get bond from investment
(= (GetBondFromInvestment $investment)
   (let* (($query (BondInvestment $bond_id $investor_id $amount $timestamp))
          ($bond_query (ImpactBond $bond_id $creator_id $title $target_amount $created_at)))
     $bond_query))

;; Get bond from cause
(= (GetBondFromCause $cause_atom)
   (let* (($query (BondCause $bond_id $cause))
          ($bond_query (ImpactBond $bond_id $creator_id $title $target_amount $created_at)))
     $bond_query))

;; Get NFTs for an investment
(= (GetNFTsForInvestment $investment)
   (let* (($query (BondInvestment $bond_id $investor_id $amount $timestamp))
          ($nfts (FindAll (BondNFT $bond_id $nft_id $metadata))))
     $nfts))

;; Helper to collect all metadata for a bond
(= (CollectBondMetadata $bond_id)
   (FindAll (BondMetadata $bond_id $key $value)))

;; Helper to collect all investments for a bond
(= (CollectBondInvestments $bond_id)
   (FindAll (BondInvestment $bond_id $investor_id $amount $timestamp)))

;; Helper to collect all milestones for a bond
(= (CollectBondMilestones $bond_id)
   (FindAll (BondMilestone $bond_id $milestone_id $description $evidence $timestamp)))

;; Helper to collect all causes for a bond
(= (CollectBondCauses $bond_id)
   (FindAll (BondCause $bond_id $cause)))

;; Object operations (implementation would be provided by MeTTa runtime)
(= (CreateObject)
   (NewObject))

(= (ObjectSet $obj $key $value)
   (SetObjectProperty $obj $key $value))

;; Lambda and functional helpers
(= (lambda $args $body)
   (Lambda $args $body))

;; FlatMap function implementation (would be provided by MeTTa runtime)
(= (FlatMap $list $function)
   (FlatMapImplementation $list $function))

;; =============================
;; END OF BOND IMPLEMENTATION
;; =============================