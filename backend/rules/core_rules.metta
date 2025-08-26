;; MeTTa Rules for Nimo Platform
;; This file contains core MeTTa rules for autonomous verification,
;; reputation scoring, and token award calculations.
;; Updated based on research findings in docs/metta_research_findings.md

;; =============================
;; IDENTITY & USER MANAGEMENT
;; =============================

;; Identity verification
(= (VerifyUser $user-id)
   (and (User $user-id $_)
        (or (HasVerifiedEmail $user-id)
            (HasVerifiedDID $user-id))))

;; DID verification rule
(= (HasVerifiedDID $user-id)
   (DIDVerification $user-id $_ $_))

;; Email verification rule
(= (HasVerifiedEmail $user-id)
   (EmailVerification $user-id $_ $_))

;; =============================
;; CONTRIBUTION VERIFICATION
;; =============================

;; Main verification rule - atom-based implementation
(= (VerifyContribution $contrib-id)
   (and (Contribution $contrib-id $user-id $_)
        (ValidEvidence $contrib-id)
        (SkillMatch $contrib-id $user-id)
        (ImpactAssessment $contrib-id "moderate")))

;; Evidence validation rules
(= (ValidEvidence $contrib-id)
   (let* (($evidence-count (CountEvidence $contrib-id))
          ($min-evidence 1))
     (>= $evidence-count $min-evidence)))

;; GitHub repository validation
(= (HasGithubEvidence $contrib-id)
   (Evidence $_ $contrib-id "github" $_))

;; Website with proof validation
(= (HasWebsiteEvidence $contrib-id)
   (Evidence $_ $contrib-id "website" $_))

;; Document with signature validation
(= (HasDocumentEvidence $contrib-id)
   (and (Evidence $_ $contrib-id "document" $_)
        (HasSignature $contrib-id $_)))

;; Skill matching - atom-based implementation
(= (SkillMatch $contrib-id $user-id)
   (let* (($category (GetContributionCategory $contrib-id))
          ($required-skills (RequiredSkillsForCategory $category)))
     (UserHasAnySkill $user-id $required-skills)))

;; Helper to check if user has any required skills
(= (UserHasAnySkill $user-id $skills)
   (or (Empty $skills)
       (or (HasSkill $user-id (First $skills) $_)
           (UserHasAnySkill $user-id (Rest $skills)))))

;; Get contribution category
(= (GetContributionCategory $contrib-id)
   (let* (($contribution (Contribution $contrib-id $_ $category)))
     $category))

;; Define required skills for categories
(= (RequiredSkillsForCategory "coding")
   (List "programming" "software development" "coding"))
   
(= (RequiredSkillsForCategory "education")
   (List "teaching" "curriculum" "tutoring"))
   
(= (RequiredSkillsForCategory "volunteer")
   (List "community service" "organizing"))
   
(= (RequiredSkillsForCategory $_)
   (List))

;; =============================
;; IMPACT ASSESSMENT
;; =============================

;; Impact assessment - atom-based implementation
(= (ImpactAssessment $contrib-id $min-level)
   (let* (($impact (GetImpactLevel $contrib-id))
          ($sufficient (ImpactLevelSufficient $impact $min-level)))
     $sufficient))

;; Get impact level from contribution
(= (GetImpactLevel $contrib-id)
   (let* (($impact (ContributionImpact $contrib-id $level)))
     (if $impact $level "minimal")))

;; Check if impact level is sufficient
(= (ImpactLevelSufficient $actual $minimum)
   (let* (($impact-levels (List "minimal" "moderate" "significant" "transformative"))
          ($actual-pos (PositionInList $actual $impact-levels))
          ($min-pos (PositionInList $minimum $impact-levels)))
     (>= $actual-pos $min-pos)))

;; Helper to find position in list
(= (PositionInList $item $list)
   (PositionInListHelper $item $list 0))

(= (PositionInListHelper $item $list $pos)
   (if (Empty $list)
       -1
       (if (== $item (First $list))
           $pos
           (PositionInListHelper $item (Rest $list) (+ $pos 1)))))

