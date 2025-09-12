;; Nimo MeTTa Test Suite
;; This file contains tests for the MeTTa implementation of the Nimo platform

;; Import all modules
;; (import ./src/models/identity)
;; (import ./src/models/contribution)
;; (import ./src/models/token)
;; (import ./src/models/diaspora_bonds)
;; (import ./src/controllers/auto_award)
;; (import ./src/controllers/nimo_core)
;; (import ./src/controllers/cardano_operations)
;; (import ./utils/utils)

;; =============================
;; TEST HELPER FUNCTIONS
;; =============================

;; Assert equality
(= (AssertEqual $actual $expected $test_name)
   (if (Equal $actual $expected)
       (TestPassed $test_name)
       (TestFailed $test_name (ConcatString "Expected: " $expected " but got: " $actual))))

;; Assert not equal
(= (AssertNotEqual $actual $expected $test_name)
   (if (not (Equal $actual $expected))
       (TestPassed $test_name)
       (TestFailed $test_name (ConcatString $actual " should not equal " $expected))))

;; Assert true
(= (AssertTrue $condition $test_name)
   (if $condition
       (TestPassed $test_name)
       (TestFailed $test_name "Expected true, got false")))

;; Assert false
(= (AssertFalse $condition $test_name)
   (if (not $condition)
       (TestPassed $test_name)
       (TestFailed $test_name "Expected false, got true")))

;; Assert greater than
(= (AssertGreaterThan $actual $expected $test_name)
   (if (> $actual $expected)
       (TestPassed $test_name)
       (TestFailed $test_name (ConcatString "Expected > " $expected " but got: " $actual))))

;; Assert less than
(= (AssertLessThan $actual $expected $test_name)
   (if (< $actual $expected)
       (TestPassed $test_name)
       (TestFailed $test_name (ConcatString "Expected < " $expected " but got: " $actual))))

;; Test passed
(= (TestPassed $test_name)
   (let (($result (ConcatString "✅ PASS: " $test_name)))
     (LogInfo "test" $result)
     $result))

;; Test failed
(= (TestFailed $test_name $message)
   (let (($result (ConcatString "❌ FAIL: " $test_name " - " $message)))
     (LogError "test" $result)
     $result))

;; Run a test suite
(= (RunTestSuite $suite_name $tests)
   (let* (($test_count (Length $tests))
          ($start_time (CurrentTimestamp))
          ($results (map $tests RunTest))
          ($end_time (CurrentTimestamp))
          ($duration (- $end_time $start_time))
          ($passed (Length (filter $results IsTestPassed)))
          ($failed (- $test_count $passed)))
     (LogInfo "test_suite" (ConcatString "Test Suite: " $suite_name))
     (LogInfo "test_suite" (ConcatString "Tests: " $test_count ", Passed: " $passed ", Failed: " $failed))
     (LogInfo "test_suite" (ConcatString "Duration: " $duration "s"))
     (TestSuiteResult $suite_name $passed $failed $duration)))

;; Run a single test
(= (RunTest $test)
   ($test))

;; Check if a test passed
(= (IsTestPassed $result)
   (StartsWith $result "✅"))

;; =============================
;; IDENTITY MODULE TESTS
;; =============================

;; Test user creation
(= (test_user_creation)
   (let* (($username "TestUser")
          ($user_id (define-user $username))
          ($user_query (Identity $user_id $found_username $created_at))
          ($status_query (IdentityStatus $user_id $status)))
     (AssertEqual $found_username $username "User creation should store correct username")
     (AssertEqual $status "unverified" "New user should have unverified status")))

;; Test adding skills
(= (test_add_skills)
   (let* (($username "SkillUser")
          ($user_id (define-user $username)))
     (add-skill $username "Python")
     (add-skill $username "JavaScript" "advanced")
     (let* (($skill1_query (IdentitySkill $user_id "Python" $level1))
            ($skill2_query (IdentitySkill $user_id "JavaScript" $level2)))
       (AssertEqual $level1 "beginner" "Default skill level should be beginner")
       (AssertEqual $level2 "advanced" "Custom skill level should be stored correctly"))))

