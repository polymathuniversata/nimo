"""
Enhanced IPFS Service with OOP Principles

Provides decentralized file storage for metadata, evidence, and other content
using IPFS (InterPlanetary File System) with proper object-oriented design,
abstraction, encapsulation, and modularity.
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import requests
from flask import current_app
import logging
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

from services.base_blockchain_service import BaseBlockchainService, BlockchainType, BlockchainServiceError

class IPFSStorageType(Enum):
    """Supported IPFS storage types"""
    LOCAL_NODE = "local_node"
    PUBLIC_GATEWAY = "public_gateway"
    PINNING_SERVICE = "pinning_service"

class IPFSUploadStrategy(ABC):
    """Abstract strategy for IPFS upload operations"""

    @abstractmethod
    def upload_file(self, file_path: Union[str, Path], service: 'IPFSService') -> Optional[str]:
        """Upload a file using specific strategy"""
        pass

    @abstractmethod
    def upload_json(self, data: Dict[str, Any], service: 'IPFSService') -> Optional[str]:
        """Upload JSON data using specific strategy"""
        pass

class LocalNodeUploadStrategy(IPFSUploadStrategy):
    """Upload strategy using local IPFS node"""

    def upload_file(self, file_path: Union[str, Path], service: 'IPFSService') -> Optional[str]:
        """Upload file using local IPFS node"""
        file_path = Path(file_path)

        if not file_path.exists():
            service.logger.error(f"File not found: {file_path}")
            return None

        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{service.api_url}add",
                    files=files,
                    timeout=30
                )

            if response.status_code == 200:
                result = response.json()
                ipfs_hash = result['Hash']
                service.logger.info(f"File uploaded to IPFS: {ipfs_hash}")
                return ipfs_hash
            else:
                service.logger.error(f"Failed to upload file: {response.text}")
                return None

        except Exception as e:
            service.logger.error(f"Error uploading file to IPFS: {e}")
            return None

    def upload_json(self, data: Dict[str, Any], service: 'IPFSService') -> Optional[str]:
        """Upload JSON data using local IPFS node"""
        try:
            json_string = json.dumps(data, indent=2, ensure_ascii=False)

            files = {'file': ('data.json', json_string, 'application/json')}
            response = requests.post(
                f"{service.api_url}add",
                files=files,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                ipfs_hash = result['Hash']
                service.logger.info(f"JSON uploaded to IPFS: {ipfs_hash}")
                return ipfs_hash
            else:
                service.logger.error(f"Failed to upload JSON: {response.text}")
                return None

        except Exception as e:
            service.logger.error(f"Error uploading JSON to IPFS: {e}")
            return None

class PublicGatewayUploadStrategy(IPFSUploadStrategy):
    """Upload strategy using public IPFS gateway (read-only)"""

    def upload_file(self, file_path: Union[str, Path], service: 'IPFSService') -> Optional[str]:
        """Public gateway doesn't support uploads"""
        service.logger.warning("Public gateway does not support file uploads")
        return None

    def upload_json(self, data: Dict[str, Any], service: 'IPFSService') -> Optional[str]:
        """Public gateway doesn't support uploads"""
        service.logger.warning("Public gateway does not support JSON uploads")
        return None

@dataclass
class IPFSFileInfo:
    """IPFS file information"""
    hash: str
    size: Optional[int] = None
    type: Optional[str] = None
    links: Optional[List[Dict]] = None

@dataclass
class IPFSServiceConfig:
    """Configuration for IPFS service"""
    gateway_url: str
    api_url: str
    storage_type: IPFSStorageType
    timeout: int = 30
    max_retries: int = 3

class IPFSServiceError(BlockchainServiceError):
    """Base exception for IPFS service errors"""
    def __init__(self, message: str, operation: str = None, file_hash: str = None):
        self.file_hash = file_hash
        super().__init__(message, "IPFSService", operation)

class IPFSConnectionError(IPFSServiceError):
    """Exception raised when IPFS connection fails"""
    pass

class IPFSUploadError(IPFSServiceError):
    """Exception raised when IPFS upload fails"""
    pass

