;; Nimo Token Implementation
;; This file contains the MeTTa implementation for the token economic system

;; =============================
;; TOKEN DATA STRUCTURES
;; =============================

;; Token types
(= (TokenType "NIMO") (PlatformToken))
(= (TokenType "ADA") (BlockchainNativeToken "Cardano"))
(= (TokenType "ETH") (BlockchainNativeToken "Ethereum"))

;; Token balance
(= (TokenBalance $user_id $token_type $amount)
   (HasBalance $user_id $token_type $amount))

;; Token transaction
(= (TokenTransaction $id $token_type $from $to $amount $reason $timestamp)
   (Transaction $id $token_type $from $to $amount $reason $timestamp))

;; Token minting record
(= (TokenMinting $id $token_type $to $amount $reason $timestamp)
   (MintingRecord $id $token_type $to $amount $reason $timestamp))

;; Token burning record
(= (TokenBurning $id $token_type $from $amount $reason $timestamp)
   (BurningRecord $id $token_type $from $amount $reason $timestamp))

;; Token award rules
(= (TokenAwardRule $contribution_category $base_amount)
   (AwardRule $contribution_category $base_amount))

;; =============================
;; TOKEN OPERATIONS
;; =============================

;; Initialize token balance
(= (init-token-balance $username)
   (let (($user_id (GetUserID $username)))
     (TokenBalance $user_id "NIMO" 0)))

;; Initialize NIMO token balance
(= (init-nimo-balance $username $amount)
   (let (($user_id (GetUserID $username)))
     (TokenBalance $user_id "NIMO" $amount)))

;; Initialize ADA token balance
(= (init-ada-balance $username $amount)
   (let (($user_id (GetUserID $username)))
     (TokenBalance $user_id "ADA" $amount)))

;; Get token balance
(= (get-token-balance $username)
   (let (($user_id (GetUserID $username))
         ($nimo_query (TokenBalance $user_id "NIMO" $nimo_amount))
         ($ada_query (TokenBalance $user_id "ADA" $ada_amount)))
     (Balance $username $nimo_amount $ada_amount)))

;; Transfer tokens between users
(= (transfer-tokens $from_username $to_username $token_type $amount $reason)
   (let* (($from_id (GetUserID $from_username))
          ($to_id (GetUserID $to_username))
          ($from_balance_query (TokenBalance $from_id $token_type $from_amount))
          ($to_balance_query (TokenBalance $to_id $token_type $to_amount))
          ($tx_id (GenerateTransactionID))
          ($timestamp (CurrentTimestamp)))
     (if (>= $from_amount $amount)
         (let (($new_from_amount (- $from_amount $amount))
               ($new_to_amount (+ $to_amount $amount)))
           (TokenBalance $from_id $token_type $new_from_amount)
           (TokenBalance $to_id $token_type $new_to_amount)
           (TokenTransaction $tx_id $token_type $from_id $to_id $amount $reason $timestamp)
           $tx_id)
         (Error "Insufficient balance"))))

;; Mint new tokens
(= (mint-tokens $to_username $token_type $amount $reason)
   (let* (($to_id (GetUserID $to_username))
          ($balance_query (TokenBalance $to_id $token_type $current_amount))
          ($new_amount (+ $current_amount $amount))
          ($mint_id (GenerateMintingID))
          ($timestamp (CurrentTimestamp)))
     (TokenBalance $to_id $token_type $new_amount)
     (TokenMinting $mint_id $token_type $to_id $amount $reason $timestamp)
     $mint_id))

;; Burn tokens
(= (burn-tokens $from_username $token_type $amount $reason)
   (let* (($from_id (GetUserID $from_username))
          ($balance_query (TokenBalance $from_id $token_type $current_amount))
          ($burn_id (GenerateBurningID))
          ($timestamp (CurrentTimestamp)))
     (if (>= $current_amount $amount)
         (let (($new_amount (- $current_amount $amount)))
           (TokenBalance $from_id $token_type $new_amount)
           (TokenBurning $burn_id $token_type $from_id $amount $reason $timestamp)
           $burn_id)
         (Error "Insufficient balance to burn"))))

;; Auto-award tokens for contributions (legacy)
(= (auto-award $username $contribution_title)
   (auto-award-nimo $username $contribution_title))

;; Auto-award NIMO tokens for contributions
(= (auto-award-nimo $username $contribution_title)
   (let* (($user_id (GetUserID $username))
          ($contribution_id (FindContributionID $user_id $contribution_title))
          ($categories (FindAll (ContributionCategory $contribution_id $category)))
          ($verification_count (CountVerifications $contribution_id))
          ($confidence (CalculateConfidence $contribution_id))
          ($base_amount (CalculateBaseAward $categories))
          ($multiplier (+ 1.0 (* 0.1 $verification_count)))
          ($final_amount (* $base_amount $multiplier $confidence))
          ($reason (ConcatString "Auto-award for " $contribution_title)))
     (if (> $verification_count 0)
         (mint-tokens $username "NIMO" $final_amount $reason)
         (Error "Cannot award tokens for unverified contribution"))))

