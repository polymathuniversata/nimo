;; Nimo Autonomous Award Controller
;; This file contains the MeTTa implementation for the autonomous award system
;; It handles automatic verification and token awards based on contribution data

;; =============================
;; AUTONOMOUS AGENT CONFIGURATION
;; =============================

;; Agent configuration parameters
(= (AgentConfig "verification_threshold" 0.75)
   (ConfigValue "verification_threshold" 0.75))
(= (AgentConfig "min_verifications" 2)
   (ConfigValue "min_verifications" 2))
(= (AgentConfig "max_auto_verify_per_day" 10)
   (ConfigValue "max_auto_verify_per_day" 10))
(= (AgentConfig "auto_verification_enabled" true)
   (ConfigValue "auto_verification_enabled" true))
(= (AgentConfig "auto_award_enabled" true)
   (ConfigValue "auto_award_enabled" true))

;; Agent activity log
(= (AgentActivityLog $action $target_id $result $timestamp)
   (ActivityLog $action $target_id $result $timestamp))

;; Agent verification criteria
(= (VerificationCriterion $criterion_id $name $weight)
   (Criterion $criterion_id $name $weight))

;; Initialize default verification criteria
(= (InitializeDefaultCriteria)
   (let ()
     (VerificationCriterion "community_engagement" "Community Engagement" 0.3)
     (VerificationCriterion "technical_contribution" "Technical Contribution" 0.3)
     (VerificationCriterion "social_impact" "Social Impact" 0.2)
     (VerificationCriterion "innovation" "Innovation" 0.1)
     (VerificationCriterion "sustainability" "Sustainability" 0.1)))

;; =============================
;; VERIFICATION ENGINE
;; =============================

;; Main entry point for autonomous verification process
(= (run-auto-verification)
   (let* (($enabled (GetConfigValue "auto_verification_enabled"))
          ($max_count (GetConfigValue "max_auto_verify_per_day"))
          ($unverified_contributions (FindUnverifiedContributions))
          ($filtered_contributions (FilterVerifiableContributions $unverified_contributions))
          ($contributions_to_verify (TakeN $filtered_contributions $max_count)))
     (if $enabled
         (map $contributions_to_verify VerifyContributionAutonomously)
         (AgentActivityLog "auto_verification_skipped" "system" "Autonomous verification is disabled" (CurrentTimestamp)))))

;; Find all unverified contributions
(= (FindUnverifiedContributions)
   (FindAll (and (Contribution $id $user_id $title $timestamp)
                 (ContributionStatus $id "unverified"))))

;; Filter contributions that have enough data to be verified
(= (FilterVerifiableContributions $contributions)
   (filter $contributions HasSufficientData))

;; Check if a contribution has sufficient data for verification
(= (HasSufficientData $contribution)
   (let* (($id (GetContributionID $contribution))
          ($metadata_count (Length (CollectContributionMetadata $id))))
     (>= $metadata_count 2)))

;; Verify a contribution autonomously
(= (VerifyContributionAutonomously $contribution)
   (let* (($id (GetContributionID $contribution))
          ($user_id (GetContributionUserId $contribution))
          ($confidence (CalculateVerificationConfidence $id))
          ($threshold (GetConfigValue "verification_threshold"))
          ($timestamp (CurrentTimestamp)))
     (if (>= $confidence $threshold)
         (let ()
           (ContributionVerification $id "autonomous_system" $timestamp $confidence)
           (ContributionStatus $id "verified")
           (AgentActivityLog "auto_verification" $id "Verified with confidence" $timestamp)
           (CheckForAutoAward $id $user_id $confidence))
         (AgentActivityLog "auto_verification_failed" $id "Insufficient confidence" $timestamp))))

;; Calculate verification confidence for a contribution
(= (CalculateVerificationConfidence $contribution_id)
   (let* (($metadata (CollectContributionMetadata $contribution_id))
          ($contribution_type (GetMetadataValue $metadata "type"))
          ($evidence_count (CountEvidenceItems $metadata))
          ($description_quality (AnalyzeDescriptionQuality $metadata))
          ($reputation_factor (GetContributorReputationFactor $contribution_id))
          ($criteria_score (EvaluateCriteriaScore $contribution_id $metadata))
          ;; Weight different factors
          ($confidence (+ (* 0.3 $description_quality)
                         (* 0.2 (min 1.0 (/ $evidence_count 3)))
                         (* 0.2 $reputation_factor)
                         (* 0.3 $criteria_score))))
     (max 0.0 (min 1.0 $confidence))))