class IPFSDownloadError(IPFSServiceError):
    """Exception raised when IPFS download fails"""
    pass

class IPFSService(BaseBlockchainService):
    """
    Enhanced IPFS Service with proper OOP design

    Provides decentralized file storage with abstraction, encapsulation,
    and strategy pattern for different upload methods.
    """

    def __init__(self, config: IPFSServiceConfig = None):
        """Initialize IPFS service with configuration"""
        super().__init__("ipfs", BlockchainType.ETHEREUM)  # IPFS is blockchain-agnostic

        # Service configuration
        self.config = config or self._create_default_config()

        # Strategy pattern for upload operations
        self.upload_strategy = self._create_upload_strategy()

        # Service state
        self.local_node_available = self._check_local_node()
        self._file_cache: Dict[str, bytes] = {}

        self.logger.info(f"IPFS Service initialized with {self.config.storage_type.value}")

    def _initialize_service(self):
        """Initialize IPFS-specific service components"""
        self.logger.info("Initializing IPFS service components")

        # Validate configuration
        if not self.config.gateway_url:
            raise IPFSServiceError("Gateway URL is required")

        # Test connectivity
        if not self._test_connectivity():
            self.logger.warning("IPFS connectivity test failed")

    def _create_default_config(self) -> IPFSServiceConfig:
        """Create default IPFS service configuration"""
        return IPFSServiceConfig(
            gateway_url=os.getenv('IPFS_GATEWAY_URL', 'https://ipfs.io/ipfs/'),
            api_url=os.getenv('IPFS_API_URL', 'http://localhost:5001/api/v0/'),
            storage_type=IPFSStorageType.LOCAL_NODE
        )

    def _create_upload_strategy(self) -> IPFSUploadStrategy:
        """Create appropriate upload strategy based on configuration"""
        if self.config.storage_type == IPFSStorageType.LOCAL_NODE:
            return LocalNodeUploadStrategy()
        elif self.config.storage_type == IPFSStorageType.PUBLIC_GATEWAY:
            return PublicGatewayUploadStrategy()
        else:
            # Default to local node
            return LocalNodeUploadStrategy()

    def _check_local_node(self) -> bool:
        """Check if local IPFS node is running"""
        try:
            response = requests.post(
                f"{self.config.api_url}id",
                timeout=self.config.timeout
            )
            return response.status_code == 200
        except Exception:
            return False

    def _test_connectivity(self) -> bool:
        """Test IPFS connectivity"""
        try:
            # Test gateway connectivity
            test_hash = "QmYwAPJzv5CZsnAztECyHLhSXGYPFHJK1YwK1BnNfJ3x1"  # Known test hash
            url = f"{self.config.gateway_url}{test_hash}"
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def is_connected(self) -> bool:
        """Check if IPFS service is connected"""
        if self.config.storage_type == IPFSStorageType.LOCAL_NODE:
            return self.local_node_available
        else:
            return self._test_connectivity()

    def get_transaction_status(self, tx_hash: str):
        """IPFS doesn't have transactions, return mock status"""
        return {
            'hash': tx_hash,
            'status': 'confirmed',
            'confirmed': True
        }

    def get_network_info(self):
        """Get IPFS network information"""
        return {
            'network': 'ipfs',
            'storage_type': self.config.storage_type.value,
            'local_node_available': self.local_node_available,
            'gateway_url': self.config.gateway_url
        }

    def estimate_transaction_cost(self, operation: str, params: Dict = None):
        """IPFS operations are free, return zero cost"""
        return {
            'operation': operation,
            'estimated_cost': 0,
            'currency': 'free'
        }

    def get_balance(self, address: str):
        """IPFS doesn't have balances, return mock data"""
        return {
            'address': address,
            'balance': 0,
            'currency': 'free'
        }

    def send_transaction(self, **kwargs):
        """IPFS doesn't support transactions, return mock response"""
        return {
            'success': False,
            'error': 'IPFS does not support transactions'
        }

    def upload_file(self, file_path: Union[str, Path]) -> Optional[str]:
        """
        Upload a file to IPFS using the configured strategy

        Args:
            file_path: Path to the file to upload

        Returns:
            IPFS hash (CID) if successful, None otherwise

        Raises:
            IPFSUploadError: If upload fails
        """
        try:
            ipfs_hash = self.upload_strategy.upload_file(file_path, self)
            if not ipfs_hash:
                raise IPFSUploadError("File upload failed")
            return ipfs_hash

        except Exception as e:
            self.logger.error(f"Error uploading file: {e}")
            raise IPFSUploadError(f"File upload failed: {str(e)}", operation="upload_file")

    def upload_json(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Upload JSON data to IPFS using the configured strategy

        Args:
            data: JSON data to upload

        Returns:
            IPFS hash (CID) if successful, None otherwise

        Raises:
            IPFSUploadError: If upload fails
        """
        try:
            if not isinstance(data, dict):
                raise IPFSUploadError("Data must be a dictionary")

            ipfs_hash = self.upload_strategy.upload_json(data, self)
            if not ipfs_hash:
                raise IPFSUploadError("JSON upload failed")
            return ipfs_hash

        except IPFSUploadError:
            raise
        except Exception as e:
            self.logger.error(f"Error uploading JSON: {e}")
            raise IPFSUploadError(f"JSON upload failed: {str(e)}", operation="upload_json")

    def download_file(self, ipfs_hash: str, output_path: Union[str, Path] = None) -> Optional[bytes]:
        """
        Download a file from IPFS

        Args:
            ipfs_hash: IPFS hash (CID) of the file
            output_path: Optional path to save the file

        Returns:
            File content as bytes if successful, None otherwise

        Raises:
            IPFSDownloadError: If download fails
        """
        try:
            # Check cache first
            if ipfs_hash in self._file_cache:
                content = self._file_cache[ipfs_hash]
            else:
                url = f"{self.config.gateway_url}{ipfs_hash}"
                response = requests.get(url, timeout=self.config.timeout)

                if response.status_code != 200:
                    raise IPFSDownloadError(f"Failed to download file: HTTP {response.status_code}")

                content = response.content
                # Cache the content
                self._file_cache[ipfs_hash] = content

            # Save to file if output path provided
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(content)
                self.logger.info(f"File downloaded from IPFS: {output_path}")

            return content

        except IPFSDownloadError:
            raise
        except Exception as e:
            self.logger.error(f"Error downloading file from IPFS: {e}")
            raise IPFSDownloadError(f"File download failed: {str(e)}", operation="download_file", file_hash=ipfs_hash)

    def download_json(self, ipfs_hash: str) -> Optional[Dict[str, Any]]:
        """
        Download JSON data from IPFS

        Args:
            ipfs_hash: IPFS hash (CID) of the JSON data

        Returns:
            Parsed JSON data if successful, None otherwise

        Raises:
            IPFSDownloadError: If download fails
        """
        try:
            content = self.download_file(ipfs_hash)
            if content:
                json_data = json.loads(content.decode('utf-8'))
                self.logger.info(f"JSON data retrieved from IPFS: {ipfs_hash}")
                return json_data
            return None

        except (IPFSDownloadError, json.JSONDecodeError) as e:
            self.logger.error(f"Error downloading JSON from IPFS: {e}")
            raise IPFSDownloadError(f"JSON download failed: {str(e)}", operation="download_json", file_hash=ipfs_hash)

    def get_file_url(self, ipfs_hash: str) -> str:
        """
        Get HTTP URL for an IPFS file

        Args:
            ipfs_hash: IPFS hash (CID)

        Returns:
            HTTP URL to access the file
        """
        return f"{self.config.gateway_url}{ipfs_hash}"

    def pin_file(self, ipfs_hash: str) -> bool:
        """
        Pin a file to ensure it stays available

        Args:
            ipfs_hash: IPFS hash (CID) to pin

        Returns:
            True if pinned successfully, False otherwise

        Raises:
            IPFSServiceError: If pinning fails
        """
        if not self.local_node_available:
            self.logger.warning("Local IPFS node not available, cannot pin files")
            return False

        try:
            response = requests.post(
                f"{self.config.api_url}pin/add",
                params={'arg': ipfs_hash},
                timeout=self.config.timeout
            )

            if response.status_code == 200:
                self.logger.info(f"File pinned successfully: {ipfs_hash}")
                return True
            else:
                raise IPFSServiceError(f"Failed to pin file: {response.text}")

        except Exception as e:
            self.logger.error(f"Error pinning file: {e}")
            raise IPFSServiceError(f"File pinning failed: {str(e)}", operation="pin_file", file_hash=ipfs_hash)

    def unpin_file(self, ipfs_hash: str) -> bool:
        """
        Unpin a file

        Args:
            ipfs_hash: IPFS hash (CID) to unpin

        Returns:
            True if unpinned successfully, False otherwise

        Raises:
            IPFSServiceError: If unpinning fails
        """
        if not self.local_node_available:
            self.logger.warning("Local IPFS node not available, cannot unpin files")
            return False

        try:
            response = requests.post(
                f"{self.config.api_url}pin/rm",
                params={'arg': ipfs_hash},
                timeout=self.config.timeout
            )

            if response.status_code == 200:
                self.logger.info(f"File unpinned successfully: {ipfs_hash}")
                return True
            else:
                raise IPFSServiceError(f"Failed to unpin file: {response.text}")

        except Exception as e:
            self.logger.error(f"Error unpinning file: {e}")
            raise IPFSServiceError(f"File unpinning failed: {str(e)}", operation="unpin_file", file_hash=ipfs_hash)

    def get_file_info(self, ipfs_hash: str) -> Optional[IPFSFileInfo]:
        """
        Get information about a file on IPFS

        Args:
            ipfs_hash: IPFS hash (CID)

        Returns:
            IPFSFileInfo object if available, None otherwise

        Raises:
            IPFSServiceError: If info retrieval fails
        """
        if not self.local_node_available:
            self.logger.warning("Local IPFS node not available, cannot get file info")
            return None

        try:
            response = requests.post(
                f"{self.config.api_url}object/stat",
                params={'arg': ipfs_hash},
                timeout=self.config.timeout
            )

            if response.status_code == 200:
                info = response.json()
                file_info = IPFSFileInfo(
                    hash=ipfs_hash,
                    size=info.get('DataSize'),
                    type=info.get('Type'),
                    links=info.get('Links', [])
                )
                self.logger.info(f"File info retrieved: {ipfs_hash}")
                return file_info
            else:
                raise IPFSServiceError(f"Failed to get file info: {response.text}")

        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
            raise IPFSServiceError(f"File info retrieval failed: {str(e)}", operation="get_file_info", file_hash=ipfs_hash)

    def clear_cache(self):
        """Clear the internal file cache"""
        self._file_cache.clear()
        self.logger.info("IPFS file cache cleared")

    def get_service_status(self) -> Dict[str, Any]:
        """Get IPFS service status"""
        return {
            'service': 'IPFSService',
            'storage_type': self.config.storage_type.value,
            'local_node_available': self.local_node_available,
            'gateway_url': self.config.gateway_url,
            'api_url': self.config.api_url,
            'cache_size': len(self._file_cache),
            'connected': self.is_connected()
        }

# Factory function for creating IPFS service instances
def create_ipfs_service(config: IPFSServiceConfig = None) -> IPFSService:
    """Factory function to create IPFSService with configuration"""
    return IPFSService(config)

# Singleton instance for backward compatibility
_ipfs_service_instance = None

def get_ipfs_service() -> IPFSService:
    """Get singleton IPFS service instance (for backward compatibility)"""
    global _ipfs_service_instance
    if _ipfs_service_instance is None:
        _ipfs_service_instance = IPFSService()
    return _ipfs_service_instance

# Backward compatibility methods
def store_json(data: Dict[str, Any]) -> Optional[str]:
    """Backward compatibility wrapper for upload_json"""
    service = get_ipfs_service()
    return service.upload_json(data)