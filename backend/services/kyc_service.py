"""
KYC (Know Your Customer) service for Nimo platform
Handles KYC verification, document processing, and compliance checks
"""

import os
import requests
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from app import db
from models.user import User

class KYCService:
    """Service class for handling KYC operations"""

    # Required KYC fields
    REQUIRED_PERSONAL_FIELDS = [
        'date_of_birth', 'nationality', 'phone_number'
    ]

    REQUIRED_DOCUMENT_FIELDS = [
        'id_document_type', 'id_document_number',
        'id_document_front_url', 'selfie_url'
    ]

    REQUIRED_ADDRESS_FIELDS = [
        'address_street', 'address_city',
        'address_country', 'address_postal_code'
    ]

    @staticmethod
    def validate_kyc_data(kyc_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate KYC data completeness and format
        Returns (is_valid, error_messages)
        """
        errors = []

        # Check personal information
        for field in KYCService.REQUIRED_PERSONAL_FIELDS:
            if field not in kyc_data or not kyc_data[field]:
                errors.append(f"Missing required field: {field}")

        # Check document information
        for field in KYCService.REQUIRED_DOCUMENT_FIELDS:
            if field not in kyc_data or not kyc_data[field]:
                errors.append(f"Missing required field: {field}")

        # Check address information
        for field in KYCService.REQUIRED_ADDRESS_FIELDS:
            if field not in kyc_data or not kyc_data[field]:
                errors.append(f"Missing required field: {field}")

        # Validate date of birth
        if 'date_of_birth' in kyc_data and kyc_data['date_of_birth']:
            try:
                dob = date.fromisoformat(kyc_data['date_of_birth'])
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                if age < 18:
                    errors.append("User must be at least 18 years old")
            except ValueError:
                errors.append("Invalid date format for date_of_birth")

        # Validate phone number format (basic check)
        if 'phone_number' in kyc_data and kyc_data['phone_number']:
            phone = kyc_data['phone_number'].strip()
            if not phone.startswith('+') or len(phone) < 10:
                errors.append("Phone number must be in international format (+country_code)")

        # Validate document type
        valid_doc_types = ['passport', 'national_id', 'drivers_license']
        if 'id_document_type' in kyc_data and kyc_data['id_document_type']:
            if kyc_data['id_document_type'] not in valid_doc_types:
                errors.append(f"Invalid document type. Must be one of: {', '.join(valid_doc_types)}")

        return len(errors) == 0, errors

    @staticmethod
    def submit_kyc(user_id: int, kyc_data: Dict) -> Tuple[bool, str]:
        """
        Submit KYC information for a user
        Returns (success, message)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"

            # Validate KYC data
            is_valid, errors = KYCService.validate_kyc_data(kyc_data)
            if not is_valid:
                return False, f"KYC validation failed: {', '.join(errors)}"

            # Submit KYC
            user.submit_kyc(kyc_data)
            db.session.commit()

            return True, "KYC submitted successfully for review"

        except Exception as e:
            db.session.rollback()
            return False, f"Failed to submit KYC: {str(e)}"

    @staticmethod
    def approve_kyc(user_id: int, admin_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Approve KYC for a user
        Returns (success, message)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"

            if user.kyc_status != 'in_review':
                return False, f"Cannot approve KYC with status: {user.kyc_status}"

            user.approve_kyc()
            db.session.commit()

            return True, "KYC approved successfully"

        except Exception as e:
            db.session.rollback()
            return False, f"Failed to approve KYC: {str(e)}"

    @staticmethod
    def reject_kyc(user_id: int, reason: str, admin_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Reject KYC for a user
        Returns (success, message)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"

            if user.kyc_status != 'in_review':
                return False, f"Cannot reject KYC with status: {user.kyc_status}"

            if not reason or not reason.strip():
                return False, "Rejection reason is required"

            user.reject_kyc(reason.strip())
            db.session.commit()

            return True, "KYC rejected"

        except Exception as e:
            db.session.rollback()
            return False, f"Failed to reject KYC: {str(e)}"

    @staticmethod
    def get_kyc_status(user_id: int) -> Optional[Dict]:
        """
        Get KYC status for a user
        Returns user KYC information or None if user not found
        """
        user = User.query.get(user_id)
        if not user:
            return None

        return {
            'user_id': user.id,
            'kyc_status': user.kyc_status,
            'kyc_submitted_at': user.kyc_submitted_at.isoformat() if user.kyc_submitted_at else None,
            'kyc_verified_at': user.kyc_verified_at.isoformat() if user.kyc_verified_at else None,
            'kyc_rejection_reason': user.kyc_rejection_reason,
            'is_kyc_complete': user.is_kyc_complete(),
            'is_kyc_pending': user.is_kyc_pending()
        }

    @staticmethod
    def get_pending_kyc_submissions() -> List[Dict]:
        """
        Get all pending KYC submissions for admin review
        """
        users = User.query.filter_by(kyc_status='in_review').all()

        return [{
            'user_id': user.id,
            'email': user.email,
            'name': user.name,
            'kyc_submitted_at': user.kyc_submitted_at.isoformat() if user.kyc_submitted_at else None,
            'id_document_type': user.id_document_type,
            'nationality': user.nationality
        } for user in users]

    @staticmethod
    def check_user_eligibility(user_id: int) -> Tuple[bool, str]:
        """
        Check if user is eligible for platform features
        Returns (is_eligible, reason)
        """
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"

        # Check if user has wallet connected
        if not user.wallet_address:
            return False, "Wallet connection required"

        # Check KYC status
        if not user.is_kyc_complete():
            if user.kyc_status == 'rejected':
                return False, f"KYC rejected: {user.kyc_rejection_reason or 'No reason provided'}"
            elif user.kyc_status == 'pending':
                return False, "KYC submission required"
            elif user.kyc_status == 'in_review':
                return False, "KYC under review"
            else:
                return False, "KYC verification required"

        return True, "User is eligible"