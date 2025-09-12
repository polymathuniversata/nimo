"""
Base Blockchain Service

Abstract base class providing common functionality for blockchain services.
This enables code reuse and consistent interfaces across different blockchain implementations.
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from flask import current_app

# Remove error handler import for now to avoid import issues
# from .error_handler import ErrorHandler, NimoError, ErrorCategory, ErrorSeverity

class BlockchainType(Enum):
    """Supported blockchain types"""
    ETHEREUM = "ethereum"
    CARDANO = "cardano"
    POLYGON = "polygon"

class NetworkStatus(Enum):
    """Network connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"

@dataclass
class TransactionStatus:
    """Standardized transaction status"""
    tx_hash: str
    status: str  # 'pending', 'confirmed', 'failed', 'unknown'
    block_number: Optional[int] = None
    block_time: Optional[str] = None
    gas_used: Optional[int] = None
    fees: Optional[Union[int, float]] = None
    error: Optional[str] = None
    confirmed: bool = False

@dataclass
class NetworkInfo:
    """Standardized network information"""
    network: str
    blockchain_type: BlockchainType
    connected: bool
    latest_block: Optional[int] = None
    current_gas_price: Optional[Union[int, float]] = None
    explorer_url: Optional[str] = None
    contract_addresses: Optional[Dict[str, str]] = None
    error: Optional[str] = None

@dataclass
class TransactionCost:
    """Standardized transaction cost estimation"""
    operation: str
    estimated_gas: Optional[int] = None
    gas_price: Optional[Union[int, float]] = None
    total_cost: Optional[Union[int, float]] = None
    currency: str = "wei"  # wei, lovelace, etc.
    error: Optional[str] = None

class BlockchainServiceError(Exception):
    """Base exception for blockchain service errors"""
    def __init__(self, message: str, service: str = None, operation: str = None):
        self.message = message
        self.service = service
        self.operation = operation
        super().__init__(f"{service or 'Blockchain'}: {message}")

class ConnectionError(BlockchainServiceError):
    """Connection-related errors"""
    pass

class TransactionError(BlockchainServiceError):
    """Transaction-related errors"""
    pass

class ConfigurationError(BlockchainServiceError):
    """Configuration-related errors"""
    pass

