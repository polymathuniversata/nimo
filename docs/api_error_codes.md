# Nimo Platform - API Error Code Reference

## Overview

This document provides a comprehensive reference for all error codes, HTTP status codes, and error handling patterns used in the Nimo Platform API. Understanding these codes will help developers implement robust error handling and provide better user experiences.

## Error Response Format

All API errors follow a consistent JSON format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "specific_field_name",
      "value": "invalid_value",
      "constraint": "validation_rule_violated",
      "suggestion": "How to fix this error"
    },
    "timestamp": "2025-08-27T10:30:00Z",
    "path": "/api/endpoint/that/failed",
    "request_id": "req_1234567890abcdef"
  }
}
```

## HTTP Status Code Categories

### 2xx - Success
- **200 OK**: Request succeeded
- **201 Created**: Resource created successfully
- **204 No Content**: Request succeeded, no content to return

### 4xx - Client Errors
- **400 Bad Request**: Invalid request format or parameters
- **401 Unauthorized**: Authentication required or invalid
- **403 Forbidden**: Valid authentication but insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource conflict (e.g., duplicate creation)
- **422 Unprocessable Entity**: Valid request but semantic errors
- **429 Too Many Requests**: Rate limit exceeded

### 5xx - Server Errors
- **500 Internal Server Error**: Unexpected server error
- **502 Bad Gateway**: Upstream service error
- **503 Service Unavailable**: Service temporarily unavailable

## Authentication & Authorization Errors

### AUTH_001 - INVALID_CREDENTIALS
```json
{
  "error": {
    "code": "AUTH_001",
    "message": "Invalid email or password",
    "details": {
      "suggestion": "Check your email and password and try again"
    }
  }
}
```
- **HTTP Status**: 401
- **Cause**: Incorrect email/password combination
- **Resolution**: Verify credentials or use password reset

### AUTH_002 - TOKEN_EXPIRED
```json
{
  "error": {
    "code": "AUTH_002", 
    "message": "Authentication token has expired",
    "details": {
      "expired_at": "2025-08-27T09:30:00Z",
      "suggestion": "Refresh your token or log in again"
    }
  }
}
```
- **HTTP Status**: 401
- **Cause**: JWT token has expired
- **Resolution**: Use refresh token or re-authenticate

### AUTH_003 - TOKEN_INVALID
```json
{
  "error": {
    "code": "AUTH_003",
    "message": "Authentication token is invalid or malformed",
    "details": {
      "suggestion": "Log in again to get a new token"
    }
  }
}
```
- **HTTP Status**: 401
- **Cause**: Malformed, tampered, or invalid JWT token
- **Resolution**: Re-authenticate to get new token

### AUTH_004 - INSUFFICIENT_PERMISSIONS
```json
{
  "error": {
    "code": "AUTH_004",
    "message": "Insufficient permissions to access this resource",
    "details": {
      "required_role": "admin",
      "user_role": "user",
      "suggestion": "Contact an administrator for access"
    }
  }
}
```
- **HTTP Status**: 403
- **Cause**: User lacks required permissions
- **Resolution**: Request elevated permissions or use authorized account

### AUTH_005 - ACCOUNT_DISABLED
```json
{
  "error": {
    "code": "AUTH_005",
    "message": "User account has been disabled",
    "details": {
      "disabled_at": "2025-08-20T15:30:00Z",
      "reason": "Terms of service violation",
      "suggestion": "Contact support for account reactivation"
    }
  }
}
```
- **HTTP Status**: 403
- **Cause**: Account suspended or banned
- **Resolution**: Contact support

## User Management Errors

### USER_001 - USER_NOT_FOUND
```json
{
  "error": {
    "code": "USER_001",
    "message": "User not found",
    "details": {
      "user_id": "12345",
      "suggestion": "Verify the user ID is correct"
    }
  }
}
```
- **HTTP Status**: 404
- **Cause**: Requested user doesn't exist
- **Resolution**: Check user ID or create user first

### USER_002 - DUPLICATE_EMAIL
```json
{
  "error": {
    "code": "USER_002",
    "message": "Email address already registered",
    "details": {
      "email": "user@example.com",
      "suggestion": "Use a different email or try logging in"
    }
  }
}
```
- **HTTP Status**: 409
- **Cause**: Email already exists in system
- **Resolution**: Use different email or login with existing account

### USER_003 - INVALID_EMAIL_FORMAT
```json
{
  "error": {
    "code": "USER_003",
    "message": "Invalid email address format",
    "details": {
      "field": "email",
      "value": "invalid-email",
      "constraint": "Must be valid email format",
      "suggestion": "Enter a valid email address"
    }
  }
}
```
- **HTTP Status**: 422
- **Cause**: Malformed email address
- **Resolution**: Provide valid email format

### USER_004 - WEAK_PASSWORD
```json
{
  "error": {
    "code": "USER_004",
    "message": "Password does not meet security requirements",
    "details": {
      "field": "password",
      "requirements": [
        "At least 8 characters",
        "One uppercase letter",
        "One lowercase letter", 
        "One number",
        "One special character"
      ],
      "suggestion": "Choose a stronger password"
    }
  }
}
```
- **HTTP Status**: 422
- **Cause**: Password doesn't meet complexity requirements
- **Resolution**: Use stronger password meeting all requirements

### USER_005 - PROFILE_UPDATE_FAILED
```json
{
  "error": {
    "code": "USER_005",
    "message": "Failed to update user profile",
    "details": {
      "failed_fields": ["bio", "location"],
      "suggestion": "Check field values and try again"
    }
  }
}
```
- **HTTP Status**: 422
- **Cause**: Invalid profile data
- **Resolution**: Fix validation errors and retry

## Contribution Management Errors

### CONTRIB_001 - CONTRIBUTION_NOT_FOUND
```json
{
  "error": {
    "code": "CONTRIB_001",
    "message": "Contribution not found",
    "details": {
      "contribution_id": "contrib_123",
      "suggestion": "Verify the contribution ID is correct"
    }
  }
}
```
- **HTTP Status**: 404
- **Cause**: Contribution doesn't exist
- **Resolution**: Check contribution ID

### CONTRIB_002 - INVALID_EVIDENCE_URL
```json
{
  "error": {
    "code": "CONTRIB_002",
    "message": "Invalid evidence URL provided",
    "details": {
      "field": "evidence_url",
      "value": "invalid-url",
      "constraint": "Must be valid HTTP/HTTPS URL",
      "suggestion": "Provide a valid URL starting with http:// or https://"
    }
  }
}
```
- **HTTP Status**: 422
- **Cause**: Malformed URL in evidence field
- **Resolution**: Provide valid URL

### CONTRIB_003 - CONTRIBUTION_ALREADY_VERIFIED
```json
{
  "error": {
    "code": "CONTRIB_003",
    "message": "Contribution has already been verified",
    "details": {
      "contribution_id": "contrib_123",
      "verified_at": "2025-08-25T14:30:00Z",
      "suggestion": "Cannot re-verify an already verified contribution"
    }
  }
}
```
- **HTTP Status**: 409
- **Cause**: Attempting to verify already verified contribution
- **Resolution**: Contribution is already verified

### CONTRIB_004 - INSUFFICIENT_EVIDENCE
```json
{
  "error": {
    "code": "CONTRIB_004", 
    "message": "Insufficient evidence for contribution verification",
    "details": {
      "missing_fields": ["description", "evidence_url"],
      "suggestion": "Provide more detailed evidence of your contribution"
    }
  }
}
```
- **HTTP Status**: 422
- **Cause**: Missing required evidence data
- **Resolution**: Add required evidence fields

### CONTRIB_005 - VERIFICATION_FAILED
```json
{
  "error": {
    "code": "CONTRIB_005",
    "message": "Contribution verification failed",
    "details": {
      "reason": "Evidence does not support claimed contribution",
      "confidence_score": 0.3,
      "metta_result": "low_confidence",
      "suggestion": "Provide stronger evidence or clarify contribution details"
    }
  }
}
```
- **HTTP Status**: 422
- **Cause**: MeTTa verification failed
- **Resolution**: Improve evidence quality

## Token Management Errors

### TOKEN_001 - INSUFFICIENT_BALANCE
```json
{
  "error": {
    "code": "TOKEN_001",
    "message": "Insufficient token balance",
    "details": {
      "required": 100,
      "available": 50,
      "suggestion": "Earn more tokens through verified contributions"
    }
  }
}
```
- **HTTP Status**: 422
- **Cause**: Not enough tokens for operation
- **Resolution**: Earn more tokens

### TOKEN_002 - INVALID_AMOUNT
```json
{
  "error": {
    "code": "TOKEN_002",
    "message": "Invalid token amount specified",
    "details": {
      "field": "amount",
      "value": -10,
      "constraint": "Must be positive number",
      "suggestion": "Specify a positive token amount"
    }
  }
}
```
- **HTTP Status**: 422
- **Cause**: Negative or zero token amount
- **Resolution**: Use positive number

### TOKEN_003 - TRANSFER_FAILED
```json
{
  "error": {
    "code": "TOKEN_003",
    "message": "Token transfer failed",
    "details": {
      "transaction_hash": "0xabc123...",
      "reason": "Transaction reverted",
      "suggestion": "Check blockchain transaction for details"
    }
  }
}
```
- **HTTP Status**: 500
- **Cause**: Blockchain transaction failed
- **Resolution**: Check blockchain status and retry

## Blockchain Integration Errors

### BLOCKCHAIN_001 - CONNECTION_FAILED
```json
{
  "error": {
    "code": "BLOCKCHAIN_001",
    "message": "Failed to connect to blockchain network",
    "details": {
      "network": "base-sepolia",
      "rpc_url": "https://sepolia.base.org",
      "suggestion": "Try again in a few minutes"
    }
  }
}
```
- **HTTP Status**: 502
- **Cause**: Blockchain RPC unavailable
- **Resolution**: Retry after network recovers

### BLOCKCHAIN_002 - INVALID_ADDRESS
```json
{
  "error": {
    "code": "BLOCKCHAIN_002",
    "message": "Invalid blockchain address",
    "details": {
      "field": "wallet_address",
      "value": "invalid-address",
      "constraint": "Must be valid Ethereum address",
      "suggestion": "Provide a valid Ethereum address starting with 0x"
    }
  }
}
```
- **HTTP Status**: 422
- **Cause**: Malformed Ethereum address
- **Resolution**: Use valid Ethereum address format

### BLOCKCHAIN_003 - TRANSACTION_TIMEOUT
```json
{
  "error": {
    "code": "BLOCKCHAIN_003",
    "message": "Blockchain transaction timed out",
    "details": {
      "transaction_hash": "0xdef456...",
      "timeout_seconds": 300,
      "suggestion": "Check transaction status on block explorer"
    }
  }
}
```
- **HTTP Status**: 408
- **Cause**: Transaction took too long to confirm
- **Resolution**: Check transaction status manually

### BLOCKCHAIN_004 - GAS_ESTIMATION_FAILED
```json
{
  "error": {
    "code": "BLOCKCHAIN_004",
    "message": "Failed to estimate gas for transaction",
    "details": {
      "reason": "Contract execution would fail",
      "suggestion": "Check contract state and parameters"
    }
  }
}
```
- **HTTP Status**: 422
- **Cause**: Transaction would fail during execution
- **Resolution**: Verify transaction parameters

## MeTTa AI Integration Errors

### METTA_001 - SERVICE_UNAVAILABLE
```json
{
  "error": {
    "code": "METTA_001",
    "message": "MeTTa reasoning service is unavailable",
    "details": {
      "service_status": "down",
      "suggestion": "Try again later or contact support"
    }
  }
}
```
- **HTTP Status**: 503
- **Cause**: MeTTa service is down
- **Resolution**: Wait for service recovery

### METTA_002 - REASONING_FAILED
```json
{
  "error": {
    "code": "METTA_002",
    "message": "MeTTa reasoning process failed",
    "details": {
      "query": "!(verify-contribution ...)",
      "error": "Invalid syntax in reasoning query",
      "suggestion": "Contact support if this persists"
    }
  }
}
```
- **HTTP Status**: 500
- **Cause**: MeTTa query execution failed
- **Resolution**: Report to developers

### METTA_003 - TIMEOUT
```json
{
  "error": {
    "code": "METTA_003",
    "message": "MeTTa reasoning timed out",
    "details": {
      "timeout_seconds": 30,
      "suggestion": "Try a simpler verification request"
    }
  }
}
```
- **HTTP Status**: 408
- **Cause**: MeTTa processing took too long
- **Resolution**: Simplify request or retry later

## Rate Limiting Errors

### RATE_001 - LIMIT_EXCEEDED
```json
{
  "error": {
    "code": "RATE_001", 
    "message": "Rate limit exceeded",
    "details": {
      "limit": 60,
      "window": 60,
      "reset_time": 1692123456,
      "suggestion": "Wait 30 seconds before making another request"
    }
  }
}
```
- **HTTP Status**: 429
- **Cause**: Too many requests in time window
- **Resolution**: Wait for rate limit reset

### RATE_002 - QUOTA_EXCEEDED
```json
{
  "error": {
    "code": "RATE_002",
    "message": "Monthly quota exceeded",
    "details": {
      "monthly_limit": 100000,
      "used": 100000,
      "reset_date": "2025-09-01",
      "suggestion": "Upgrade your plan or wait for quota reset"
    }
  }
}
```
- **HTTP Status**: 429
- **Cause**: Monthly request quota reached
- **Resolution**: Upgrade plan or wait for reset

## Validation Errors

### VALID_001 - REQUIRED_FIELD_MISSING
```json
{
  "error": {
    "code": "VALID_001",
    "message": "Required field is missing",
    "details": {
      "field": "title",
      "suggestion": "Provide a title for your contribution"
    }
  }
}
```
- **HTTP Status**: 422
- **Cause**: Required field not provided
- **Resolution**: Add missing field

### VALID_002 - FIELD_TOO_LONG
```json
{
  "error": {
    "code": "VALID_002",
    "message": "Field value exceeds maximum length",
    "details": {
      "field": "description",
      "max_length": 1000,
      "current_length": 1250,
      "suggestion": "Shorten your description to 1000 characters or less"
    }
  }
}
```
- **HTTP Status**: 422
- **Cause**: Field value too long
- **Resolution**: Shorten field value

### VALID_003 - INVALID_FORMAT
```json
{
  "error": {
    "code": "VALID_003",
    "message": "Invalid field format",
    "details": {
      "field": "phone_number",
      "format": "+1234567890",
      "suggestion": "Use international format: +1234567890"
    }
  }
}
```
- **HTTP Status**: 422
- **Cause**: Field doesn't match required format
- **Resolution**: Use correct format

## System Errors

### SYS_001 - DATABASE_CONNECTION_FAILED
```json
{
  "error": {
    "code": "SYS_001",
    "message": "Database connection failed",
    "details": {
      "suggestion": "Please try again in a few minutes"
    }
  }
}
```
- **HTTP Status**: 503
- **Cause**: Database is unavailable
- **Resolution**: Retry after database recovers

### SYS_002 - INTERNAL_SERVER_ERROR
```json
{
  "error": {
    "code": "SYS_002",
    "message": "Internal server error occurred",
    "details": {
      "error_id": "err_1234567890",
      "suggestion": "Contact support with error ID if this persists"
    }
  }
}
```
- **HTTP Status**: 500
- **Cause**: Unexpected server error
- **Resolution**: Contact support with error ID

### SYS_003 - MAINTENANCE_MODE
```json
{
  "error": {
    "code": "SYS_003",
    "message": "Service is currently under maintenance",
    "details": {
      "maintenance_end": "2025-08-27T12:00:00Z",
      "suggestion": "Please try again after maintenance window"
    }
  }
}
```
- **HTTP Status**: 503
- **Cause**: Scheduled maintenance
- **Resolution**: Wait for maintenance to complete

## Bond Management Errors

### BOND_001 - BOND_NOT_FOUND
```json
{
  "error": {
    "code": "BOND_001",
    "message": "Impact bond not found",
    "details": {
      "bond_id": "bond_123",
      "suggestion": "Verify the bond ID is correct"
    }
  }
}
```
- **HTTP Status**: 404
- **Cause**: Bond doesn't exist
- **Resolution**: Check bond ID

### BOND_002 - INSUFFICIENT_FUNDS_FOR_INVESTMENT
```json
{
  "error": {
    "code": "BOND_002",
    "message": "Insufficient funds for bond investment",
    "details": {
      "required": 1000,
      "available": 500,
      "suggestion": "Add more funds to your wallet"
    }
  }
}
```
- **HTTP Status**: 422
- **Cause**: Not enough tokens to invest
- **Resolution**: Add more funds

### BOND_003 - BOND_TARGET_REACHED
```json
{
  "error": {
    "code": "BOND_003",
    "message": "Bond has already reached its target amount",
    "details": {
      "target_amount": 10000,
      "current_amount": 10000,
      "suggestion": "This bond is fully funded"
    }
  }
}
```
- **HTTP Status**: 409
- **Cause**: Bond is fully funded
- **Resolution**: Choose different bond

## Error Handling Best Practices

### Client-Side Error Handling

```javascript
async function handleApiCall(apiFunction) {
  try {
    const response = await apiFunction();
    return response.data;
  } catch (error) {
    if (error.response) {
      const { code, message, details } = error.response.data.error;
      
      switch (code) {
        case 'AUTH_002': // Token expired
          await refreshToken();
          return handleApiCall(apiFunction); // Retry
          
        case 'RATE_001': // Rate limited
          const waitTime = details.reset_time - Date.now() / 1000;
          await new Promise(resolve => setTimeout(resolve, waitTime * 1000));
          return handleApiCall(apiFunction); // Retry
          
        case 'USER_002': // Duplicate email
          showError('Email already registered. Try logging in instead.');
          break;
          
        default:
          showError(message || 'An unexpected error occurred');
      }
    } else {
      showError('Network error. Please check your connection.');
    }
    throw error;
  }
}
```

### Server-Side Error Response Creation

```python
def create_error_response(code, message, details=None, status_code=400):
    """Create standardized error response"""
    error_response = {
        "error": {
            "code": code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": request.path,
            "request_id": request.headers.get('X-Request-ID', 'unknown')
        }
    }
    
    if details:
        error_response["error"]["details"] = details
        
    return jsonify(error_response), status_code