;; Auto-award ADA tokens for contributions
(= (auto-award-ada $username $contribution_title)
   (let* (($user_id (GetUserID $username))
          ($contribution_id (FindContributionID $user_id $contribution_title))
          ($verification_count (CountVerifications $contribution_id))
          ($confidence (CalculateConfidence $contribution_id))
          ($nimo_query (auto-award-nimo $username $contribution_title))
          ($nimo_amount (GetMintAmount $nimo_query))
          ($ada_amount (CalculateADAReward $nimo_amount $confidence))
          ($reason (ConcatString "ADA reward for " $contribution_title)))
     (if (> $verification_count 0)
         (mint-tokens $username "ADA" $ada_amount $reason)
         (Error "Cannot award ADA for unverified contribution"))))

;; Calculate reward for contribution
(= (CalculateADAReward $nimo_amount $confidence)
   (let* (($base_ada (/ $nimo_amount 100))  ;; 1 ADA = 100 NIMO
          ($confidence_multiplier (max 0.5 (min 2.0 (+ $confidence 0.5))))
          ($final_ada (* $base_ada $confidence_multiplier)))
     $final_ada))

;; =============================
;; TOKEN QUERIES
;; =============================

;; Get all transactions for a user
(= (get-user-transactions $username)
   (let (($user_id (GetUserID $username)))
     (append (FindAll (TokenTransaction $id $token_type $user_id $to $amount $reason $timestamp))
             (FindAll (TokenTransaction $id $token_type $from $user_id $amount $reason $timestamp)))))

;; Get all minting records for a user
(= (get-user-mintings $username)
   (let (($user_id (GetUserID $username)))
     (FindAll (TokenMinting $id $token_type $user_id $amount $reason $timestamp))))

;; Get all burning records for a user
(= (get-user-burnings $username)
   (let (($user_id (GetUserID $username)))
     (FindAll (TokenBurning $id $token_type $user_id $amount $reason $timestamp))))

;; Get transaction by ID
(= (get-transaction $tx_id)
   (TokenTransaction $tx_id $token_type $from $to $amount $reason $timestamp))

;; Count verifications for a contribution
(= (CountVerifications $contribution_id)
   (Length (FindAll (ContributionVerification $contribution_id $verifier_id $timestamp $confidence))))

;; Calculate average verification confidence
(= (CalculateConfidence $contribution_id)
   (let (($verifications (FindAll (ContributionVerification $contribution_id $verifier_id $timestamp $confidence))))
     (if (> (Length $verifications) 0)
         (/ (SumConfidence $verifications) (Length $verifications))
         0.0)))

;; Sum confidence values
(= (SumConfidence $verifications)
   (FoldLeft $verifications 0.0 AddConfidence))

;; Add confidence helper
(= (AddConfidence $acc $verification)
   (let (($confidence (GetConfidence $verification)))
     (+ $acc $confidence)))

;; Get confidence from verification
(= (GetConfidence $verification)
   (let (($query (ContributionVerification $id $verifier_id $timestamp $confidence)))
     $confidence))

;; Calculate base award from categories
(= (CalculateBaseAward $categories)
   (if (= (Length $categories) 0)
       50.0  ;; Default amount
       (MaxAward (map $categories GetCategoryAward))))

;; Get award for category
(= (GetCategoryAward $category_atom)
   (let* (($category (GetCategory $category_atom))
          ($rule_query (TokenAwardRule $category $amount)))
     (if (IsNull $amount)
         50.0  ;; Default if no rule exists
         $amount)))

;; Get category from category atom
(= (GetCategory $category_atom)
   (let (($query (ContributionCategory $id $category)))
     $category))

;; Get minting amount from minting record
(= (GetMintAmount $mint_id)
   (let (($query (TokenMinting $mint_id $token_type $to $amount $reason $timestamp)))
     $amount))

;; =============================
;; UTILITY FUNCTIONS
;; =============================

;; Generate transaction ID
(= (GenerateTransactionID)
   (let (($random (RandomString 16)))
     (ConcatString "tx-" $random)))

;; Generate minting ID
(= (GenerateMintingID)
   (let (($random (RandomString 16)))
     (ConcatString "mint-" $random)))

;; Generate burning ID
(= (GenerateBurningID)
   (let (($random (RandomString 16)))
     (ConcatString "burn-" $random)))

;; List operations (implementation would be provided by MeTTa runtime)
(= (append $list1 $list2)
   (AppendLists $list1 $list2))

(= (Length $list)
   (ListLength $list))

(= (max $a $b)
   (if (> $a $b) $a $b))

(= (min $a $b)
   (if (< $a $b) $a $b))

(= (MaxAward $amounts)
   (FoldLeft $amounts 0.0 Max))

(= (FoldLeft $list $initial $function)
   (FoldLeftImplementation $list $initial $function))

;; Check if a value is null
(= (IsNull $value)
   (Equal $value null))

;; =============================
;; END OF TOKEN IMPLEMENTATION
;; =============================