;; =============================
;; CONFIDENCE SCORING
;; =============================

;; Calculate confidence for verification decision
(= (CalculateConfidence $contrib-id)
   (let* (($evidence-score (EvidenceScore $contrib-id))
          ($reputation-score (ReputationScore $contrib-id))
          ($consistency-score (ConsistencyScore $contrib-id)))
     (/ (+ $evidence-score $reputation-score $consistency-score) 3.0)))

;; Evidence score calculation - atom-based
(= (EvidenceScore $contrib-id)
   (let* (($github-evidence (HasGithubEvidence $contrib-id))
          ($website-evidence (HasWebsiteEvidence $contrib-id))
          ($document-evidence (HasDocumentEvidence $contrib-id))
          ($evidence-count (CountEvidence $contrib-id)))
     (if $github-evidence
         0.9
         (if $document-evidence
             0.7
             (if $website-evidence
                 0.6
                 (if (> $evidence-count 0)
                     0.5
                     0.0))))))

;; Reputation score calculation
(= (ReputationScore $contrib-id)
   (let* (($user-id (GetContributorId $contrib-id))
          ($user-reputation (UserReputation $user-id $score)))
     (if $user-reputation
         (min 1.0 (/ $score 100.0))
         0.5)))

;; Consistency score calculation
(= (ConsistencyScore $contrib-id)
   (let* (($user-id (GetContributorId $contrib-id))
          ($past-contributions (CountUserContributions $user-id))
          ($verification-rate (UserVerificationRate $user-id $rate)))
     (if (< $past-contributions 3)
         0.5
         (if $verification-rate
             (min 1.0 $rate)
             0.5))))

;; =============================
;; VERIFICATION WITH CONFIDENCE
;; =============================

;; Full verification with confidence
(= (VerifyWithConfidence $contrib-id)
   (let* (($verified (VerifyContribution $contrib-id))
          ($confidence (CalculateConfidence $contrib-id))
          ($explanation (if $verified
                           (GeneratePositiveExplanation $contrib-id $confidence)
                           (GenerateNegativeExplanation $contrib-id $confidence))))
     (VerificationResult $contrib-id $verified $confidence $explanation)))

;; Get contributor ID from contribution
(= (GetContributorId $contrib-id)
   (let* (($contrib (Contribution $contrib-id $user-id $_)))
     $user-id))

;; Count user contributions
(= (CountUserContributions $user-id)
   (let* (($contributions (Contribution $_ $user-id $_)))
     (Length $contributions)))

;; Count evidence for a contribution
(= (CountEvidence $contrib-id)
   (let* (($evidence-list (Evidence $_ $contrib-id $_ $_)))
     (Length $evidence-list)))

;; =============================
;; EXPLANATION GENERATION
;; =============================

;; Generate explanation for positive verification
(= (GeneratePositiveExplanation $contrib-id $confidence)
   (let* (($primary-factor (GetPrimaryFactor $contrib-id))
          ($formatted-confidence (FormatPercentage $confidence)))
     (JoinStrings 
       "Contribution verified with " $formatted-confidence " confidence. "
       "Key factor: " $primary-factor)))

;; Generate explanation for negative verification
(= (GenerateNegativeExplanation $contrib-id $confidence)
   (let* (($reason (GetRejectionReason $contrib-id))
          ($formatted-confidence (FormatPercentage $confidence)))
     (JoinStrings 
       "Contribution could not be verified with sufficient confidence (" $formatted-confidence "). "
       "Reason: " $reason)))

;; Get primary factor for verification
(= (GetPrimaryFactor $contrib-id)
   (cond ((HasGithubEvidence $contrib-id) "Strong GitHub repository evidence")
         ((HasDocumentEvidence $contrib-id) "Document with signature")
         ((HasWebsiteEvidence $contrib-id) "Website evidence")
         (else "Provided evidence")))