class BaseBlockchainService(ABC):
    """
    Abstract base class for blockchain services.

    Provides common functionality and enforces consistent interfaces
    across different blockchain implementations.
    """

    def __init__(self, network: str, blockchain_type: BlockchainType):
        """Initialize base blockchain service"""
        self.network = network
        self.blockchain_type = blockchain_type
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{network}")

        # Service state
        self.available = True
        self.error: Optional[str] = None
        self._connection_status = NetworkStatus.DISCONNECTED

        # Error handling - simplified for now
        # self.error_handler = ErrorHandler(self.__class__.__name__.lower())

        # Transaction tracking
        self.pending_transactions: Dict[str, Dict] = {}
        self.failed_transactions: Dict[str, Dict] = {}

        # Initialize service
        self._initialize_service()

    @abstractmethod
    def _initialize_service(self):
        """Initialize blockchain-specific service components"""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to blockchain network"""
        pass

    @abstractmethod
    def get_transaction_status(self, tx_hash: str) -> TransactionStatus:
        """Get status of a transaction"""
        pass

    @abstractmethod
    def get_network_info(self) -> NetworkInfo:
        """Get current network information"""
        pass

    @abstractmethod
    def estimate_transaction_cost(self, operation: str, params: Dict = None) -> TransactionCost:
        """Estimate transaction cost for an operation"""
        pass

    @abstractmethod
    def get_balance(self, address: str) -> Dict[str, Any]:
        """Get balance for an address"""
        pass

    @abstractmethod
    def send_transaction(self, **kwargs) -> Dict[str, Any]:
        """Send a transaction (implementation-specific)"""
        pass

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()

    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        import uuid
        return str(uuid.uuid4())[:8]

    def _track_transaction(self, tx_hash: str, operation: str, params: Dict = None):
        """Track a pending transaction"""
        self.pending_transactions[tx_hash] = {
            'hash': tx_hash,
            'operation': operation,
            'timestamp': self._get_current_timestamp(),
            'status': 'pending',
            'params': params or {}
        }

    def _track_failed_transaction(self, error: str, operation: str, params: Dict = None) -> str:
        """Track a failed transaction and return error ID"""
        error_id = self._generate_error_id()
        self.failed_transactions[error_id] = {
            'error': error,
            'operation': operation,
            'timestamp': self._get_current_timestamp(),
            'params': params or {}
        }
        return error_id

    def _update_connection_status(self):
        """Update connection status"""
        try:
            if self.is_connected():
                self._connection_status = NetworkStatus.CONNECTED
                self.available = True
                self.error = None
            else:
                self._connection_status = NetworkStatus.DISCONNECTED
                self.available = False
        except Exception as e:
            self._connection_status = NetworkStatus.ERROR
            self.available = False
            self.error = str(e)
            self.logger.error(f"Connection status check failed: {e}")

    def get_service_status(self) -> Dict[str, Any]:
        """Get overall service status"""
        self._update_connection_status()

        return {
            'service': self.__class__.__name__,
            'network': self.network,
            'blockchain_type': self.blockchain_type.value,
            'available': self.available,
            'connection_status': self._connection_status.value,
            'error': self.error,
            'pending_transactions': len(self.pending_transactions),
            'failed_transactions': len(self.failed_transactions)
        }

    def cleanup_pending_transactions(self, max_age_hours: int = 24):
        """Clean up old pending transactions"""
        import datetime

        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=max_age_hours)
        cutoff_iso = cutoff_time.isoformat()

        # Remove old pending transactions
        to_remove = []
        for tx_hash, tx_data in self.pending_transactions.items():
            if tx_data['timestamp'] < cutoff_iso:
                to_remove.append(tx_hash)

        for tx_hash in to_remove:
            self.pending_transactions.pop(tx_hash, None)

        # Remove old failed transactions
        to_remove = []
        for error_id, error_data in self.failed_transactions.items():
            if error_data['timestamp'] < cutoff_iso:
                to_remove.append(error_id)

        for error_id in to_remove:
            self.failed_transactions.pop(error_id, None)

        self.logger.info(f"Cleaned up {len(to_remove)} old transactions")

    def validate_address(self, address: str) -> bool:
        """Validate blockchain address format (to be overridden by subclasses)"""
        return bool(address and len(address.strip()) > 0)

    def format_transaction_response(self, tx_hash: str, **kwargs) -> Dict[str, Any]:
        """Format standardized transaction response"""
        return {
            'success': True,
            'tx_hash': tx_hash,
            'network': self.network,
            'blockchain_type': self.blockchain_type.value,
            'timestamp': self._get_current_timestamp(),
            **kwargs
        }

    def format_error_response(self, error: Union[str, Exception], operation: str = None, **kwargs) -> Dict[str, Any]:
        """Format standardized error response"""
        error_message = str(error) if isinstance(error, Exception) else error
        
        # Track failed transaction
        error_id = self._track_failed_transaction(error_message, operation or 'unknown', kwargs)

        return {
            'success': False,
            'error': error_message,
            'error_id': error_id,
            'network': self.network,
            'blockchain_type': self.blockchain_type.value,
            'timestamp': self._get_current_timestamp(),
            'operation': operation,
            **kwargs
        }

    def handle_service_exception(self, exception: Exception, operation: str = None, **kwargs) -> Dict[str, Any]:
        """Handle service exceptions with standardized error response"""
        return self.format_error_response(exception, operation, **kwargs)

    def log_operation(self, operation: str, success: bool, details: Dict = None):
        """Log blockchain operation with consistent format"""
        level = logging.INFO if success else logging.ERROR
        status = "successful" if success else "failed"

        message = f"{operation} {status}"
        if details:
            message += f" - {details}"

        self.logger.log(level, message)

    @classmethod
    def create_service(cls, blockchain_type: str, network: str, **kwargs):
        """Factory method to create appropriate service instance"""
        from .ethereum_service import EthereumService
        from .cardano_service import CardanoService

        blockchain_enum = BlockchainType(blockchain_type.lower())

        if blockchain_enum == BlockchainType.ETHEREUM:
            return EthereumService(network, **kwargs)
        elif blockchain_enum == BlockchainType.CARDANO:
            return CardanoService(network, **kwargs)
        else:
            raise ValueError(f"Unsupported blockchain type: {blockchain_type}")