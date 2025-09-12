export interface User {
  id: string;
  email: string;
  name: string;
  walletAddress?: string;
  authMethod: 'traditional' | 'wallet';
  isKycVerified: boolean;
  kycStatus: 'pending' | 'approved' | 'rejected' | 'not_started' | 'in_review';
  reputationScore: number;
  tokenBalance: number;
  createdAt: string;
  skills: string[];
  location?: string;
  bio?: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  walletConnected: boolean;
  walletAddress?: string;
}

export interface LoginCredentials {
  email?: string;
  password?: string;
  walletAddress?: string;
  signature?: string;
  message?: string;
  authMethod: 'traditional' | 'wallet';
}

export interface RegisterData {
  email?: string;
  password?: string;
  name: string;
  location?: string;
  bio?: string;
  skills: string[];
  walletAddress?: string;
  authMethod: 'traditional' | 'wallet';
}

export interface KycData {
  date_of_birth: string;
  nationality: string;
  phone_number: string;
  id_document_type: 'passport' | 'national_id' | 'drivers_license';
  id_document_number: string;
  id_document_front_url: string;
  id_document_back_url?: string;
  selfie_url: string;
  address_street: string;
  address_city: string;
  address_state?: string;
  address_country: string;
  address_postal_code: string;
  address_proof_url?: string;
}

export interface KycStatus {
  user_id: number;
  kyc_status: 'pending' | 'approved' | 'rejected' | 'in_review';
  kyc_submitted_at?: string;
  kyc_verified_at?: string;
  kyc_rejection_reason?: string;
  is_kyc_complete: boolean;
  is_kyc_pending: boolean;
}