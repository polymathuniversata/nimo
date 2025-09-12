"""
IPFS Service for Nimo Platform

This service provides decentralized file storage for metadata, evidence,
and other content using IPFS (InterPlanetary File System).
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import requests
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class IPFSService:
    """
    IPFS Service for decentralized storage
    """

    def __init__(self, gateway_url: str = None, api_url: str = None):
        """
        Initialize IPFS service

        Args:
            gateway_url: IPFS gateway URL (e.g., 'https://ipfs.io/ipfs/')
            api_url: IPFS API URL (e.g., 'http://localhost:5001/api/v0/')
        """
        self.gateway_url = gateway_url or os.getenv('IPFS_GATEWAY_URL', 'https://ipfs.io/ipfs/')
        self.api_url = api_url or os.getenv('IPFS_API_URL', 'http://localhost:5001/api/v0/')

        # Ensure URLs end with proper separators
        if not self.gateway_url.endswith('/'):
            self.gateway_url += '/'
        if not self.api_url.endswith('/'):
            self.api_url += '/'

        # Check if local IPFS node is available
        self.local_node_available = self._check_local_node()

        logger.info(f"IPFS Service initialized with gateway: {self.gateway_url}")
        if self.local_node_available:
            logger.info(f"Local IPFS node available at: {self.api_url}")
        else:
            logger.warning("Local IPFS node not available, using public gateway only")

    def _check_local_node(self) -> bool:
        """Check if local IPFS node is running"""
        try:
            response = requests.post(f"{self.api_url}id", timeout=5)
            return response.status_code == 200
        except:
            return False

    def upload_file(self, file_path: Union[str, Path]) -> Optional[str]:
        """
        Upload a file to IPFS

        Args:
            file_path: Path to the file to upload

        Returns:
            IPFS hash (CID) if successful, None otherwise
        """
        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        try:
            if self.local_node_available:
                # Use local IPFS node
                with open(file_path, 'rb') as f:
                    files = {'file': f}
                    response = requests.post(
                        f"{self.api_url}add",
                        files=files,
                        timeout=30
                    )

                if response.status_code == 200:
                    result = response.json()
                    ipfs_hash = result['Hash']
                    logger.info(f"File uploaded to IPFS: {ipfs_hash}")
                    return ipfs_hash
                else:
                    logger.error(f"Failed to upload file: {response.text}")
                    return None
            else:
                # Fallback to pinning service or public gateway
                logger.warning("Local IPFS node not available, file upload not supported")
                return None

        except Exception as e:
            logger.error(f"Error uploading file to IPFS: {e}")
            return None

    def upload_json(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Upload JSON data to IPFS

        Args:
            data: JSON data to upload

        Returns:
            IPFS hash (CID) if successful, None otherwise
        """
        try:
            json_string = json.dumps(data, indent=2, ensure_ascii=False)

            if self.local_node_available:
                # Use local IPFS node
                files = {'file': ('data.json', json_string, 'application/json')}
                response = requests.post(
                    f"{self.api_url}add",
                    files=files,
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    ipfs_hash = result['Hash']
                    logger.info(f"JSON uploaded to IPFS: {ipfs_hash}")
                    return ipfs_hash
                else:
                    logger.error(f"Failed to upload JSON: {response.text}")
                    return None
            else:
                # Fallback to pinning service
                logger.warning("Local IPFS node not available, JSON upload not supported")
                return None

        except Exception as e:
            logger.error(f"Error uploading JSON to IPFS: {e}")
            return None

    def download_file(self, ipfs_hash: str, output_path: Union[str, Path] = None) -> Optional[bytes]:
        """
        Download a file from IPFS

        Args:
            ipfs_hash: IPFS hash (CID) of the file
            output_path: Optional path to save the file

        Returns:
            File content as bytes if successful, None otherwise
        """
        try:
            url = f"{self.gateway_url}{ipfs_hash}"
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                if output_path:
                    output_path = Path(output_path)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    logger.info(f"File downloaded from IPFS: {output_path}")
                else:
                    logger.info(f"File content retrieved from IPFS: {ipfs_hash}")

                return response.content
            else:
                logger.error(f"Failed to download file from IPFS: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error downloading file from IPFS: {e}")
            return None

    def download_json(self, ipfs_hash: str) -> Optional[Dict[str, Any]]:
        """
        Download JSON data from IPFS

        Args:
            ipfs_hash: IPFS hash (CID) of the JSON data

        Returns:
            Parsed JSON data if successful, None otherwise
        """
        try:
            content = self.download_file(ipfs_hash)
            if content:
                json_data = json.loads(content.decode('utf-8'))
                logger.info(f"JSON data retrieved from IPFS: {ipfs_hash}")
                return json_data
            else:
                return None

        except Exception as e:
            logger.error(f"Error downloading JSON from IPFS: {e}")
            return None

    def get_file_url(self, ipfs_hash: str) -> str:
        """
        Get HTTP URL for an IPFS file

        Args:
            ipfs_hash: IPFS hash (CID)

        Returns:
            HTTP URL to access the file
        """
        return f"{self.gateway_url}{ipfs_hash}"

    def pin_file(self, ipfs_hash: str) -> bool:
        """
        Pin a file to ensure it stays available

        Args:
            ipfs_hash: IPFS hash (CID) to pin

        Returns:
            True if pinned successfully, False otherwise
        """
        if not self.local_node_available:
            logger.warning("Local IPFS node not available, cannot pin files")
            return False

        try:
            response = requests.post(
                f"{self.api_url}pin/add",
                params={'arg': ipfs_hash},
                timeout=30
            )

            if response.status_code == 200:
                logger.info(f"File pinned successfully: {ipfs_hash}")
                return True
            else:
                logger.error(f"Failed to pin file: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error pinning file: {e}")
            return False

    def unpin_file(self, ipfs_hash: str) -> bool:
        """
        Unpin a file

        Args:
            ipfs_hash: IPFS hash (CID) to unpin

        Returns:
            True if unpinned successfully, False otherwise
        """
        if not self.local_node_available:
            logger.warning("Local IPFS node not available, cannot unpin files")
            return False

        try:
            response = requests.post(
                f"{self.api_url}pin/rm",
                params={'arg': ipfs_hash},
                timeout=30
            )

            if response.status_code == 200:
                logger.info(f"File unpinned successfully: {ipfs_hash}")
                return True
            else:
                logger.error(f"Failed to unpin file: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error unpinning file: {e}")
            return False

    def get_file_info(self, ipfs_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a file on IPFS

        Args:
            ipfs_hash: IPFS hash (CID)

        Returns:
            File information if available, None otherwise
        """
        if not self.local_node_available:
            logger.warning("Local IPFS node not available, cannot get file info")
            return None

        try:
            response = requests.post(
                f"{self.api_url}object/stat",
                params={'arg': ipfs_hash},
                timeout=30
            )

            if response.status_code == 200:
                info = response.json()
                logger.info(f"File info retrieved: {ipfs_hash}")
                return info
            else:
                logger.error(f"Failed to get file info: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None

# Singleton instance
_ipfs_service_instance = None

def get_ipfs_service() -> IPFSService:
    """Get singleton IPFS service instance"""
    global _ipfs_service_instance
    if _ipfs_service_instance is None:
        _ipfs_service_instance = IPFSService()
    return _ipfs_service_instance