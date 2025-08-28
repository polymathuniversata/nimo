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
  contribution_type: string;
  impact_level: 'low' | 'moderate' | 'significant' | 'transformative';
  created_at: string;
  user_id: number;
  wallet_address: string | null;
  evidence: {
    type: string;
    url: string;
  };
  metta_processing?: boolean;
  metta_confidence?: number;
  verifications?: Verification[];
}

// Types for Bond
interface Milestone {
  id: string;
  title: string;
  target_amount: number;
  completed: boolean;
}

interface Bond {
  id: string;
  title: string;
  description: string;
  value: number;
  cause: string;
  status: string;
  milestones?: Milestone[];
}

// Types for NFT
interface NFTData {
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
  Milestone,
  NFTData,
  WalletConnectionProps
};