;; Test adding blockchain wallet
(= (test_add_wallet)
   (let* (($username "WalletUser")
          ($user_id (define-user $username))
          ($cardano_address "addr_test1qpz8yj8x2w3kq3...")
          ($eth_address "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"))
     (let (($result1 (add-cardano-address $username $cardano_address))
           ($result2 (add-ethereum-address $username $eth_address))
           ($wallet1_query (IdentityWallet $user_id "cardano" $found_cardano))
           ($wallet2_query (IdentityWallet $user_id "ethereum" $found_eth)))
       (AssertTrue $result1 "Should accept valid Cardano address")
       (AssertTrue $result2 "Should accept valid Ethereum address")
       (AssertEqual $found_cardano $cardano_address "Should store Cardano address correctly")
       (AssertEqual $found_eth $eth_address "Should store Ethereum address correctly"))))

;; Test user verification
(= (test_user_verification)
   (let* (($username "VerifyUser")
          ($verifier "VerifierUser")
          ($user_id (define-user $username))
          ($verifier_id (define-user $verifier)))
     (verify-identity $username $verifier_id)
     (let (($status_query (IdentityStatus $user_id $status)))
       (AssertEqual $status "verified" "User should have verified status after verification"))))

;; =============================
;; CONTRIBUTION MODULE TESTS
;; =============================

;; Test contribution creation
(= (test_contribution_creation)
   (let* (($username "ContribUser")
          ($user_id (define-user $username))
          ($title "Test Contribution")
          ($contrib_id (add-contribution $username $title))
          ($contrib_query (Contribution $contrib_id $found_user_id $found_title $timestamp))
          ($status_query (ContributionStatus $contrib_id $status)))
     (AssertEqual $found_user_id $user_id "Contribution should be linked to correct user")
     (AssertEqual $found_title $title "Contribution should have correct title")
     (AssertEqual $status "unverified" "New contribution should have unverified status")))

;; Test contribution with metadata
(= (test_contribution_metadata)
   (let* (($username "MetaUser")
          (define-user $username)
          ($title "Metadata Test")
          ($description "This is a test description")
          ($contrib_id (add-contribution-with-metadata $username $title $description))
          ($metadata_query (ContributionMetadata $contrib_id "description" $found_desc)))
     (AssertEqual $found_desc $description "Contribution should store metadata correctly")))

;; Test contribution verification
(= (test_contribution_verification)
   (let* (($username "VerifContribUser")
          ($verifier "ContribVerifier")
          (define-user $username)
          (define-user $verifier)
          ($title "Verify Contrib Test")
          ($contrib_id (add-contribution $username $title)))
     (verify-specific-contribution $contrib_id $verifier)
     (let (($status_query (ContributionStatus $contrib_id $status)))
       (AssertEqual $status "verified" "Contribution should have verified status after verification"))))

;; Test MeTTa proof generation
(= (test_metta_proof)
   (let* (($username "ProofUser")
          (define-user $username)
          ($title "Proof Test")
          ($contrib_id (add-contribution $username $title))
          ($proof_hash (generate-metta-proof $username $title))
          ($proof_query (ContributionProof $contrib_id $found_hash $timestamp)))
     (AssertEqual $found_hash $proof_hash "Should generate and store correct proof hash")
     (AssertTrue (not (IsNull $found_hash)) "Proof hash should not be null"))))

;; =============================
;; TOKEN MODULE TESTS
;; =============================

;; Test token balance initialization
(= (test_token_balance)
   (let* (($username "TokenUser")
          ($user_id (define-user $username))
          ($nimo_amount 100)
          ($ada_amount 5.0))
     (init-nimo-balance $username $nimo_amount)
     (init-ada-balance $username $ada_amount)
     (let* (($nimo_query (TokenBalance $user_id "NIMO" $found_nimo))
            ($ada_query (TokenBalance $user_id "ADA" $found_ada)))
       (AssertEqual $found_nimo $nimo_amount "NIMO balance should be initialized correctly")
       (AssertEqual $found_ada $ada_amount "ADA balance should be initialized correctly"))))