# Usage example
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not data.get('email'):
        return create_error_response(
            code="VALID_001",
            message="Required field is missing",
            details={
                "field": "email",
                "suggestion": "Provide an email address"
            },
            status_code=422
        )
    
    if User.query.filter_by(email=data['email']).first():
        return create_error_response(
            code="USER_002", 
            message="Email address already registered",
            details={
                "email": data['email'],
                "suggestion": "Use a different email or try logging in"
            },
            status_code=409
        )
```

## Monitoring and Analytics

### Error Tracking Metrics

Track these metrics for error monitoring:

1. **Error Rate by Endpoint**
   - Track error rates for each API endpoint
   - Alert when error rates exceed thresholds

2. **Error Code Distribution**
   - Monitor frequency of each error code
   - Identify most common error patterns

3. **User Experience Impact**
   - Track errors that affect user workflows
   - Prioritize fixes based on user impact

### Error Logging Format

```python
import logging
import json

def log_error(error_code, message, details=None, user_id=None):
    """Log error in structured format"""
    log_data = {
        "error_code": error_code,
        "message": message,
        "user_id": user_id,
        "request_id": request.headers.get('X-Request-ID'),
        "endpoint": request.path,
        "method": request.method,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details or {}
    }
    
    logging.error(json.dumps(log_data))
```

## Support and Troubleshooting

### Common Resolution Steps

1. **Authentication Issues**
   - Clear local storage/cookies
   - Re-login to get fresh token
   - Check API key validity

2. **Rate Limiting**
   - Implement exponential backoff
   - Check rate limit headers
   - Consider upgrading plan

3. **Validation Errors**
   - Review API documentation
   - Validate input client-side
   - Use proper data types

4. **Network Errors**
   - Check internet connection
   - Verify API endpoint URLs
   - Check for maintenance windows

### Getting Support

- **Documentation**: Review this error reference
- **Status Page**: https://status.nimo-platform.com  
- **Support Email**: support@nimo-platform.com
- **Developer Discord**: https://discord.gg/nimo-dev

Include error codes and request IDs when contacting support for faster resolution.

---

**Last Updated**: August 2025  
**Version**: 1.0  
**Next Review**: September 2025