;; Count evidence items in metadata
(= (CountEvidenceItems $metadata)
   (let (($evidence (GetMetadataValue $metadata "evidence")))
     (if (IsNull $evidence)
         0
         (if (IsList $evidence)
             (Length $evidence)
             1))))

;; Analyze description quality (0.0 - 1.0)
(= (AnalyzeDescriptionQuality $metadata)
   (let* (($description (GetMetadataValue $metadata "description"))
          ($words (if (IsNull $description)
                     0
                     (CountWords $description))))
     (min 1.0 (/ $words 20))))  ;; 20+ words gives full score

;; Get contributor's reputation as a factor (0.5 - 1.0)
(= (GetContributorReputationFactor $contribution_id)
   (let* (($user_id (GetContributionUserIdFromId $contribution_id))
          ($reputation_query (IdentityReputation $user_id $score))
          ($normalized (/ (max 0 $score) 100)))
     (+ 0.5 (* 0.5 (min 1.0 $normalized)))))  ;; Scale from 0.5 to 1.0

;; Evaluate contribution against verification criteria
(= (EvaluateCriteriaScore $contribution_id $metadata)
   (let* (($criteria (FindAll (VerificationCriterion $criterion_id $name $weight)))
          ($scores (map $criteria (lambda ($criterion)
                                    (EvaluateCriterion $criterion $contribution_id $metadata))))
          ($weighted_sum (SumWeightedScores $criteria $scores))
          ($weight_sum (SumWeights $criteria)))
     (/ $weighted_sum $weight_sum)))

;; Evaluate contribution against single criterion
(= (EvaluateCriterion $criterion $contribution_id $metadata)
   (let* (($criterion_id (GetCriterionID $criterion))
          ($contribution_type (GetMetadataValue $metadata "type"))
          ($category_scores (GetCategoryCriterionScores $contribution_type)))
     (GetCategoryScore $category_scores $criterion_id)))

;; Sum weighted scores
(= (SumWeightedScores $criteria $scores)
   (let (($zipped (zip $criteria $scores)))
     (FoldLeft $zipped 0.0 (lambda ($acc $pair)
                            (let (($criterion (First $pair))
                                  ($score (Second $pair))
                                  ($weight (GetCriterionWeight $criterion)))
                              (+ $acc (* $weight $score)))))))

;; Sum weights
(= (SumWeights $criteria)
   (FoldLeft $criteria 0.0 (lambda ($acc $criterion)
                             (+ $acc (GetCriterionWeight $criterion)))))

;; =============================
;; AUTO AWARD ENGINE
;; =============================

;; Check if a contribution should receive an auto award
(= (CheckForAutoAward $contribution_id $user_id $confidence)
   (let* (($enabled (GetConfigValue "auto_award_enabled"))
          ($contribution_query (Contribution $contribution_id $user_id $title $timestamp))
          ($username (GetUsernameFromId $user_id))
          ($timestamp (CurrentTimestamp)))
     (if $enabled
         (let (($result (auto-award-nimo $username $title)))
           (AgentActivityLog "auto_award" $contribution_id "NIMO tokens awarded" $timestamp)
           (let (($ada_result (auto-award-ada $username $title)))
             (AgentActivityLog "auto_award" $contribution_id "ADA tokens awarded" $timestamp)
             $ada_result))
         (AgentActivityLog "auto_award_skipped" $contribution_id "Auto awards are disabled" $timestamp))))

;; Get predefined category-criterion scores (would be expanded in a real system)
(= (GetCategoryCriterionScores $category)
   (match $category
     ("technical" (CreateScoreMap
                    (list "community_engagement" "technical_contribution" "social_impact" "innovation" "sustainability")
                    (list 0.6 0.9 0.4 0.8 0.5)))
     ("community" (CreateScoreMap
                    (list "community_engagement" "technical_contribution" "social_impact" "innovation" "sustainability")
                    (list 0.9 0.3 0.8 0.4 0.6)))
     ("environmental" (CreateScoreMap
                    (list "community_engagement" "technical_contribution" "social_impact" "innovation" "sustainability")
                    (list 0.7 0.5 0.8 0.6 0.9)))
     (otherwise (CreateScoreMap
                    (list "community_engagement" "technical_contribution" "social_impact" "innovation" "sustainability")
                    (list 0.6 0.6 0.6 0.6 0.6)))))