;; Test token transfer
(= (test_token_transfer)
   (let* (($from_user "FromUser")
          ($to_user "ToUser")
          ($from_id (define-user $from_user))
          ($to_id (define-user $to_user))
          ($initial_amount 100)
          ($transfer_amount 30))
     (init-nimo-balance $from_user $initial_amount)
     (init-nimo-balance $to_user 0)
     (transfer-tokens $from_user $to_user "NIMO" $transfer_amount "Test transfer")
     (let* (($from_query (TokenBalance $from_id "NIMO" $from_balance))
            ($to_query (TokenBalance $to_id "NIMO" $to_balance)))
       (AssertEqual $from_balance (- $initial_amount $transfer_amount) "Sender balance should decrease")
       (AssertEqual $to_balance $transfer_amount "Receiver balance should increase"))))

;; Test token minting
(= (test_token_minting)
   (let* (($username "MintUser")
          ($user_id (define-user $username))
          ($initial_amount 50)
          ($mint_amount 25))
     (init-nimo-balance $username $initial_amount)
     (mint-tokens $username "NIMO" $mint_amount "Test minting")
     (let (($balance_query (TokenBalance $user_id "NIMO" $balance)))
       (AssertEqual $balance (+ $initial_amount $mint_amount) "Balance should increase after minting"))))

;; Test automatic token awards
(= (test_auto_award)
   (let* (($username "AwardUser")
          ($verifier "AwardVerifier")
          ($user_id (define-user $username))
          (define-user $verifier)
          ($title "Award Test")
          ($contrib_id (add-contribution $username $title)))
     (init-nimo-balance $username 0)
     (init-ada-balance $username 0)
     (verify-specific-contribution $contrib_id $verifier)
     (auto-award-nimo $username $title)
     (let (($balance_query (TokenBalance $user_id "NIMO" $balance)))
       (AssertGreaterThan $balance 0 "NIMO balance should increase after auto-award"))))

;; =============================
;; BOND MODULE TESTS
;; =============================

;; Test impact bond creation
(= (test_bond_creation)
   (let* (($creator "BondCreator")
          ($creator_id (define-user $creator))
          ($bond_id "test-bond-001")
          ($title "Test Bond")
          ($target_amount 10000)
          ($created_bond_id (create-impact-bond $bond_id $creator $title $target_amount))
          ($bond_query (ImpactBond $created_bond_id $found_creator_id $found_title $found_target $created_at))
          ($status_query (BondStatus $created_bond_id $status)))
     (AssertEqual $created_bond_id $bond_id "Should return correct bond ID")
     (AssertEqual $found_creator_id $creator_id "Bond should be linked to creator")
     (AssertEqual $found_title $title "Bond should have correct title")
     (AssertEqual $found_target $target_amount "Bond should have correct target amount")
     (AssertEqual $status "active" "New bond should have active status")))

;; Test bond investment
(= (test_bond_investment)
   (let* (($creator "InvestCreator")
          ($investor "InvestorUser")
          (define-user $creator)
          (define-user $investor)
          ($bond_id "test-bond-002")
          ($title "Investment Test Bond")
          ($target_amount 10000)
          ($investment_amount 2000)
          (create-impact-bond $bond_id $creator $title $target_amount)
          ($nft_id (purchase-impact-bond $bond_id $investor $investment_amount))
          ($metadata_query (BondMetadata $bond_id "funded_amount" $funded_amount))
          ($investment_query (BondInvestment $bond_id $investor_id $found_amount $timestamp))
          ($nft_query (BondNFT $bond_id $found_nft_id $metadata)))
     (AssertEqual $funded_amount $investment_amount "Funded amount should be updated")
     (AssertEqual $found_amount $investment_amount "Investment amount should be recorded correctly")
     (AssertEqual $found_nft_id $nft_id "NFT ID should match returned ID"))))

;; Test bond milestones
(= (test_bond_milestones)
   (let* (($creator "MilestoneCreator")
          ($verifier "MilestoneVerifier")
          (define-user $creator)
          (define-user $verifier)
          ($bond_id "test-bond-003")
          ($title "Milestone Test Bond")
          ($target_amount 10000)
          ($description "Test milestone")
          ($evidence "evidence-link")
          (create-impact-bond $bond_id $creator $title $target_amount)
          ($milestone_id (record-bond-milestone $bond_id $description $evidence))
          ($verified_id (verify-bond-milestone $bond_id $description $verifier))
          ($milestone_query (BondMilestone $bond_id $found_milestone_id $found_desc $found_evidence $timestamp))
          ($verification_query (MilestoneVerification $verified_id $verifier_id $ver_timestamp)))
     (AssertEqual $found_milestone_id $milestone_id "Milestone ID should match returned ID")
     (AssertEqual $found_desc $description "Milestone should have correct description")
     (AssertEqual $found_evidence $evidence "Milestone should have correct evidence")
     (AssertEqual $verified_id $milestone_id "Verification should return milestone ID")))

