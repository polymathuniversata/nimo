// Types for Contribution
interface Verification {
  id?: number;
  verifier_name: string;
  organization?: string;
  comments?: string;
  confidence?: number;
  created_at?: string;
}

interface Contribution {
  id: number;
  title: string;
  description: string;
  status?: string;
  reward?: number;
  contribution_type?: string;
  impact_level?: string;
  created_at?: string;
  user_id?: number;
  wallet_address?: string;
  evidence?: Record<string, unknown>;
  verifications?: Array<Record<string, unknown>>;
  metta_processing?: boolean;
  metta_confidence?: number;
  metta_reasoning?: string;
}

// Types for Bond
interface Bond {
  id: number;
  name: string;
  description: string;
  yield: number;
  minInvestment: number;
  maturityDate: string;
  available: number;
  totalSupply: number;
  issuer: string;
}

// Types for Investment
interface Investment {
  id: number;
  name: string;
  description: string;
  yield: number;
  minInvestment: number;
  maturityDate: string;
  available: number;
  totalSupply: number;
  issuer: string;
  investmentAmount: number;
  investmentDate: string;
  expectedReturn: number;
}

// Types for NFT
interface NFTData {
  id: number;
  walletAddress: string;
  tokenBalance: number;
  verificationLevel: string;
  uniqueId: string;
  mintDate: string;
  reputation: number;
  specialties: string[];
  traits: {
    reputation: number;
    verificationLevel: string;
    joinDate: string;
    innovator_type: string;
    impact_focus: string;
    collaboration_score: number;
  };
}

// Legacy types (keeping for backward compatibility)
interface Milestone {
  id: string;
  title: string;
  target_amount: number;
  completed: boolean;
}

interface LegacyBond {
  id: string;
  title: string;
  description: string;
  value: number;
  cause: string;
  status: string;
  milestones?: Milestone[];
}

interface LegacyNFTData {
  id: string;
  address: string;
  reputation: number;
  verificationLevel: string;
  specialties: string[];
  mintDate: string;
  uniqueId: string;
  traits: {
    innovator_type: string;
    impact_focus: string;
    collaboration_score: number;
  };
  metadata?: {
    name: string;
    description: string;
    image: string;
  };
}

// Wallet Connection Props
interface WalletConnectionProps {
  onConnect: (address: string) => void;
  onDisconnect: () => void;
  isConnected: boolean;
  walletAddress: string | null;
}

export type {
  Contribution,
  Bond,
  Investment,
  NFTData,
  WalletConnectionProps,
  // Legacy types for backward compatibility
  Milestone,
  LegacyBond as BondLegacy,
  LegacyNFTData as NFTDataLegacy
};