;; =============================
;; MONITORING AND STATISTICS
;; =============================

;; Get agent daily statistics
(= (get-agent-daily-stats)
   (let* (($today_start (TodayStartTimestamp))
          ($today_logs (FindAll (and (AgentActivityLog $action $target_id $result $timestamp)
                                    (>= $timestamp $today_start))))
          ($verification_count (CountLogsOfType $today_logs "auto_verification"))
          ($award_count (CountLogsOfType $today_logs "auto_award"))
          ($failed_count (CountLogsOfType $today_logs "auto_verification_failed")))
     (AgentStats $verification_count $award_count $failed_count)))

;; Count logs of a specific type
(= (CountLogsOfType $logs $type)
   (Length (filter $logs (lambda ($log) (LogTypeMatches $log $type)))))

;; Check if log matches type
(= (LogTypeMatches $log $type)
   (let (($query (AgentActivityLog $action $target_id $result $timestamp)))
     (Equal $action $type)))

;; Get recent agent activity
(= (get-recent-agent-activity $limit)
   (let* (($all_logs (FindAll (AgentActivityLog $action $target_id $result $timestamp)))
          ($sorted_logs (SortByTimestamp $all_logs))
          ($recent_logs (TakeN $sorted_logs $limit)))
     $recent_logs))

;; =============================
;; UTILITY FUNCTIONS
;; =============================

;; Get config value
(= (GetConfigValue $key)
   (let (($query (AgentConfig $key $value)))
     $value))

;; Get metadata value from metadata list
(= (GetMetadataValue $metadata $key)
   (let (($matching (filter $metadata (lambda ($item) (MetadataKeyMatches $item $key)))))
     (if (= (Length $matching) 0)
         null
         (let (($query (ContributionMetadata $id $found_key $value)))
           $value))))

;; Check if metadata key matches
(= (MetadataKeyMatches $metadata_item $key)
   (let (($query (ContributionMetadata $id $item_key $value)))
     (Equal $item_key $key)))

;; Get username from user ID
(= (GetUsernameFromId $user_id)
   (let (($query (Identity $user_id $username $created_at)))
     $username))

;; Get contribution user ID
(= (GetContributionUserId $contribution)
   (let (($query (Contribution $id $user_id $title $timestamp)))
     $user_id))

;; Get contribution user ID from contribution ID
(= (GetContributionUserIdFromId $contribution_id)
   (let (($query (Contribution $contribution_id $user_id $title $timestamp)))
     $user_id))

;; Get criterion ID
(= (GetCriterionID $criterion)
   (let (($query (VerificationCriterion $criterion_id $name $weight)))
     $criterion_id))

;; Get criterion weight
(= (GetCriterionWeight $criterion)
   (let (($query (VerificationCriterion $criterion_id $name $weight)))
     $weight))

;; Create a score map from lists of keys and values
(= (CreateScoreMap $keys $values)
   (zip $keys $values))

;; Get category score from score map
(= (GetCategoryScore $score_map $criterion_id)
   (let (($matching (filter $score_map (lambda ($pair) (Equal (First $pair) $criterion_id)))))
     (if (= (Length $matching) 0)
         0.5  ;; Default score if not found
         (Second (First $matching)))))

;; Count words in a string
(= (CountWords $text)
   (Length (SplitString $text " ")))

;; Today's start timestamp
(= (TodayStartTimestamp)
   (GetTodayStartTime))

;; Sort logs by timestamp (descending)
(= (SortByTimestamp $logs)
   (SortByDescending $logs GetLogTimestamp))

;; Get log timestamp
(= (GetLogTimestamp $log)
   (let (($query (AgentActivityLog $action $target_id $result $timestamp)))
     $timestamp))

;; Take N items from list
(= (TakeN $list $n)
   (TakeNImplementation $list $n))

;; List utilities (would be provided by MeTTa runtime)
(= (zip $list1 $list2)
   (ZipLists $list1 $list2))

(= (First $pair)
   (GetFirst $pair))

(= (Second $pair)
   (GetSecond $pair))

(= (IsList $value)
   (IsMeTTaList $value))

(= (SplitString $text $delimiter)
   (StringSplit $text $delimiter))

(= (SortByDescending $list $key_function)
   (SortListByDescending $list $key_function))

;; =============================
;; END OF AUTO AWARD CONTROLLER
;; =============================