;; =============================
;; AUTO AWARD MODULE TESTS
;; =============================

;; Test verification confidence calculation
(= (test_verification_confidence)
   (let* (($username "ConfidenceUser")
          ($user_id (define-user $username))
          ($title "Confidence Test")
          ($description "This is a detailed description for testing confidence calculation")
          ($contrib_id (add-contribution-with-metadata $username $title $description))
          (add-contribution-metadata $contrib_id "type" "technical")
          (add-contribution-metadata $contrib_id "evidence" "evidence-link-1")
          (add-contribution-metadata $contrib_id "evidence" "evidence-link-2")
          (IdentityReputation $user_id 50)
          ($confidence (CalculateVerificationConfidence $contrib_id)))
     (AssertGreaterThan $confidence 0.0 "Confidence should be greater than 0")
     (AssertLessThan $confidence 1.0 "Confidence should be less than 1")))

;; Test autonomous verification
(= (test_autonomous_verification)
   (let* (($username "AutoVerifyUser")
          ($user_id (define-user $username))
          ($title "Auto Verify Test")
          ($description "This is a detailed description with sufficient data for verification")
          ($contrib_id (add-contribution-with-metadata $username $title $description))
          (add-contribution-metadata $contrib_id "type" "technical")
          (add-contribution-metadata $contrib_id "evidence" "evidence-link-1")
          (add-contribution-metadata $contrib_id "evidence" "evidence-link-2")
          (add-contribution-metadata $contrib_id "evidence" "evidence-link-3")
          (IdentityReputation $user_id 80)
          (AgentConfig "verification_threshold" 0.5)
          ($contribution (Contribution $contrib_id $user_id $title $timestamp))
          (VerifyContributionAutonomously $contribution)
          ($status_query (ContributionStatus $contrib_id $status)))
     (AssertEqual $status "verified" "Contribution should be verified autonomously")))

;; =============================
;; CORE CONTROLLER MODULE TESTS
;; =============================

;; Test user registration
(= (test_user_registration)
   (let* (($username "RegisteredUser")
          ($location "TestLocation")
          ($user_id (register-user $username $location))
          ($identity_query (Identity $user_id $found_username $created_at))
          ($info_query (IdentityAttribute $user_id "location" $found_location))
          ($balance_query (TokenBalance $user_id "NIMO" $balance)))
     (AssertEqual $found_username $username "User should be registered with correct username")
     (AssertEqual $found_location $location "User should have correct location")
     (AssertEqual $balance 0 "User should have initialized NIMO balance")))

;; Test contribution processing
(= (test_contribution_processing)
   (let* (($username "ProcessUser")
          (define-user $username)
          ($title "Process Test")
          ($description "Description for processing test")
          ($category "technical")
          ($contrib_id (process-contribution $username $title $description $category))
          ($contrib_query (Contribution $contrib_id $user_id $found_title $timestamp))
          ($metadata_query (ContributionMetadata $contrib_id "description" $found_desc))
          ($category_query (ContributionCategory $contrib_id $found_category)))
     (AssertEqual $found_title $title "Contribution should have correct title")
     (AssertEqual $found_desc $description "Contribution should have correct description")
     (AssertEqual $found_category $category "Contribution should have correct category")))

;; Test system status reporting
(= (test_system_status)
   (let* (($status (get-system-status))
          ($status_query (SystemStatus $name $version $uptime $user_count $contribution_count 
                                      $verified_count $token_transactions $bond_count)))
     (AssertNotEqual $name "" "System name should not be empty")
     (AssertNotEqual $version "" "System version should not be empty")
     (AssertGreaterThan $uptime 0 "System uptime should be positive")
     (AssertGreaterThan $user_count 0 "User count should be positive after tests")))

;; =============================
;; CARDANO OPERATIONS MODULE TESTS
;; =============================

