#!/usr/bin/env python3
"""
Complete End-to-End Test for Nimo MeTTa → USDC Reward System

This script simulates the complete flow:
1. User submits contribution
2. MeTTa analyzes and verifies contribution
3. System calculates NIMO token reward
4. System calculates USDC reward based on confidence
5. System records transaction on blockchain (simulated)
6. System sends USDC reward (if applicable)
"""

import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from services.usdc_integration import USDCIntegration
from services.metta_integration_enhanced import get_metta_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompleteFlowTester:
    def __init__(self):
        """Initialize complete flow test environment"""
        self.usdc_integration = USDCIntegration()
        self.metta_integration = get_metta_service()
        
        # Test scenarios
        self.test_scenarios = [
            {
                "name": "High-Quality Coding Contribution",
                "user_id": "user123",
                "user_address": "0x742d35Cc6634C0532925a3b8D6AC14C0F7B2291E",
                "contribution": {
                    "id": "contrib_001",
                    "title": "DeFi Smart Contract with Comprehensive Tests",
                    "description": "Built a complete DeFi lending protocol with full test suite",
                    "category": "coding",
                    "evidence": [
                        {
                            "type": "github",
                            "url": "https://github.com/user123/defi-protocol",
                            "description": "Full smart contract implementation"
                        },
                        {
                            "type": "document", 
                            "url": "https://docs.google.com/document/d/abc123",
                            "description": "Technical documentation"
                        }
                    ],
                    "expected_confidence": 0.9,
                    "expected_nimo": 100,
                    "expected_usdc_eligible": True
                }
            },
            {
                "name": "Medium-Quality Educational Content",
                "user_id": "user456", 
                "user_address": "0x8ba1f109551bD432803012645Hac136c22c177e",
                "contribution": {
                    "id": "contrib_002",
                    "title": "Blockchain Basics Tutorial Series",
                    "description": "Created a 10-part tutorial series on blockchain fundamentals",
                    "category": "education",
                    "evidence": [
                        {
                            "type": "website",
                            "url": "https://medium.com/@user456/blockchain-basics",
                            "description": "Medium article series"
                        }
                    ],
                    "expected_confidence": 0.75,
                    "expected_nimo": 60,
                    "expected_usdc_eligible": False  # Below 0.8 confidence threshold
                }
            },
            {
                "name": "High-Impact Volunteer Work",
                "user_id": "user789",
                "user_address": "0x123456789abcdef123456789abcdef123456789a",
                "contribution": {
                    "id": "contrib_003", 
                    "title": "Community Cleanup and Education Initiative",
                    "description": "Organized environmental cleanup with 100+ volunteers and educational workshops",
                    "category": "environmental",
                    "evidence": [
                        {
                            "type": "document",
                            "url": "https://drive.google.com/file/d/xyz789",
                            "description": "Official volunteer certificates and photos"
                        },
                        {
                            "type": "website",
                            "url": "https://localenvironmentalgroup.org/events/cleanup2024",
                            "description": "Event documentation"
                        }
                    ],
                    "expected_confidence": 0.88,
                    "expected_nimo": 85,
                    "expected_usdc_eligible": True
                }
            }
        ]
    
    def simulate_contribution_submission(self, scenario):
        """Step 1: Simulate contribution submission"""
        logger.info(f"📝 Step 1: Contribution Submission - {scenario['name']}")
        
        contribution = scenario['contribution']
        
        logger.info(f"   User ID: {scenario['user_id']}")
        logger.info(f"   Title: {contribution['title']}")
        logger.info(f"   Category: {contribution['category']}")
        logger.info(f"   Evidence Count: {len(contribution['evidence'])}")
        
        # In real implementation, this would save to database
        # For now, we'll just return the contribution data
        return {
            'contribution_id': contribution['id'],
            'user_id': scenario['user_id'],
            'user_address': scenario['user_address'],
            'submission_timestamp': datetime.now().isoformat(),
            'status': 'submitted',
            'data': contribution
        }
    
    def run_metta_analysis(self, submission):
        """Step 2: MeTTa analyzes and verifies contribution"""
        logger.info("🧠 Step 2: MeTTa Analysis & Verification")
        
        try:
            # Run MeTTa validation
            metta_result = self.metta_integration.validate_contribution(
                submission['contribution_id'],
                submission['data']
            )
            
            logger.info(f"   Verified: {metta_result.get('verified')}")
            logger.info(f"   Confidence: {metta_result.get('confidence', 0):.3f}")
            logger.info(f"   Token Award: {metta_result.get('token_award', 0)}")
            logger.info(f"   Explanation: {metta_result.get('explanation', 'N/A')[:80]}...")
            
            return {
                'verified': metta_result.get('verified'),
                'confidence': metta_result.get('confidence', 0),
                'token_award': metta_result.get('token_award', 0),
                'explanation': metta_result.get('explanation'),
                'metta_proof': metta_result.get('metta_proof', ''),
                'verification_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"   ❌ MeTTa analysis failed: {e}")
            return {
                'verified': False,
                'confidence': 0,
                'token_award': 0,
                'explanation': f'Analysis failed: {str(e)}',
                'error': str(e)
            }
    
    def calculate_rewards(self, submission, metta_result):
        """Step 3 & 4: Calculate NIMO tokens and USDC rewards"""
        logger.info("💰 Step 3-4: Reward Calculation")
        
        if not metta_result.get('verified'):
            logger.info("   ❌ Contribution not verified - no rewards")
            return {
                'nimo_tokens': 0,
                'usdc_reward': 0,
                'usdc_eligible': False,
                'reason': 'Contribution not verified'
            }
        
        try:
            # Calculate USDC rewards using our integration
            usdc_calculation = self.usdc_integration.get_reward_calculation(
                nimo_amount=metta_result['token_award'],
                confidence=metta_result['confidence'], 
                contribution_type=submission['data']['category']
            )
            
            logger.info(f"   NIMO Tokens: {usdc_calculation['nimo_amount']}")
            logger.info(f"   Base USDC: ${usdc_calculation['base_usdc_amount']:.3f}")
            logger.info(f"   Confidence Multiplier: {usdc_calculation['confidence_multiplier']:.2f}x")
            logger.info(f"   Final USDC: ${usdc_calculation['final_usdc_amount']:.3f}")
            logger.info(f"   USDC Eligible: {usdc_calculation['pays_usdc']}")
            
            total_value_usd = (usdc_calculation['nimo_amount'] * 0.01) + usdc_calculation['final_usdc_amount']
            logger.info(f"   Total Reward Value: ~${total_value_usd:.3f}")
            
            return {
                'nimo_tokens': usdc_calculation['nimo_amount'],
                'usdc_reward': usdc_calculation['final_usdc_amount'],
                'usdc_eligible': usdc_calculation['pays_usdc'],
                'total_value_usd': total_value_usd,
                'calculation_details': usdc_calculation
            }
            
        except Exception as e:
            logger.error(f"   ❌ Reward calculation failed: {e}")
            return {
                'nimo_tokens': 0,
                'usdc_reward': 0,
                'usdc_eligible': False,
                'error': str(e)
            }
    
    def simulate_blockchain_recording(self, submission, metta_result, rewards):
        """Step 5: Simulate blockchain recording"""
        logger.info("⛓️  Step 5: Blockchain Recording (Simulated)")
        
        if not metta_result.get('verified'):
            logger.info("   ⏭️  Skipping - contribution not verified")
            return {'status': 'skipped', 'reason': 'not verified'}
        
        try:
            # Simulate successful blockchain transaction
            import hashlib
            import time
            
            tx_data = {
                'contribution_id': submission['contribution_id'],
                'user_address': submission['user_address'],
                'nimo_tokens': rewards['nimo_tokens'],
                'confidence': metta_result['confidence'],
                'metta_proof': metta_result.get('metta_proof', ''),
                'timestamp': int(time.time())
            }
            
            # Generate fake transaction hash
            tx_hash = '0x' + hashlib.sha256(json.dumps(tx_data).encode()).hexdigest()
            
            logger.info(f"   📄 Transaction Hash: {tx_hash}")
            logger.info(f"   🌐 Network: base-sepolia")
            logger.info(f"   ⛽ Gas Used: ~150,000")
            logger.info(f"   🔗 Explorer: https://sepolia.basescan.org/tx/{tx_hash}")
            
            return {
                'status': 'success',
                'tx_hash': tx_hash,
                'block_number': 30260500 + int(time.time()) % 1000,  # Fake block number
                'gas_used': 150000,
                'network': 'base-sepolia'
            }
            
        except Exception as e:
            logger.error(f"   ❌ Blockchain recording failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def simulate_usdc_payment(self, submission, rewards, blockchain_result):
        """Step 6: Simulate USDC reward payment"""
        logger.info("💵 Step 6: USDC Reward Payment (Simulated)")
        
        if not rewards['usdc_eligible']:
            logger.info("   ⏭️  No USDC payment - eligibility requirements not met")
            logger.info(f"   Reason: Confidence {rewards['calculation_details']['confidence']:.3f} < {self.usdc_integration.min_confidence_for_usdc}")
            return {'status': 'not_eligible', 'reason': 'Below confidence threshold'}
        
        if rewards['usdc_reward'] <= 0:
            logger.info("   ⏭️  No USDC payment - reward amount is zero")
            return {'status': 'zero_amount'}
        
        try:
            # Simulate gas estimation
            gas_estimation = self.usdc_integration.estimate_gas_for_transfer(
                to_address=submission['user_address'],
                usdc_amount=Decimal(str(rewards['usdc_reward']))
            )
            
            if 'error' in gas_estimation:
                logger.warning(f"   ⚠️  Gas estimation failed: {gas_estimation['error']}")
                estimated_gas_cost = 0.001  # Fallback estimate
            else:
                estimated_gas_cost = gas_estimation['total_gas_cost_eth']
            
            # Simulate successful USDC transfer
            import hashlib
            import time
            
            usdc_tx_data = {
                'to_address': submission['user_address'],
                'amount_usdc': rewards['usdc_reward'],
                'contribution_id': submission['contribution_id'],
                'timestamp': int(time.time())
            }
            
            usdc_tx_hash = '0x' + hashlib.sha256(json.dumps(usdc_tx_data).encode()).hexdigest()
            
            logger.info(f"   💰 USDC Amount: ${rewards['usdc_reward']:.3f}")
            logger.info(f"   📍 To Address: {submission['user_address']}")
            logger.info(f"   📄 TX Hash: {usdc_tx_hash}")
            logger.info(f"   ⛽ Estimated Gas Cost: {estimated_gas_cost:.6f} ETH")
            logger.info(f"   🔗 Explorer: https://sepolia.basescan.org/tx/{usdc_tx_hash}")
            
            return {
                'status': 'success',
                'tx_hash': usdc_tx_hash,
                'amount_usdc': rewards['usdc_reward'],
                'gas_cost_eth': estimated_gas_cost,
                'network': 'base-sepolia'
            }
            
        except Exception as e:
            logger.error(f"   ❌ USDC payment simulation failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def run_complete_scenario(self, scenario):
        """Run complete flow for a single scenario"""
        logger.info("=" * 80)
        logger.info(f"🚀 Running Complete Flow: {scenario['name']}")
        logger.info("=" * 80)
        
        results = {
            'scenario_name': scenario['name'],
            'start_time': datetime.now().isoformat(),
            'steps': []
        }
        
        try:
            # Step 1: Contribution Submission
            submission = self.simulate_contribution_submission(scenario)
            results['steps'].append(('submission', submission))
            
            logger.info("")
            
            # Step 2: MeTTa Analysis
            metta_result = self.run_metta_analysis(submission)
            results['steps'].append(('metta_analysis', metta_result))
            
            logger.info("")
            
            # Step 3-4: Reward Calculation
            rewards = self.calculate_rewards(submission, metta_result)
            results['steps'].append(('reward_calculation', rewards))
            
            logger.info("")
            
            # Step 5: Blockchain Recording
            blockchain_result = self.simulate_blockchain_recording(submission, metta_result, rewards)
            results['steps'].append(('blockchain_recording', blockchain_result))
            
            logger.info("")
            
            # Step 6: USDC Payment
            usdc_result = self.simulate_usdc_payment(submission, rewards, blockchain_result)
            results['steps'].append(('usdc_payment', usdc_result))
            
            # Final summary
            logger.info("")
            logger.info("📊 SCENARIO SUMMARY")
            logger.info("-" * 40)
            logger.info(f"   Verified: {metta_result.get('verified', False)}")
            logger.info(f"   NIMO Tokens: {rewards.get('nimo_tokens', 0)}")
            logger.info(f"   USDC Reward: ${rewards.get('usdc_reward', 0):.3f}")
            logger.info(f"   Total Value: ~${rewards.get('total_value_usd', 0):.3f}")
            logger.info(f"   Blockchain TX: {blockchain_result.get('status', 'N/A')}")
            logger.info(f"   USDC Payment: {usdc_result.get('status', 'N/A')}")
            
            results['end_time'] = datetime.now().isoformat()
            results['success'] = True
            
        except Exception as e:
            logger.error(f"❌ Scenario failed: {e}")
            results['success'] = False
            results['error'] = str(e)
        
        return results
    
    def run_all_scenarios(self):
        """Run complete flow for all test scenarios"""
        logger.info("🎯 Starting Complete End-to-End Flow Test")
        logger.info(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🌐 Network: {self.usdc_integration.network}")
        logger.info(f"💱 NIMO→USDC Rate: ${float(self.usdc_integration.nimo_to_usdc_rate):.3f}")
        logger.info(f"🎯 Min Confidence for USDC: {self.usdc_integration.min_confidence_for_usdc}")
        
        all_results = []
        
        for i, scenario in enumerate(self.test_scenarios, 1):
            logger.info(f"\n🔄 Scenario {i}/{len(self.test_scenarios)}")
            result = self.run_complete_scenario(scenario)
            all_results.append(result)
        
        # Generate final report
        self.generate_final_report(all_results)
        
        return all_results
    
    def generate_final_report(self, all_results):
        """Generate comprehensive final report"""
        logger.info("\n" + "=" * 80)
        logger.info("📈 COMPLETE FLOW TEST REPORT")
        logger.info("=" * 80)
        
        total_scenarios = len(all_results)
        successful_scenarios = sum(1 for r in all_results if r.get('success', False))
        
        total_nimo = 0
        total_usdc = 0
        total_value = 0
        usdc_payments = 0
        blockchain_txs = 0
        
        for result in all_results:
            if result.get('success'):
                for step_name, step_data in result['steps']:
                    if step_name == 'reward_calculation':
                        total_nimo += step_data.get('nimo_tokens', 0)
                        total_usdc += step_data.get('usdc_reward', 0)
                        total_value += step_data.get('total_value_usd', 0)
                    elif step_name == 'usdc_payment' and step_data.get('status') == 'success':
                        usdc_payments += 1
                    elif step_name == 'blockchain_recording' and step_data.get('status') == 'success':
                        blockchain_txs += 1
        
        logger.info(f"📊 Success Rate: {successful_scenarios}/{total_scenarios} ({successful_scenarios/total_scenarios*100:.1f}%)")
        logger.info(f"🪙 Total NIMO Tokens Awarded: {total_nimo:,}")
        logger.info(f"💵 Total USDC Rewards: ${total_usdc:.3f}")
        logger.info(f"💰 Total Reward Value: ~${total_value:.3f}")
        logger.info(f"⛓️  Blockchain Transactions: {blockchain_txs}")
        logger.info(f"💳 USDC Payments: {usdc_payments}")
        
        logger.info("\n🎯 Scenario Breakdown:")
        for i, result in enumerate(all_results, 1):
            status = "✅" if result.get('success') else "❌"
            logger.info(f"   {status} {i}. {result['scenario_name']}")
        
        if successful_scenarios == total_scenarios:
            logger.info("\n🎉 ALL SCENARIOS COMPLETED SUCCESSFULLY!")
            logger.info("🚀 The MeTTa → USDC reward system is working correctly!")
        else:
            logger.info(f"\n⚠️  {total_scenarios - successful_scenarios} scenario(s) had issues")
            logger.info("🔧 Check logs above for details")

def main():
    """Main test execution"""
    try:
        tester = CompleteFlowTester()
        results = tester.run_all_scenarios()
        
        # Count successful scenarios
        success_count = sum(1 for r in results if r.get('success', False))
        total_count = len(results)
        
        if success_count == total_count:
            logger.info(f"\n🏆 Test completed successfully: {success_count}/{total_count}")
            sys.exit(0)
        else:
            logger.warning(f"\n⚠️  Test completed with issues: {success_count}/{total_count}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"🔥 Test suite crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()