;; Get rejection reason
(= (GetRejectionReason $contrib-id)
   (let* (($user-id (GetContributorId $contrib-id))
          ($evidence-count (CountEvidence $contrib-id))
          ($user-reputation-atom (UserReputation $user-id $reputation))
          ($user-reputation (if $user-reputation-atom $reputation 0))
          ($verification-rate-atom (UserVerificationRate $user-id $rate))
          ($verification-rate (if $verification-rate-atom $rate 0)))
     (cond ((== $evidence-count 0) "Insufficient evidence provided")
           ((< $user-reputation 30) "User reputation below threshold")
           ((< $verification-rate 0.3) "Low historical verification rate")
           (else "Multiple verification criteria not met"))))

;; Format percentage helper
(= (FormatPercentage $value)
   (let* (($percentage (* $value 100))
          ($rounded (Round $percentage)))
     (JoinStrings $rounded "%")))

;; String join helper
(= (JoinStrings $s1 $s2)
   (StringConcat $s1 $s2))
   
(= (JoinStrings $s1 $s2 $s3)
   (StringConcat $s1 (StringConcat $s2 $s3)))
   
(= (JoinStrings $s1 $s2 $s3 $s4)
   (StringConcat $s1 (StringConcat $s2 (StringConcat $s3 $s4))))
   
(= (JoinStrings $s1 $s2 $s3 $s4 $s5)
   (StringConcat $s1 (StringConcat $s2 (StringConcat $s3 (StringConcat $s4 $s5)))))

;; Round helper
(= (Round $num)
   (Floor (+ $num 0.5)))

;; =============================
;; FRAUD DETECTION
;; =============================

;; Detect fraud for contribution - atom-based
(= (DetectFraud $contrib-id)
   (let* (($user-id (GetContributorId $contrib-id)))
     (or (DuplicateSubmission $contrib-id $user-id)
         (SuspiciousActivityPattern $user-id)
         (EvidenceInconsistency $contrib-id))))

;; Detect duplicate submissions
(= (DuplicateSubmission $contrib-id $user-id)
   (let* (($evidence-urls (GetEvidenceUrls $contrib-id))
          ($other-contribs (OtherContributions $user-id $contrib-id))
          ($similar-found (CheckDuplicateEvidence $evidence-urls $other-contribs)))
     $similar-found))

;; Get evidence URLs for a contribution
(= (GetEvidenceUrls $contrib-id)
   (EvidenceUrlsHelper (Evidence $_ $contrib-id $_ $_)))

(= (EvidenceUrlsHelper $evidence-atoms)
   (if (Empty $evidence-atoms)
       (List)
       (let* (($first-evidence (First $evidence-atoms))
              ($url (GetEvidenceUrl $first-evidence))
              ($rest-urls (EvidenceUrlsHelper (Rest $evidence-atoms))))
         (Cons $url $rest-urls))))

(= (GetEvidenceUrl $evidence-atom)
   (nth 3 $evidence-atom))

;; Get other contributions by the same user
(= (OtherContributions $user-id $current-contrib-id)
   (filter (lambda ($c) (!= (nth 0 $c) $current-contrib-id))
           (Contribution $_ $user-id $_)))

;; Check for duplicate evidence across contributions
(= (CheckDuplicateEvidence $urls $other-contribs)
   (if (Empty $urls)
       #f
       (if (Empty $other-contribs)
           #f
           (or (ContributionHasUrl (First $other-contribs) (First $urls))
               (CheckDuplicateEvidence (Rest $urls) $other-contribs)
               (CheckDuplicateEvidence $urls (Rest $other-contribs))))))

;; Detect suspicious activity patterns based on timestamps
(= (SuspiciousActivityPattern $user-id)
   (let* (($submission-times (GetSubmissionTimes $user-id))
          ($rapid-submissions (HasRapidSubmissions $submission-times 3600))) ;; 1 hour
     $rapid-submissions))

;; Check evidence consistency
(= (EvidenceInconsistency $contrib-id)
   (let* (($evidence-list (Evidence $_ $contrib-id $_ $_))
          ($metadata (ContributionMetadata $contrib-id $_))
          ($dates-consistent (CheckDateConsistency $evidence-list $metadata))
          ($author-consistent (CheckAuthorConsistency $contrib-id)))
     (not (and $dates-consistent $author-consistent))))

