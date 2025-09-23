import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from web3 import Web3
from blockfrost import BlockFrostApi, ApiUrls
from prometheus_client import start_http_server, Counter, Gauge, Histogram

# Metrics
PROOF_SUBMISSIONS = Counter('metta_bridge_proof_submissions_total', 'Total number of proof submissions')
PROOF_VERIFICATIONS = Counter('metta_bridge_proof_verifications_total', 'Total number of proof verifications')
DECISION_EXECUTIONS = Counter('metta_bridge_decision_executions_total', 'Total number of decision executions')
ACTIVE_CHALLENGES = Gauge('metta_bridge_active_challenges', 'Number of active challenges')
CONTRACT_BALANCE = Gauge('metta_bridge_contract_balance_ada', 'Current contract balance in ADA')
PROOF_PROCESSING_TIME = Histogram('metta_bridge_proof_processing_seconds', 'Time taken to process proofs')

@dataclass
class AlertConfig:
    min_contract_balance: int  # Minimum contract balance in ADA
    max_active_challenges: int  # Maximum number of active challenges
    proof_processing_timeout: int  # Maximum time for proof processing in seconds
    alert_webhook_url: str  # Discord/Slack webhook URL for alerts

class MettaBridgeMonitor:
    def __init__(self, config_path: str):
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.blockfrost_api = BlockFrostApi(
            project_id=self.config['blockfrost_project_id'],
            base_url=ApiUrls.mainnet.value
        )
        self.alert_config = AlertConfig(**self.config['alert_config'])
        
        # Start Prometheus metrics server
        start_http_server(self.config['prometheus_port'])
        
    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger('metta_bridge_monitor')
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler('bridge_monitor.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _load_config(self, config_path: str) -> Dict:
        with open(config_path, 'r') as f:
            return json.load(f)
    
    async def monitor_contract_balance(self):
        """Monitor contract balance and alert if below threshold"""
        try:
            address = self.config['contract_address']
            balance = await self.blockfrost_api.address(address)
            balance_ada = float(balance.amount[0].quantity) / 1_000_000
            
            CONTRACT_BALANCE.set(balance_ada)
            
            if balance_ada < self.alert_config.min_contract_balance:
                await self._send_alert(
                    f"⚠️ Contract balance low: {balance_ada} ADA"
                    f"(below {self.alert_config.min_contract_balance} ADA threshold)"
                )
        except Exception as e:
            self.logger.error(f"Error monitoring contract balance: {e}")
    
    async def monitor_active_challenges(self):
        """Monitor number of active challenges and alert if above threshold"""
        try:
            # Query contract state for active challenges
            active_challenges = await self._get_active_challenges()
            ACTIVE_CHALLENGES.set(len(active_challenges))
            
            if len(active_challenges) > self.alert_config.max_active_challenges:
                await self._send_alert(
                    f"⚠️ High number of active challenges: {len(active_challenges)}"
                    f"(above {self.alert_config.max_active_challenges} threshold)"
                )
        except Exception as e:
            self.logger.error(f"Error monitoring active challenges: {e}")
    
    async def monitor_proof_processing(self):
        """Monitor proof processing times and alert on timeouts"""
        try:
            # Query recent proofs and their processing times
            recent_proofs = await self._get_recent_proofs()
            
            for proof in recent_proofs:
                processing_time = time.time() - proof['submitted_at']
                PROOF_PROCESSING_TIME.observe(processing_time)
                
                if processing_time > self.alert_config.proof_processing_timeout:
                    await self._send_alert(
                        f"⚠️ Proof processing timeout for ID {proof['proof_id']}"
                        f"(processing time: {processing_time}s)"
                    )
        except Exception as e:
            self.logger.error(f"Error monitoring proof processing: {e}")
    
    async def _get_active_challenges(self) -> List[Dict]:
        """Query contract state for active challenges"""
        # Implementation depends on contract state query mechanism
        pass
    
    async def _get_recent_proofs(self) -> List[Dict]:
        """Query recent proof submissions"""
        # Implementation depends on contract state query mechanism
        pass
    
    async def _send_alert(self, message: str):
        """Send alert to configured webhook"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                webhook_data = {
                    'content': message,
                    'username': 'MeTTa Bridge Monitor',
                    'avatar_url': 'https://example.com/bot-avatar.png'
                }
                async with session.post(self.alert_config.alert_webhook_url, json=webhook_data) as resp:
                    if resp.status != 204:
                        self.logger.error(f"Failed to send alert: {resp.status}")
        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")
    
    async def run(self):
        """Main monitoring loop"""
        while True:
            await self.monitor_contract_balance()
            await self.monitor_active_challenges()
            await self.monitor_proof_processing()
            
            # Update metrics
            PROOF_SUBMISSIONS._value.set(
                await self._get_total_proof_submissions()
            )
            PROOF_VERIFICATIONS._value.set(
                await self._get_total_proof_verifications()
            )
            DECISION_EXECUTIONS._value.set(
                await self._get_total_decision_executions()
            )
            
            await asyncio.sleep(self.config['monitoring_interval'])

if __name__ == '__main__':
    import asyncio
    
    monitor = MettaBridgeMonitor('config.json')
    asyncio.run(monitor.run())