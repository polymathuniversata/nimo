"""
MeTTa Security Utilities for Nimo Platform

This module provides security utilities for safe MeTTa query construction
and input sanitization to prevent MeTTa injection attacks.

Security principles:
1. All user inputs must be sanitized before inclusion in MeTTa queries
2. String literals must be properly escaped
3. Only whitelisted characters and patterns allowed
4. Length limits enforced on all inputs
"""

import re
import html
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse


class MeTTaSecurityError(Exception):
    """Exception raised for MeTTa security violations"""
    pass


class MeTTaSanitizer:
    """Secure input sanitization for MeTTa queries"""
    
    # Whitelisted characters for different input types
    SAFE_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,64}$')
    SAFE_SKILL_PATTERN = re.compile(r'^[a-zA-Z0-9_\s-]{1,50}$')
    SAFE_CATEGORY_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,30}$')
    SAFE_IMPACT_PATTERN = re.compile(r'^(minimal|moderate|significant|transformative)$')
    
    # Maximum lengths for different input types
    MAX_LENGTHS = {
        'id': 64,
        'username': 50,
        'title': 200,
        'description': 1000,
        'skill': 50,
        'category': 30,
        'url': 2048,
        'hash': 66  # 0x + 64 hex chars
    }
    
    @classmethod
    def sanitize_id(cls, value: str, field_name: str = "id") -> str:
        """
        Sanitize ID values (user IDs, contribution IDs, etc.)
        
        Args:
            value: Raw input value
            field_name: Name of the field for error reporting
            
        Returns:
            Sanitized ID string
            
        Raises:
            MeTTaSecurityError: If input is invalid
        """
        if not isinstance(value, str):
            raise MeTTaSecurityError(f"{field_name} must be a string")
        
        if len(value) > cls.MAX_LENGTHS['id']:
            raise MeTTaSecurityError(f"{field_name} exceeds maximum length")
        
        if not cls.SAFE_ID_PATTERN.match(value):
            raise MeTTaSecurityError(f"{field_name} contains invalid characters")
        
        return value
    
    @classmethod
    def sanitize_skill(cls, value: str) -> str:
        """
        Sanitize skill names
        
        Args:
            value: Raw skill name
            
        Returns:
            Sanitized skill name
            
        Raises:
            MeTTaSecurityError: If input is invalid
        """
        if not isinstance(value, str):
            raise MeTTaSecurityError("Skill must be a string")
        
        if len(value) > cls.MAX_LENGTHS['skill']:
            raise MeTTaSecurityError("Skill name exceeds maximum length")
        
        if not cls.SAFE_SKILL_PATTERN.match(value):
            raise MeTTaSecurityError("Skill name contains invalid characters")
        
        return value.strip().lower()
    
    @classmethod
    def sanitize_category(cls, value: str) -> str:
        """
        Sanitize contribution categories
        
        Args:
            value: Raw category value
            
        Returns:
            Sanitized category
            
        Raises:
            MeTTaSecurityError: If input is invalid
        """
        if not isinstance(value, str):
            raise MeTTaSecurityError("Category must be a string")
        
        if len(value) > cls.MAX_LENGTHS['category']:
            raise MeTTaSecurityError("Category exceeds maximum length")
        
        if not cls.SAFE_CATEGORY_PATTERN.match(value):
            raise MeTTaSecurityError("Category contains invalid characters")
        
        return value.lower()
    
    @classmethod
    def sanitize_impact_level(cls, value: str) -> str:
        """
        Sanitize impact level values
        
        Args:
            value: Raw impact level
            
        Returns:
            Sanitized impact level
            
        Raises:
            MeTTaSecurityError: If input is invalid
        """
        if not isinstance(value, str):
            raise MeTTaSecurityError("Impact level must be a string")
        
        value = value.lower().strip()
        
        if not cls.SAFE_IMPACT_PATTERN.match(value):
            raise MeTTaSecurityError("Invalid impact level")
        
        return value
    
    @classmethod
    def sanitize_url(cls, value: str) -> str:
        """
        Sanitize and validate URLs
        
        Args:
            value: Raw URL
            
        Returns:
            Sanitized URL
            
        Raises:
            MeTTaSecurityError: If URL is invalid
        """
        if not isinstance(value, str):
            raise MeTTaSecurityError("URL must be a string")
        
        if len(value) > cls.MAX_LENGTHS['url']:
            raise MeTTaSecurityError("URL exceeds maximum length")
        
        try:
            parsed = urlparse(value)
            if not parsed.scheme or not parsed.netloc:
                raise MeTTaSecurityError("Invalid URL format")
            
            if parsed.scheme not in ['http', 'https', 'ipfs']:
                raise MeTTaSecurityError("Unsupported URL scheme")
            
        except Exception as e:
            raise MeTTaSecurityError(f"URL validation failed: {str(e)}")
        
        return value
    
    @classmethod
    def sanitize_string(cls, value: str, field_name: str, max_length: int = 1000) -> str:
        """
        General string sanitization with length limits and HTML escaping
        
        Args:
            value: Raw string value
            field_name: Name of the field for error reporting
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
            
        Raises:
            MeTTaSecurityError: If input is invalid
        """
        if not isinstance(value, str):
            raise MeTTaSecurityError(f"{field_name} must be a string")
        
        if len(value) > max_length:
            raise MeTTaSecurityError(f"{field_name} exceeds maximum length ({max_length})")
        
        # HTML escape to prevent XSS
        sanitized = html.escape(value.strip())
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\'\\\x00-\x1f\x7f-\x9f]', '', sanitized)
        
        return sanitized
    
    @classmethod
    def escape_metta_string(cls, value: str) -> str:
        """
        Escape string for safe inclusion in MeTTa queries
        
        Args:
            value: String to escape
            
        Returns:
            Escaped string safe for MeTTa queries
        """
        if not isinstance(value, str):
            return str(value)
        
        # Escape quotes and backslashes for MeTTa string literals
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        
        # Remove control characters
        escaped = re.sub(r'[\x00-\x1f\x7f]', '', escaped)
        
        return escaped
    
    @classmethod
    def validate_metadata(cls, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize metadata dictionary
        
        Args:
            metadata: Raw metadata dictionary
            
        Returns:
            Sanitized metadata dictionary
            
        Raises:
            MeTTaSecurityError: If metadata is invalid
        """
        if not isinstance(metadata, dict):
            raise MeTTaSecurityError("Metadata must be a dictionary")
        
        sanitized = {}
        
        # Validate specific known fields
        if 'impact' in metadata:
            sanitized['impact'] = cls.sanitize_impact_level(metadata['impact'])
        
        if 'skills' in metadata:
            if not isinstance(metadata['skills'], list):
                raise MeTTaSecurityError("Skills must be a list")
            
            sanitized['skills'] = []
            for skill in metadata['skills']:
                sanitized['skills'].append(cls.sanitize_skill(skill))
        
        # Limit total metadata size
        total_size = len(str(sanitized))
        if total_size > 10000:  # 10KB limit
            raise MeTTaSecurityError("Metadata exceeds size limit")
        
        return sanitized


def create_safe_metta_atom(template: str, **kwargs) -> str:
    """
    Create a safe MeTTa atom with sanitized parameters
    
    Args:
        template: MeTTa atom template with {param} placeholders
        **kwargs: Parameters to substitute in template
        
    Returns:
        Safe MeTTa atom string
        
    Raises:
        MeTTaSecurityError: If any parameter is invalid
    """
    sanitized_kwargs = {}
    
    for key, value in kwargs.items():
        if isinstance(value, str):
            sanitized_kwargs[key] = MeTTaSanitizer.escape_metta_string(value)
        elif isinstance(value, (int, float)):
            sanitized_kwargs[key] = str(value)
        else:
            raise MeTTaSecurityError(f"Unsupported parameter type for {key}")
    
    try:
        return template.format(**sanitized_kwargs)
    except KeyError as e:
        raise MeTTaSecurityError(f"Missing template parameter: {e}")
    except Exception as e:
        raise MeTTaSecurityError(f"Template formatting error: {e}")


# Security audit utilities
class MeTTaAuditor:
    """Security auditing utilities for MeTTa operations"""
    
    @classmethod
    def audit_query(cls, query: str) -> Dict[str, Any]:
        """
        Audit a MeTTa query for security issues
        
        Args:
            query: MeTTa query string to audit
            
        Returns:
            Audit result dictionary
        """
        issues = []
        risk_level = "low"
        
        # Check for potential injection patterns
        if re.search(r'["\'].*\$.*["\']', query):
            issues.append("Potential variable injection in string literal")
            risk_level = "high"
        
        # Check for unescaped quotes
        if '""' in query or "''" in query:
            issues.append("Potential quote escaping issue")
            risk_level = "medium"
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'\$\w*\s*[=!<>]',  # Variable comparisons
            r'eval\s*\(',       # Eval functions
            r'exec\s*\(',       # Exec functions
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                issues.append(f"Suspicious pattern detected: {pattern}")
                risk_level = "high"
        
        return {
            "query": query,
            "risk_level": risk_level,
            "issues": issues,
            "safe": len(issues) == 0
        }