;; =============================
;; TOKEN AWARD CALCULATION
;; =============================

;; Calculate token award based on contribution type
(= (CalculateTokenAward $contrib-id)
   (let* (($category (GetContributionCategory $contrib-id))
          ($base-amount (BaseTokenAmount $category))
          ($confidence (CalculateConfidence $contrib-id))
          ($quality-bonus (* $confidence 50))
          ($total-amount (+ $base-amount $quality-bonus)))
     $total-amount))

;; Base token amount by category
(= (BaseTokenAmount $category)
   (match $category
     ("coding" 75)
     ("education" 60)
     ("volunteer" 50)
     ("activism" 65)
     ("leadership" 70)
     ("entrepreneurship" 80)
     ("environmental" 70)
     ("community" 60)
     (_ 50)))

;; Award tokens with explanation
(= (AwardTokens $contrib-id)
   (let* (($verification (VerifyWithConfidence $contrib-id))
          ($verified (nth 1 $verification))
          ($user-id (GetContributorId $contrib-id)))
     (if $verified
         (let* (($amount (CalculateTokenAward $contrib-id))
                ($previous-balance (GetTokenBalance $user-id))
                ($new-balance (+ $previous-balance $amount)))
           (UpdateTokenBalance $user-id $new-balance)
           (AwardResult $contrib-id $user-id $amount "Success" $new-balance))
         (AwardResult $contrib-id $user-id 0 "Failed verification" 
                     (GetTokenBalance $user-id)))))

;; =============================
;; REPUTATION CALCULATION
;; =============================

;; Calculate user reputation - atom-based
(= (CalculateUserReputation $user-id)
   (let* (($verified-contribs (CountVerifiedContributions $user-id))
          ($skill-diversity (CountUniqueSkills $user-id))
          ($community-endorsements (CountEndorsements $user-id))
          ($impact-score (AverageImpactScore $user-id)))
     (+ (* $verified-contribs 10)
        (* $skill-diversity 5)
        (* $community-endorsements 3)
        (* $impact-score 7))))

;; Count verified contributions
(= (CountVerifiedContributions $user-id)
   (Length (VerifiedContributions $user-id)))

(= (VerifiedContributions $user-id)
   (filter (lambda ($c) (VerifyContribution (nth 0 $c)))
           (Contribution $_ $user-id $_)))

;; Count unique skills
(= (CountUniqueSkills $user-id)
   (Length (UniqueSkills $user-id)))

(= (UniqueSkills $user-id)
   (UniqueItems (map (lambda ($s) (nth 1 $s))
                     (HasSkill $user-id $_ $_))))

;; Helper for unique items in a list
(= (UniqueItems $list)
   (UniqueItemsHelper $list (List)))

(= (UniqueItemsHelper $list $seen)
   (if (Empty $list)
       $seen
       (let* (($item (First $list))
              ($rest (Rest $list)))
         (if (In $item $seen)
             (UniqueItemsHelper $rest $seen)
             (UniqueItemsHelper $rest (Cons $item $seen))))))

;; =============================
;; UTILITY FUNCTIONS
;; =============================

;; List helpers
(= (Empty $list)
   (== $list (List)))

(= (First $list)
   (car $list))

(= (Rest $list)
   (cdr $list))

(= (Length $list)
   (if (Empty $list)
       0
       (+ 1 (Length (Rest $list)))))

(= (In $item $list)
   (if (Empty $list)
       #f
       (or (== $item (First $list))
           (In $item (Rest $list)))))

;; List constructor shortcuts
(= (List) ())
(= (List $a) ($a))
(= (List $a $b) ($a $b))
(= (List $a $b $c) ($a $b $c))
(= (List $a $b $c $d) ($a $b $c $d))
(= (List $a $b $c $d $e) ($a $b $c $d $e))

;; Math helpers
(= (Floor $num)
   (int $num))

;; =============================
;; END OF RULES
;; =============================