;; Test Cardano address validation
(= (test_cardano_address_validation)
   (let* (($valid_address "addr_test1qpz8yj8x2w3kq3...")
          ($invalid_address "invalid_address")
          ($mainnet_address "addr1qxck9q05rr7pzazdd8xmfsj8l42n8mw7p9kllrx9xsqh8pl7e4al2j00xwyk7msut53ux0wsmzgxvw4sjymgkdk63dxsay0npf")
          ($result1 (ValidCardanoAddress $valid_address))
          ($result2 (ValidCardanoAddress $invalid_address))
          ($result3 (ValidCardanoAddress $mainnet_address)))
     (AssertTrue $result1 "Preview testnet address should be valid")
     (AssertFalse $result2 "Invalid address should be rejected")
     (AssertTrue $result3 "Mainnet address should be valid")))

;; Test wallet creation
(= (test_wallet_creation)
   (let* (($username "CardanoUser")
          (define-user $username)
          ($network "preview")
          ($wallet_details (CreateWallet $username $network))
          ($wallet_query (WalletDetails $wallet_id $address))
          ($user_address_query (GetCardanoAddress $username)))
     (AssertTrue (not (IsNull $wallet_id)) "Wallet ID should not be null")
     (AssertTrue (not (IsNull $address)) "Address should not be null")
     (AssertEqual $user_address_query $address "User should have the wallet address associated")))

;; Test transaction creation
(= (test_transaction_creation)
   (let* (($from_address "addr_test1qpz8yj8x2w3kq3...")
          ($to_address "addr_test1qqz8yj8x2w3kq3...")
          ($amount 5.0)
          ($tx_id (CreateADATransaction $from_address $to_address $amount))
          ($tx_query (GetTransaction $tx_id))
          ($tx_details_query (TransactionDetails $found_tx_id $network $status $created_at $submitted_at $confirmed_at)))
     (AssertEqual $found_tx_id $tx_id "Transaction ID should match created ID")
     (AssertEqual $status "created" "Transaction status should be 'created'")
     (AssertTrue (not (IsNull $created_at)) "Transaction created timestamp should not be null")))

;; =============================
;; UTILITY MODULE TESTS
;; =============================

;; Test string operations
(= (test_string_operations)
   (let* (($string "Hello, World!")
          ($prefix "Hello")
          ($result1 (StartsWith $string $prefix))
          ($result2 (StringLength $string))
          ($result3 (ConcatString "Hello, " "World!"))
          ($result4 (HashString $string)))
     (AssertTrue $result1 "String should start with prefix")
     (AssertEqual $result2 13 "String length should be correct")
     (AssertEqual $result3 $string "String concatenation should work")
     (AssertTrue (not (IsNull $result4)) "String hash should not be null")))

;; Test list operations
(= (test_list_operations)
   (let* (($list1 (list 1 2 3))
          ($list2 (list 4 5 6))
          ($result1 (Length $list1))
          ($result2 (Contains $list1 2))
          ($result3 (Contains $list1 4))
          ($result4 (append $list1 $list2))
          ($result5 (map $list1 (lambda ($x) (* $x 2))))
          ($result6 (filter $list1 (lambda ($x) (> $x 1)))))
     (AssertEqual $result1 3 "List length should be correct")
     (AssertTrue $result2 "List should contain 2")
     (AssertFalse $result3 "List should not contain 4")
     (AssertEqual (Length $result4) 6 "Appended list should have combined length")
     (AssertEqual (First $result5) 2 "Map should double first element")
     (AssertEqual (Length $result6) 2 "Filter should return elements > 1")))

;; Test math operations
(= (test_math_operations)
   (let* (($result1 (max 5 10))
          ($result2 (min 5 10))
          ($result3 (clamp 15 5 10))
          ($result4 (clamp 2 5 10))
          ($result5 (percentage 25 100))
          ($result6 (percentage 0 100)))
     (AssertEqual $result1 10 "Max should return larger number")
     (AssertEqual $result2 5 "Min should return smaller number")
     (AssertEqual $result3 10 "Clamp should limit to max value")
     (AssertEqual $result4 5 "Clamp should limit to min value")
     (AssertEqual $result5 25 "Percentage should calculate correctly")
     (AssertEqual $result6 0 "Percentage with zero part should be zero")))

