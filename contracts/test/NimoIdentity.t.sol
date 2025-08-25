// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "../src/NimoIdentity.sol";
import "../src/NimoToken.sol";

contract NimoIdentityTest is Test {
    NimoIdentity public nimoIdentity;
    NimoToken public nimoToken;
    
    address public owner;
    address public user1;
    address public user2;
    address public verifier;
    address public mettaAgent;
    
    // Events from contracts
    event IdentityCreated(uint256 indexed tokenId, string username, address owner);
    event ContributionAdded(uint256 indexed contributionId, uint256 indexed identityId, string contributionType);
    event ContributionVerified(uint256 indexed contributionId, address verifier, uint256 tokensAwarded);
    event TokensAwarded(uint256 indexed identityId, uint256 amount, string reason);
    
    function setUp() public {
        owner = address(this);
        user1 = address(0x1);
        user2 = address(0x2);
        verifier = address(0x3);
        mettaAgent = address(0x4);
        
        // Deploy contracts
        nimoToken = new NimoToken("NimoToken", "NIMO", 1000000 * 10**18);
        nimoIdentity = new NimoIdentity();
        
        // Setup roles
        bytes32 VERIFIER_ROLE = nimoIdentity.VERIFIER_ROLE();
        bytes32 METTA_AGENT_ROLE = nimoIdentity.METTA_AGENT_ROLE();
        bytes32 MINTER_ROLE = nimoToken.MINTER_ROLE();
        
        nimoIdentity.grantRole(VERIFIER_ROLE, verifier);
        nimoIdentity.grantRole(METTA_AGENT_ROLE, mettaAgent);
        nimoToken.grantRole(MINTER_ROLE, address(nimoIdentity));
        
        // Give users some ETH for gas
        vm.deal(user1, 10 ether);
        vm.deal(user2, 10 ether);
        vm.deal(verifier, 10 ether);
        vm.deal(mettaAgent, 10 ether);
    }
    
    function testIdentityCreation() public {
        vm.startPrank(user1);
        
        vm.expectEmit(true, true, true, true);
        emit IdentityCreated(1, "testuser", user1);
        
        nimoIdentity.createIdentity("testuser", "ipfs://test-metadata");
        
        // Check identity was created
        NimoIdentity.Identity memory identity = nimoIdentity.getIdentity(1);
        assertEq(identity.username, "testuser");
        assertEq(identity.metadataURI, "ipfs://test-metadata");
        assertTrue(identity.isActive);
        assertEq(identity.reputationScore, 0);
        assertEq(identity.tokenBalance, 0);
        
        // Check NFT ownership
        assertEq(nimoIdentity.ownerOf(1), user1);
        assertEq(nimoIdentity.balanceOf(user1), 1);
        
        vm.stopPrank();
    }
    
    function testIdentityCreationFailsForDuplicateUsername() public {
        vm.prank(user1);
        nimoIdentity.createIdentity("testuser", "ipfs://test1");
        
        vm.prank(user2);
        vm.expectRevert("Username already exists");
        nimoIdentity.createIdentity("testuser", "ipfs://test2");
    }
    
    function testIdentityCreationFailsForAddressWithExistingIdentity() public {
        vm.startPrank(user1);
        nimoIdentity.createIdentity("testuser1", "ipfs://test1");
        
        vm.expectRevert("Address already has identity");
        nimoIdentity.createIdentity("testuser2", "ipfs://test2");
        vm.stopPrank();
    }
    
    function testContributionSubmission() public {
        // Create identity first
        vm.prank(user1);
        nimoIdentity.createIdentity("contributor", "ipfs://profile");
        
        vm.prank(user1);
        vm.expectEmit(true, true, true, true);
        emit ContributionAdded(1, 1, "hackathon");
        
        nimoIdentity.addContribution(
            "hackathon",
            "Built amazing DApp",
            "ipfs://evidence",
            "metta-hash-123"
        );
        
        // Check contribution was added
        NimoIdentity.Contribution memory contribution = nimoIdentity.getContribution(1);
        assertEq(contribution.identityId, 1);
        assertEq(contribution.contributionType, "hackathon");
        assertEq(contribution.description, "Built amazing DApp");
        assertEq(contribution.evidenceURI, "ipfs://evidence");
        assertEq(contribution.mettaHash, "metta-hash-123");
        assertFalse(contribution.verified);
        assertEq(contribution.tokensAwarded, 0);
    }
    
    function testContributionVerification() public {
        // Setup: create identity and add contribution
        vm.prank(user1);
        nimoIdentity.createIdentity("contributor", "ipfs://profile");
        
        vm.prank(user1);
        nimoIdentity.addContribution(
            "hackathon",
            "Built amazing DApp",
            "ipfs://evidence",
            "metta-hash-123"
        );
        
        // Verify contribution
        vm.prank(verifier);
        vm.expectEmit(true, true, true, true);
        emit ContributionVerified(1, verifier, 100);
        
        nimoIdentity.verifyContribution(1, 100);
        
        // Check contribution was verified
        NimoIdentity.Contribution memory contribution = nimoIdentity.getContribution(1);
        assertTrue(contribution.verified);
        assertEq(contribution.verifier, verifier);
        assertEq(contribution.tokensAwarded, 100);
        
        // Check identity was updated
        NimoIdentity.Identity memory identity = nimoIdentity.getIdentity(1);
        assertEq(identity.tokenBalance, 100);
        assertEq(identity.reputationScore, 10); // 10% of tokens as reputation
    }
    
    function testMeTTaRuleExecution() public {
        // Setup: create identity
        vm.prank(user1);
        nimoIdentity.createIdentity("metta-user", "ipfs://profile");
        
        // Execute MeTTa rule
        vm.prank(mettaAgent);
        vm.expectEmit(true, true, true, true);
        emit TokensAwarded(1, 50, "MeTTa agent award");
        
        nimoIdentity.executeMeTTaRule(
            "(auto-award user contribution)",
            1,
            50
        );
        
        // Check identity was updated
        NimoIdentity.Identity memory identity = nimoIdentity.getIdentity(1);
        assertEq(identity.tokenBalance, 50);
        assertEq(identity.reputationScore, 5); // 10% of tokens as reputation
    }
    
    function testImpactBondCreation() public {
        // Setup: create identity
        vm.prank(user1);
        nimoIdentity.createIdentity("bond-creator", "ipfs://profile");
        
        string[] memory milestones = new string[](3);
        milestones[0] = "Milestone 1";
        milestones[1] = "Milestone 2";
        milestones[2] = "Milestone 3";
        
        uint256 maturityDate = block.timestamp + 365 days;
        
        vm.prank(user1);
        nimoIdentity.createImpactBond(
            "Climate Action Project",
            "Reforestation initiative",
            10 ether,
            maturityDate,
            milestones
        );
        
        // Check bond was created (basic verification)
        // Note: More detailed testing would require getter functions for impact bonds
    }
    
    function testImpactBondInvestment() public {
        // Setup: create identity and bond
        vm.prank(user1);
        nimoIdentity.createIdentity("bond-creator", "ipfs://profile");
        
        string[] memory milestones = new string[](1);
        milestones[0] = "Project completion";
        
        uint256 maturityDate = block.timestamp + 365 days;
        
        vm.prank(user1);
        nimoIdentity.createImpactBond(
            "Test Bond",
            "Test Description",
            5 ether,
            maturityDate,
            milestones
        );
        
        // Invest in bond
        vm.prank(user2);
        nimoIdentity.investInBond{value: 1 ether}(1);
        
        // Check investment was recorded
        uint256 investment = nimoIdentity.getBondInvestment(1, user2);
        assertEq(investment, 1 ether);
    }
    
    function testOnlyVerifierCanVerifyContributions() public {
        vm.prank(user1);
        nimoIdentity.createIdentity("contributor", "ipfs://profile");
        
        vm.prank(user1);
        nimoIdentity.addContribution("test", "description", "evidence", "hash");
        
        // Try to verify as non-verifier (should fail)
        vm.prank(user2);
        vm.expectRevert();
        nimoIdentity.verifyContribution(1, 50);
    }
    
    function testOnlyMeTTaAgentCanExecuteRules() public {
        vm.prank(user1);
        nimoIdentity.createIdentity("user", "ipfs://profile");
        
        // Try to execute MeTTa rule as non-agent (should fail)
        vm.prank(user2);
        vm.expectRevert();
        nimoIdentity.executeMeTTaRule("rule", 1, 50);
    }
    
    function testGetIdentityByUsername() public {
        vm.prank(user1);
        nimoIdentity.createIdentity("testuser", "ipfs://test");
        
        NimoIdentity.Identity memory identity = nimoIdentity.getIdentityByUsername("testuser");
        assertEq(identity.username, "testuser");
        assertEq(identity.metadataURI, "ipfs://test");
        assertTrue(identity.isActive);
    }
    
    function testContributionRequiresActiveIdentity() public {
        vm.prank(user1);
        vm.expectRevert("No identity found for address");
        nimoIdentity.addContribution("test", "description", "evidence", "hash");
    }
    
    function testSupportsInterface() public view {
        // Test ERC721 interface
        assertTrue(nimoIdentity.supportsInterface(0x80ac58cd));
        // Test AccessControl interface
        assertTrue(nimoIdentity.supportsInterface(0x7965db0b));
    }
}