;; =============================
;; MAIN TEST RUNNER
;; =============================

;; Run all test suites
(= (run_all_tests)
   (let* (($identity_tests (RunTestSuite "Identity Module Tests" 
                                        (list test_user_creation 
                                              test_add_skills 
                                              test_add_wallet 
                                              test_user_verification)))
          
          ($contribution_tests (RunTestSuite "Contribution Module Tests" 
                                           (list test_contribution_creation 
                                                 test_contribution_metadata 
                                                 test_contribution_verification 
                                                 test_metta_proof)))
          
          ($token_tests (RunTestSuite "Token Module Tests" 
                                     (list test_token_balance 
                                           test_token_transfer 
                                           test_token_minting 
                                           test_auto_award)))
          
          ($bond_tests (RunTestSuite "Bond Module Tests" 
                                    (list test_bond_creation 
                                          test_bond_investment 
                                          test_bond_milestones)))
          
          ($auto_award_tests (RunTestSuite "Auto Award Module Tests" 
                                          (list test_verification_confidence 
                                                test_autonomous_verification)))
          
          ($core_tests (RunTestSuite "Core Controller Module Tests" 
                                    (list test_user_registration 
                                          test_contribution_processing 
                                          test_system_status)))
          
          ($cardano_tests (RunTestSuite "Cardano Operations Module Tests" 
                                       (list test_cardano_address_validation 
                                             test_wallet_creation 
                                             test_transaction_creation)))
          
          ($utility_tests (RunTestSuite "Utility Module Tests" 
                                       (list test_string_operations 
                                             test_list_operations 
                                             test_math_operations)))
          
          ($all_passed (and (= (TestSuiteResult "Identity Module Tests" $identity_passed $identity_failed $_) $identity_tests)
                           (= (TestSuiteResult "Contribution Module Tests" $contribution_passed $contribution_failed $_) $contribution_tests)
                           (= (TestSuiteResult "Token Module Tests" $token_passed $token_failed $_) $token_tests)
                           (= (TestSuiteResult "Bond Module Tests" $bond_passed $bond_failed $_) $bond_tests)
                           (= (TestSuiteResult "Auto Award Module Tests" $auto_award_passed $auto_award_failed $_) $auto_award_tests)
                           (= (TestSuiteResult "Core Controller Module Tests" $core_passed $core_failed $_) $core_tests)
                           (= (TestSuiteResult "Cardano Operations Module Tests" $cardano_passed $cardano_failed $_) $cardano_tests)
                           (= (TestSuiteResult "Utility Module Tests" $utility_passed $utility_failed $_) $utility_tests)
                           (= $identity_failed 0)
                           (= $contribution_failed 0)
                           (= $token_failed 0)
                           (= $bond_failed 0)
                           (= $auto_award_failed 0)
                           (= $core_failed 0)
                           (= $cardano_failed 0)
                           (= $utility_failed 0)))
          ($total_tests (+ $identity_passed $identity_failed
                          $contribution_passed $contribution_failed
                          $token_passed $token_failed
                          $bond_passed $bond_failed
                          $auto_award_passed $auto_award_failed
                          $core_passed $core_failed
                          $cardano_passed $cardano_failed
                          $utility_passed $utility_failed))
          ($total_passed (+ $identity_passed $contribution_passed $token_passed $bond_passed 
                           $auto_award_passed $core_passed $cardano_passed $utility_passed))
          ($total_failed (- $total_tests $total_passed)))
     
     (LogInfo "test_runner" "=============================")
     (LogInfo "test_runner" "TEST SUMMARY")
     (LogInfo "test_runner" "=============================")
     (LogInfo "test_runner" (ConcatString "Total Tests: " $total_tests))
     (LogInfo "test_runner" (ConcatString "Total Passed: " $total_passed))
     (LogInfo "test_runner" (ConcatString "Total Failed: " $total_failed))
     (LogInfo "test_runner" "=============================")
     
     (if $all_passed
         (LogInfo "test_runner" "ALL TESTS PASSED ✅")
         (LogError "test_runner" "SOME TESTS FAILED ❌"))
     
     $all_passed))

;; Execute all tests
(run_all_tests)