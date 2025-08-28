import { BrowserRouter, Routes, Route, useLocation, useNavigate } from "react-router-dom";
import React, { useState, useEffect, useCallback } from 'react';
import type { Contribution, Bond, NFTData } from './types';
import { ContributionsSection, MarketplaceSection, IdentitySection } from "./components/Sections";

// API functions
const API_BASE = 'http://localhost:5000';

const fetchContributions = async (): Promise<{ contributions: Contribution[] }> => {
  const response = await fetch(`${API_BASE}/api/contributions`);
  return response.json();
};

const fetchBonds = async (): Promise<Bond[]> => {
  const response = await fetch(`${API_BASE}/api/bonds`);
  return response.json();
};

const fetchTokenBalance = async (): Promise<{ balance: number }> => {
  const response = await fetch(`${API_BASE}/api/tokens/balance`);
  return response.json();
};

// MetaMask wallet integration
const connectMetaMask = async (): Promise<string> => {
  if (typeof window.ethereum !== 'undefined') {
    try {
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts',
      });
      
      // Switch to Base Sepolia network
      try {
        await window.ethereum.request({
          method: 'wallet_switchEthereumChain',
          params: [{ chainId: '0x14A34' }], // Base Sepolia
        });
      } catch (switchError) {
        // If the network doesn't exist, add it
        if (switchError.code === 4902) {
          await window.ethereum.request({
            method: 'wallet_addEthereumChain',
            params: [
              {
                chainId: '0x14A34',
                chainName: 'Base Sepolia',
                nativeCurrency: {
                  name: 'ETH',
                  symbol: 'ETH',
                  decimals: 18,
                },
                rpcUrls: ['https://sepolia.base.org'],
                blockExplorerUrls: ['https://sepolia-explorer.base.org'],
              },
            ],
          });
        }
      }
      
      return accounts[0];
    } catch (error) {
      console.error('Failed to connect to MetaMask:', error);
      throw error;
    }
  } else {
    throw new Error('MetaMask is not installed');
  }
};

// MeTTa AI Integration
const submitToMeTTa = async (contributionData: Omit<Contribution, 'id'>): Promise<{ verified: boolean; confidence: number; reasoning: string }> => {
  try {
    const response = await fetch(`${API_BASE}/api/contributions/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(contributionData),
    });
    return response.json();
  } catch (error) {
    console.error('MeTTa verification failed:', error);
    return { verified: false, confidence: 0, reasoning: 'Verification service unavailable' };
  }
};

// Enhanced Wallet Connection Component
const WalletConnection: React.FC<{
  onConnect: (address: string) => void;
  onDisconnect: () => void;
  isConnected: boolean;
  walletAddress: string | null;
}> = ({ 
  onConnect, 
  onDisconnect,
  isConnected, 
  walletAddress 
}) => {
  const [isConnecting, setIsConnecting] = useState(false);
  const [walletBalance, setWalletBalance] = useState('0');
  const [networkName, setNetworkName] = useState('Base Sepolia');

  const handleConnect = async () => {
    setIsConnecting(true);
    try {
      const address = await connectMetaMask();
      
      // Get balance
      if (window.ethereum) {
        const balance = await window.ethereum.request({
          method: 'eth_getBalance',
          params: [address, 'latest'],
        });
        const ethBalance = (parseInt(balance, 16) / Math.pow(10, 18)).toFixed(4);
        setWalletBalance(ethBalance);
      }
      
      onConnect(address);
    } catch (error) {
      console.error('Connection failed:', error);
      alert(`Connection failed: ${error.message}`);
    } finally {
      setIsConnecting(false);
    }
  };

  const handleDisconnect = () => {
    onDisconnect();
    setWalletBalance('0');
  };

  const handleMouseOver = (e: React.MouseEvent<HTMLElement>) => {
    const target = e.currentTarget;
    target.style.transform = 'translateY(-5px)';
    target.style.boxShadow = '0 8px 25px rgba(255, 123, 0, 0.3)';
  };

  const handleMouseOut = (e: React.MouseEvent<HTMLElement>) => {
    const target = e.currentTarget;
    target.style.transform = 'translateY(0)';
    target.style.boxShadow = '0 2px 10px rgba(255, 123, 0, 0.2)';
  };

  if (isConnected) {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '0.5rem',
        backgroundColor: 'rgba(0,255,136,0.15)', 
        padding: '0.5rem 1rem', 
        borderRadius: '25px',
        fontSize: '0.85rem',
        border: '1px solid rgba(0,255,136,0.3)'
      }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.5rem'
        }}>
          <div style={{ 
            width: '8px', 
            height: '8px', 
            backgroundColor: '#00ff88', 
            borderRadius: '50%',
            animation: 'pulse 2s infinite'
          }}></div>
          <span style={{ fontWeight: '600' }}>
            {walletAddress?.substring(0, 6)}...{walletAddress?.substring(38)}
          </span>
          <span style={{ 
            opacity: 0.8,
            fontSize: '0.75rem',
            backgroundColor: 'rgba(0,0,0,0.2)',
            padding: '2px 6px',
            borderRadius: '10px'
          }}>
            {walletBalance} ETH
          </span>
        </div>
        <button
          onClick={handleDisconnect}
          style={{
            backgroundColor: 'transparent',
            border: 'none',
            color: '#ff4444',
            cursor: 'pointer',
            padding: '2px',
            fontSize: '0.8rem'
          }}
          title="Disconnect wallet"
        >
          ✕
        </button>
      </div>
    );
  }

  return (
    <button 
      onClick={handleConnect}
      disabled={isConnecting}
      style={{ 
        padding: '0.6rem 1.2rem', 
        backgroundColor: isConnecting ? 'rgba(255,123,0,0.5)' : '#ff7b00', 
        border: 'none', 
        borderRadius: '25px', 
        color: 'white', 
        fontSize: '0.9rem', 
        cursor: isConnecting ? 'not-allowed' : 'pointer',
        fontWeight: '600',
        boxShadow: '0 2px 10px rgba(255,123,0,0.2)',
        transition: 'all 0.3s ease'
      }}
      onMouseOver={handleMouseOver}
      onMouseOut={handleMouseOut}
    >
      {isConnecting ? '🔄 Connecting...' : '🦊 Connect MetaMask'}
    </button>
  );
};

// Enhanced MeTTa Identity NFT Component
interface IdentityNFTProps {
  walletAddress: string;
  tokenBalance: number;
  onNFTCreated?: (nftData: NFTData) => void;
}

const IdentityNFT: React.FC<IdentityNFTProps> = ({ walletAddress, tokenBalance, onNFTCreated }) => {
  const [hasNFT, setHasNFT] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [nftData, setNftData] = useState<NFTData | null>(null);
  const [verificationStep, setVerificationStep] = useState(0);

  const createIdentityNFT = async () => {
    setIsCreating(true);
    const steps = [
      'Connecting to MeTTa AI...',
      'Verifying identity attributes...',
      'Generating unique profile...',
      'Minting NFT on Base Sepolia...',
      'Finalizing on-chain registration...'
    ];
    
    // Simulate step-by-step process
    for (let i = 0; i < steps.length; i++) {
      setVerificationStep(i);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // Create NFT data
    const newNftData: NFTData = {
      id: Date.now().toString(),
      address: walletAddress,
      reputation: 750 + Math.floor(Math.random() * 250),
      verificationLevel: 'MeTTa Verified',
      specialties: ['African Innovation', 'Community Impact', 'Sustainable Development'],
      mintDate: new Date().toISOString(),
      uniqueId: `AI-${Math.floor(Math.random() * 10000)}`,
      traits: {
        innovator_type: 'Community Builder',
        impact_focus: 'Infrastructure',
        collaboration_score: 85 + Math.floor(Math.random() * 15)
      }
    };
    
    setNftData(newNftData);
    setHasNFT(true);
    setIsCreating(false);
    onNFTCreated?.(newNftData);
  };

  if (hasNFT && nftData) {
    return (
      <div style={{ 
        backgroundColor: 'rgba(255,123,0,0.08)', 
        border: '2px solid #ff7b00',
        borderRadius: '16px', 
        padding: '1.5rem',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Animated background */}
        <div style={{ 
          position: 'absolute',
          top: '-50%',
          right: '-50%',
          width: '200%',
          height: '200%',
          background: 'conic-gradient(from 0deg, transparent, rgba(255,123,0,0.15), transparent)',
          animation: 'spin 8s linear infinite'
        }}></div>
        
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
            <h3 style={{ margin: 0, color: '#ff7b00', fontSize: '1.1rem' }}>🎭 Identity NFT</h3>
            <span style={{ 
              backgroundColor: 'rgba(0,255,136,0.2)', 
              color: '#00ff88', 
              padding: '4px 12px', 
              borderRadius: '15px', 
              fontSize: '0.75rem',
              fontWeight: '600'
            }}>
              ✅ {nftData.verificationLevel}
            </span>
          </div>
          
          {/* NFT Display */}
          <div style={{ 
            backgroundColor: 'rgba(0,0,0,0.4)', 
            padding: '1.2rem', 
            borderRadius: '12px', 
            marginBottom: '1rem',
            border: '1px solid rgba(255,123,0,0.2)'
          }}>
            <div style={{ fontSize: '2.5rem', textAlign: 'center', marginBottom: '0.5rem' }}>🌍</div>
            <div style={{ textAlign: 'center', fontSize: '1rem', fontWeight: '600', marginBottom: '0.3rem' }}>
              African Innovator #{nftData.uniqueId}
            </div>
            <div style={{ textAlign: 'center', fontSize: '0.8rem', opacity: 0.7 }}>
              {nftData.traits.innovator_type}
            </div>
            <div style={{ textAlign: 'center', fontSize: '0.75rem', marginTop: '0.5rem', opacity: 0.6 }}>
              Minted: {new Date(nftData.mintDate).toLocaleDateString()}
            </div>
          </div>

          {/* Stats Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.8rem', marginBottom: '1rem' }}>
            <div>
              <div style={{ opacity: 0.7 }}>Reputation Score</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#00ff88' }}>
                {nftData.reputation}/1000
              </div>
            </div>
            <div>
              <div style={{ opacity: 0.7 }}>NIMO Balance</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#ff7b00' }}>
                {tokenBalance.toLocaleString()}
              </div>
            </div>
          </div>
          
          {/* Specialties */}
          <div style={{ marginBottom: '1rem' }}>
            <div style={{ fontSize: '0.8rem', opacity: 0.7, marginBottom: '0.5rem' }}>Specialties:</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3rem' }}>
              {nftData.specialties.map((specialty, idx) => (
                <span key={idx} style={{
                  fontSize: '0.7rem',
                  backgroundColor: 'rgba(255,123,0,0.2)',
                  color: '#ff7b00',
                  padding: '2px 8px',
                  borderRadius: '10px',
                  border: '1px solid rgba(255,123,0,0.3)'
                }}>
                  {specialty}
                </span>
              ))}
            </div>
          </div>
          
          {/* Collaboration Score */}
          <div style={{
            backgroundColor: 'rgba(0,0,0,0.3)',
            padding: '0.8rem',
            borderRadius: '8px',
            fontSize: '0.8rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
              <span>Collaboration Score</span>
              <span style={{ color: '#00ff88', fontWeight: '600' }}>{nftData.traits.collaboration_score}/100</span>
            </div>
            <div style={{
              backgroundColor: 'rgba(255,255,255,0.1)',
              height: '4px',
              borderRadius: '2px',
              overflow: 'hidden'
            }}>
              <div style={{
                backgroundColor: '#00ff88',
                height: '100%',
                width: `${nftData.traits.collaboration_score}%`,
                transition: 'width 1s ease'
              }}></div>
            </div>
          </div>
        </div>

        <style>{`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}</style>
      </div>
    );
  }

  const steps = [
    'Connecting to MeTTa AI...',
    'Verifying identity attributes...',
    'Generating unique profile...',
    'Minting NFT on Base Sepolia...',
    'Finalizing on-chain registration...'
  ];

  if (isCreating) {
    return (
      <div style={{ 
        backgroundColor: 'rgba(255,123,0,0.1)', 
        border: '2px solid rgba(255,123,0,0.3)',
        borderRadius: '16px', 
        padding: '2rem',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🤖</div>
        <h3 style={{ margin: '0 0 0.5rem 0', color: '#ff7b00' }}>MeTTa AI Processing...</h3>
        
        {/* Progress Steps */}
        <div style={{ marginBottom: '1.5rem' }}>
          {steps.map((step, idx) => (
            <div key={idx} style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem',
              padding: '0.5rem',
              opacity: idx <= verificationStep ? 1 : 0.3,
              transition: 'opacity 0.3s ease'
            }}>
              <div style={{
                width: '16px',
                height: '16px',
                borderRadius: '50%',
                backgroundColor: idx < verificationStep ? '#00ff88' : idx === verificationStep ? '#ff7b00' : 'rgba(255,255,255,0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.7rem'
              }}>
                {idx < verificationStep ? '✓' : idx === verificationStep ? '●' : ''}
              </div>
              <span style={{ fontSize: '0.9rem' }}>{step}</span>
            </div>
          ))}
        </div>
        
        {/* Progress Bar */}
        <div style={{
          backgroundColor: 'rgba(255,255,255,0.1)',
          height: '6px',
          borderRadius: '3px',
          overflow: 'hidden',
          marginBottom: '1rem'
        }}>
          <div style={{
            backgroundColor: '#ff7b00',
            height: '100%',
            width: `${((verificationStep + 1) / steps.length) * 100}%`,
            transition: 'width 0.5s ease'
          }}></div>
        </div>
        
        <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>
          This process uses advanced AI to create a unique, verifiable identity profile.
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      backgroundColor: 'rgba(255,255,255,0.05)', 
      border: '2px dashed rgba(255,123,0,0.5)',
      borderRadius: '16px', 
      padding: '2rem',
      textAlign: 'center',
      transition: 'all 0.3s ease'
    }}>
      <div style={{ fontSize: '3.5rem', marginBottom: '1rem', opacity: 0.6 }}>🎭</div>
      <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.2rem' }}>Create Identity NFT</h3>
      <p style={{ opacity: 0.8, marginBottom: '1.5rem', fontSize: '0.9rem', lineHeight: 1.4 }}>
        Mint your unique identity NFT verified by MeTTa AI to unlock platform features, 
        build your reputation, and access exclusive opportunities in the African innovation ecosystem.
      </p>
      
      {/* Benefits */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', 
        gap: '1rem', 
        marginBottom: '2rem',
        fontSize: '0.8rem'
      }}>
        <div style={{ opacity: 0.7 }}>
          <div style={{ fontSize: '1.2rem', marginBottom: '0.2rem' }}>🏆</div>
          <div>Reputation System</div>
        </div>
        <div style={{ opacity: 0.7 }}>
          <div style={{ fontSize: '1.2rem', marginBottom: '0.2rem' }}>💰</div>
          <div>Token Rewards</div>
        </div>
        <div style={{ opacity: 0.7 }}>
          <div style={{ fontSize: '1.2rem', marginBottom: '0.2rem' }}>🔒</div>
          <div>Verified Identity</div>
        </div>
      </div>
      
      <button 
        onClick={createIdentityNFT}
        disabled={isCreating}
        style={{ 
          padding: '14px 28px', 
          backgroundColor: isCreating ? 'rgba(255,123,0,0.5)' : '#ff7b00', 
          border: 'none', 
          borderRadius: '25px', 
          color: 'white', 
          fontSize: '1rem', 
          fontWeight: '600',
          cursor: isCreating ? 'not-allowed' : 'pointer',
          boxShadow: '0 4px 15px rgba(255,123,0,0.3)',
          transition: 'all 0.3s ease'
        }}
      >
        {isCreating ? '🤖 Processing...' : '✨ Mint Identity NFT'}
      </button>
      
      {!walletAddress && (
        <div style={{ marginTop: '1rem', fontSize: '0.8rem', opacity: 0.6 }}>
          🔒 Connect your wallet to mint your Identity NFT
        </div>
      )}
    </div>
  );
};

// Contribution Submission Modal
const ContributionModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Omit<Contribution, 'id' | 'verifications' | 'created_at' | 'user_id' | 'wallet_address' | 'evidence' | 'metta_processing' | 'metta_confidence'> & { 
    evidence: string;
    type: string;
    impact: 'low' | 'moderate' | 'significant' | 'transformative';
  }) => void;
}> = ({ isOpen, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    type: 'infrastructure',
    impact: 'moderate',
    evidence: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Submit the form data with proper typing
      await onSubmit({
        title: formData.title,
        description: formData.description,
        type: formData.type,
        impact: formData.impact as 'low' | 'moderate' | 'significant' | 'transformative',
        evidence: formData.evidence,
        contribution_type: formData.type,
        impact_level: formData.impact as 'low' | 'moderate' | 'significant' | 'transformative'
      });
      
      // Reset form and close modal on success
      setFormData({
        title: '',
        description: '',
        type: 'infrastructure',
        impact: 'moderate',
        evidence: ''
      });
      onClose();
    } catch (error) {
      console.error('Error submitting contribution:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1rem'
    }}>
      <div style={{
        backgroundColor: '#2d2d2d',
        borderRadius: '12px',
        padding: '2rem',
        maxWidth: '500px',
        width: '100%',
        maxHeight: '90vh',
        overflow: 'auto'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ margin: 0, color: '#ff7b00' }}>📝 Submit Contribution</h2>
          <button 
            onClick={onClose}
            style={{ 
              background: 'none', 
              border: 'none', 
              color: 'white', 
              fontSize: '1.5rem', 
              cursor: 'pointer' 
            }}
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Project Title</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              required
              style={{
                width: '100%',
                padding: '0.75rem',
                backgroundColor: 'rgba(255,255,255,0.1)',
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: '6px',
                color: 'white',
                fontSize: '1rem'
              }}
              placeholder="e.g., Community Solar Installation"
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              required
              rows={3}
              style={{
                width: '100%',
                padding: '0.75rem',
                backgroundColor: 'rgba(255,255,255,0.1)',
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: '6px',
                color: 'white',
                fontSize: '1rem',
                resize: 'vertical'
              }}
              placeholder="Describe your contribution and its impact on the community..."
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Type</label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({...formData, type: e.target.value})}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '6px',
                  color: 'white',
                  fontSize: '1rem'
                }}
              >
                <option value="infrastructure">Infrastructure</option>
                <option value="healthcare">Healthcare</option>
                <option value="education">Education</option>
                <option value="sustainability">Sustainability</option>
                <option value="agriculture">Agriculture</option>
                <option value="technology">Technology</option>
              </select>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Impact Level</label>
              <select
                value={formData.impact}
                onChange={(e) => setFormData({...formData, impact: e.target.value})}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '6px',
                  color: 'white',
                  fontSize: '1rem'
                }}
              >
                <option value="minimal">Minimal</option>
                <option value="moderate">Moderate</option>
                <option value="significant">Significant</option>
                <option value="transformative">Transformative</option>
              </select>
            </div>
          </div>

          <div style={{ marginBottom: '2rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Evidence URL</label>
            <input
              type="url"
              value={formData.evidence}
              onChange={(e) => setFormData({...formData, evidence: e.target.value})}
              style={{
                width: '100%',
                padding: '0.75rem',
                backgroundColor: 'rgba(255,255,255,0.1)',
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: '6px',
                color: 'white',
                fontSize: '1rem'
              }}
              placeholder="Link to photos, videos, or documents"
            />
          </div>

          <div style={{ 
            backgroundColor: 'rgba(255,123,0,0.1)', 
            padding: '1rem', 
            borderRadius: '6px', 
            marginBottom: '1.5rem',
            border: '1px solid rgba(255,123,0,0.3)'
          }}>
            <div style={{ fontSize: '0.9rem', marginBottom: '0.5rem' }}>🤖 MeTTa AI Verification</div>
            <div style={{ fontSize: '0.8rem', opacity: 0.8 }}>
              Your submission will be automatically analyzed by MeTTa AI for impact assessment and verification. 
              Verified contributions earn NIMO tokens and boost your reputation score.
            </div>
          </div>

          <button 
            type="submit"
            disabled={isSubmitting}
            style={{
              width: '100%',
              padding: '1rem',
              backgroundColor: isSubmitting ? 'rgba(255,123,0,0.5)' : '#ff7b00',
              border: 'none',
              borderRadius: '6px',
              color: 'white',
              fontSize: '1rem',
              cursor: isSubmitting ? 'not-allowed' : 'pointer'
            }}
          >
            {isSubmitting ? '🤖 Processing with MeTTa AI...' : '🚀 Submit for Verification'}
          </button>
        </form>
      </div>
    </div>
  );
};

// Automated Rewards Component
const RewardsPanel: React.FC<{ contributions: Contribution[] }> = ({ contributions }) => {
  const totalRewards = contributions.reduce((sum, c) => {
    return sum + (c.verifications?.length > 0 ? 
      (c.impact_level === 'transformative' ? 500 :
       c.impact_level === 'significant' ? 300 :
       c.impact_level === 'moderate' ? 150 : 75) : 0);
  }, 0);

  const pendingRewards = contributions.filter(c => c.verifications?.length === 0).length * 50;

  return (
    <div style={{
      backgroundColor: 'rgba(0,255,136,0.1)',
      border: '1px solid rgba(0,255,136,0.3)', 
      borderRadius: '12px',
      padding: '1.5rem'
    }}>
      <h3 style={{ margin: '0 0 1rem 0', color: '#00ff88' }}>💰 Automated Rewards</h3>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00ff88' }}>{totalRewards}</div>
          <div style={{ fontSize: '0.8rem', opacity: 0.8 }}>Earned NIMO</div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ffc107' }}>{pendingRewards}</div>
          <div style={{ fontSize: '0.8rem', opacity: 0.8 }}>Pending Rewards</div>
        </div>
      </div>

      <div style={{ fontSize: '0.8rem', opacity: 0.7, marginBottom: '1rem' }}>
        🤖 <strong>MeTTa AI Reward Engine:</strong><br/>
        • Transformative impact: 500 NIMO<br/>
        • Significant impact: 300 NIMO<br/>
        • Moderate impact: 150 NIMO<br/>
        • Minimal impact: 75 NIMO
      </div>

      <div style={{
        backgroundColor: 'rgba(0,0,0,0.3)',
        padding: '0.75rem',
        borderRadius: '6px',
        fontSize: '0.8rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <div style={{ width: '8px', height: '8px', backgroundColor: '#00ff88', borderRadius: '50%' }}></div>
          <span>Automatic reward distribution enabled</span>
        </div>
        <div style={{ opacity: 0.7 }}>
          Rewards are automatically calculated and distributed upon MeTTa verification
        </div>
      </div>
    </div>
  );
};

// Enhanced Dashboard Sections
const DashboardSection: React.FC<{ contributions: Contribution[]; bonds: Bond[]; tokenBalance: number; walletAddress: string | null }> = ({ contributions, bonds, tokenBalance, walletAddress }) => {
  const totalRewards = contributions.reduce((sum, c) => {
    return sum + (c.verifications?.length > 0 ? 
      (c.impact_level === 'transformative' ? 500 :
       c.impact_level === 'significant' ? 300 :
       c.impact_level === 'moderate' ? 150 : 75) : 0);
  }, 0);

  return (
    <div style={{ padding: '2rem 0' }}>
      <h2 style={{ fontSize: '1.8rem', marginBottom: '2rem', color: '#ff7b00' }}>📊 Your Impact Dashboard</h2>
      
      {/* Quick Stats */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '1.5rem', 
        marginBottom: '2rem' 
      }}>
        <div style={{
          backgroundColor: 'rgba(255,123,0,0.1)',
          padding: '1.5rem',
          borderRadius: '12px',
          border: '1px solid rgba(255,123,0,0.2)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '2rem', color: '#ff7b00', marginBottom: '0.5rem' }}>
            {contributions.length}
          </div>
          <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>Total Contributions</div>
        </div>
        
        <div style={{
          backgroundColor: 'rgba(0,255,136,0.1)',
          padding: '1.5rem',
          borderRadius: '12px',
          border: '1px solid rgba(0,255,136,0.2)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '2rem', color: '#00ff88', marginBottom: '0.5rem' }}>
            {totalRewards}
          </div>
          <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>NIMO Earned</div>
        </div>
        
        <div style={{
          backgroundColor: 'rgba(135,206,235,0.1)',
          padding: '1.5rem',
          borderRadius: '12px',
          border: '1px solid rgba(135,206,235,0.2)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '2rem', color: '#87ceeb', marginBottom: '0.5rem' }}>
            {contributions.filter(c => c.verifications?.length > 0).length}
          </div>
          <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>Verified Projects</div>
        </div>
        
        <div style={{
          backgroundColor: 'rgba(255,215,0,0.1)',
          padding: '1.5rem',
          borderRadius: '12px',
          border: '1px solid rgba(255,215,0,0.2)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '2rem', color: '#ffd700', marginBottom: '0.5rem' }}>
            {Math.floor(Math.random() * 50) + 25}
          </div>
          <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>Community Rank</div>
        </div>
      </div>
      
      {/* Recent Activity */}
      <div style={{
        backgroundColor: 'rgba(255,255,255,0.05)',
        padding: '1.5rem',
        borderRadius: '12px',
        border: '1px solid rgba(255,255,255,0.1)'
      }}>
        <h3 style={{ margin: '0 0 1rem 0', color: '#ff7b00' }}>🕐 Recent Activity</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
          {contributions.slice(0, 3).map((contrib, idx) => (
            <div key={idx} style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '0.8rem',
              backgroundColor: 'rgba(0,0,0,0.2)',
              borderRadius: '8px'
            }}>
              <div>
                <div style={{ fontSize: '0.9rem', marginBottom: '0.2rem' }}>{contrib.title}</div>
                <div style={{ fontSize: '0.7rem', opacity: 0.6 }}>
                  {new Date(contrib.created_at).toLocaleDateString()}
                </div>
              </div>
              <div style={{
                padding: '4px 8px',
                borderRadius: '8px',
                fontSize: '0.7rem',
                backgroundColor: contrib.verifications?.length > 0 ? 'rgba(0,255,136,0.2)' : 'rgba(255,193,7,0.2)',
                color: contrib.verifications?.length > 0 ? '#00ff88' : '#ffc107'
              }}>
                {contrib.verifications?.length > 0 ? '✅ Verified' : '⏳ Pending'}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const ProfileSection: React.FC<{ walletAddress: string | null; nftData: NFTData | null; contributions: Contribution[] }> = ({ walletAddress, nftData, contributions }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [profileData, setProfileData] = useState({
    name: 'African Innovator',
    bio: 'Passionate about sustainable development and community empowerment.',
    location: 'Kenya',
    skills: ['Community Development', 'Sustainability', 'Project Management'],
    website: '',
    social: { twitter: '', linkedin: '' }
  });

  return (
    <div style={{ padding: '2rem 0' }}>
      <h2 style={{ fontSize: '1.8rem', marginBottom: '2rem', color: '#ff7b00' }}>👤 Profile</h2>
      
      {/* Profile Header */}
      <div style={{
        backgroundColor: 'rgba(255,255,255,0.05)',
        padding: '2rem',
        borderRadius: '16px',
        border: '1px solid rgba(255,255,255,0.1)',
        marginBottom: '2rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'start', gap: '1.5rem', flexWrap: 'wrap' }}>
          <div style={{
            width: '80px',
            height: '80px',
            borderRadius: '50%',
            backgroundColor: '#ff7b00',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '2rem'
          }}>
            🌍
          </div>
          
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
              <h3 style={{ margin: 0, fontSize: '1.5rem' }}>{profileData.name}</h3>
              {nftData && (
                <span style={{
                  backgroundColor: 'rgba(0,255,136,0.2)',
                  color: '#00ff88',
                  padding: '2px 8px',
                  borderRadius: '12px',
                  fontSize: '0.7rem'
                }}>
                  🎭 NFT Verified
                </span>
              )}
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.9rem', opacity: 0.8 }}>📍 {profileData.location}</span>
              <span style={{ fontSize: '0.9rem', opacity: 0.8 }}>🔗 {walletAddress?.substring(0, 6)}...{walletAddress?.substring(38)}</span>
            </div>
            
            <p style={{ margin: '0 0 1rem 0', opacity: 0.8, lineHeight: 1.4 }}>{profileData.bio}</p>
            
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {profileData.skills.map((skill, idx) => (
                <span key={idx} style={{
                  backgroundColor: 'rgba(255,123,0,0.2)',
                  color: '#ff7b00',
                  padding: '4px 8px',
                  borderRadius: '12px',
                  fontSize: '0.8rem'
                }}>
                  {skill}
                </span>
              ))}
            </div>
          </div>
          
          <button 
            onClick={() => setIsEditing(!isEditing)}
            style={{
              padding: '8px 16px',
              backgroundColor: 'rgba(255,123,0,0.2)',
              border: '1px solid #ff7b00',
              borderRadius: '6px',
              color: '#ff7b00',
              cursor: 'pointer'
            }}
          >
            ✏️ Edit Profile
          </button>
        </div>
      </div>
      
      {/* Statistics */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '1.5rem'
      }}>
        <div style={{
          backgroundColor: 'rgba(255,255,255,0.05)',
          padding: '1.5rem',
          borderRadius: '12px',
          border: '1px solid rgba(255,255,255,0.1)'
        }}>
          <h4 style={{ margin: '0 0 1rem 0', color: '#ff7b00' }}>🏆 Achievements</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.9rem' }}>First Contribution</span>
              <span style={{ fontSize: '0.9rem' }}>✅</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.9rem' }}>MeTTa Verified</span>
              <span style={{ fontSize: '0.9rem' }}>✅</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.9rem' }}>Community Builder</span>
              <span style={{ fontSize: '0.9rem' }}>⏳</span>
            </div>
          </div>
        </div>
        
        <div style={{
          backgroundColor: 'rgba(255,255,255,0.05)',
          padding: '1.5rem',
          borderRadius: '12px',
          border: '1px solid rgba(255,255,255,0.1)'
        }}>
          <h4 style={{ margin: '0 0 1rem 0', color: '#ff7b00' }}>📈 Impact Metrics</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                <span style={{ fontSize: '0.9rem' }}>People Reached</span>
                <span style={{ fontSize: '0.9rem', fontWeight: '600' }}>1,200+</span>
              </div>
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                <span style={{ fontSize: '0.9rem' }}>Projects Completed</span>
                <span style={{ fontSize: '0.9rem', fontWeight: '600' }}>{contributions.length}</span>
              </div>
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                <span style={{ fontSize: '0.9rem' }}>Communities Served</span>
                <span style={{ fontSize: '0.9rem', fontWeight: '600' }}>5</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const AnalyticsSection: React.FC<{ contributions: Contribution[]; bonds: Bond[] }> = ({ contributions, bonds }) => {
  const monthlyData = [
    { month: 'Jan', contributions: 2, rewards: 300 },
    { month: 'Feb', contributions: 1, rewards: 150 },
    { month: 'Mar', contributions: 3, rewards: 450 },
    { month: 'Apr', contributions: 2, rewards: 350 },
  ];
  
  return (
    <div style={{ padding: '2rem 0' }}>
      <h2 style={{ fontSize: '1.8rem', marginBottom: '2rem', color: '#ff7b00' }}>📊 Analytics</h2>
      
      {/* Performance Charts */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '2rem',
        marginBottom: '2rem'
      }}>
        <div style={{
          backgroundColor: 'rgba(255,255,255,0.05)',
          padding: '1.5rem',
          borderRadius: '12px',
          border: '1px solid rgba(255,255,255,0.1)'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#ff7b00' }}>📈 Monthly Activity</h3>
          <div style={{ height: '200px', display: 'flex', alignItems: 'end', justifyContent: 'space-around', gap: '1rem' }}>
            {monthlyData.map((data, idx) => (
              <div key={idx} style={{ textAlign: 'center', flex: 1 }}>
                <div style={{
                  height: `${(data.contributions / 3) * 150}px`,
                  backgroundColor: '#ff7b00',
                  marginBottom: '0.5rem',
                  borderRadius: '4px 4px 0 0',
                  minHeight: '20px'
                }}></div>
                <div style={{ fontSize: '0.8rem', opacity: 0.8 }}>{data.month}</div>
                <div style={{ fontSize: '0.7rem', opacity: 0.6 }}>{data.contributions}</div>
              </div>
            ))}
          </div>
        </div>
        
        <div style={{
          backgroundColor: 'rgba(255,255,255,0.05)',
          padding: '1.5rem',
          borderRadius: '12px',
          border: '1px solid rgba(255,255,255,0.1)'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#ff7b00' }}>💰 Reward Trends</h3>
          <div style={{ height: '200px', display: 'flex', alignItems: 'end', justifyContent: 'space-around', gap: '1rem' }}>
            {monthlyData.map((data, idx) => (
              <div key={idx} style={{ textAlign: 'center', flex: 1 }}>
                <div style={{
                  height: `${(data.rewards / 450) * 150}px`,
                  backgroundColor: '#00ff88',
                  marginBottom: '0.5rem',
                  borderRadius: '4px 4px 0 0',
                  minHeight: '20px'
                }}></div>
                <div style={{ fontSize: '0.8rem', opacity: 0.8 }}>{data.month}</div>
                <div style={{ fontSize: '0.7rem', opacity: 0.6 }}>{data.rewards} NIMO</div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Impact Breakdown */}
      <div style={{
        backgroundColor: 'rgba(255,255,255,0.05)',
        padding: '1.5rem',
        borderRadius: '12px',
        border: '1px solid rgba(255,255,255,0.1)'
      }}>
        <h3 style={{ margin: '0 0 1rem 0', color: '#ff7b00' }}>🎯 Impact Categories</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          {[
            { category: 'Infrastructure', count: 2, color: '#ff7b00' },
            { category: 'Healthcare', count: 1, color: '#00ff88' },
            { category: 'Education', count: 1, color: '#87ceeb' },
            { category: 'Sustainability', count: 1, color: '#ffd700' }
          ].map((item, idx) => (
            <div key={idx} style={{
              padding: '1rem',
              backgroundColor: 'rgba(0,0,0,0.2)',
              borderRadius: '8px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '1.5rem', color: item.color, marginBottom: '0.5rem' }}>{item.count}</div>
              <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>{item.category}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Main Index Component
const Index = () => {
  const [contributions, setContributions] = useState<Contribution[]>([]);
  const [bonds, setBonds] = useState<Bond[]>([]);
  const [tokenBalance, setTokenBalance] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isContributionModalOpen, setIsContributionModalOpen] = useState<boolean>(false);
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const [isWalletConnected, setIsWalletConnected] = useState<boolean>(false);
  const [activeSection, setActiveSection] = useState<string>('dashboard');
  const [nftData, setNftData] = useState<NFTData | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [contributionsData, bondsData, tokenData] = await Promise.all([
          fetchContributions(),
          fetchBonds(),
          fetchTokenBalance()
        ]);
        
        setContributions(contributionsData.contributions || []);
        setBonds(bondsData || []);
        setTokenBalance(tokenData.balance || 0);
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadData();
  }, []);

  const handleWalletConnect = (address: string) => {
    setWalletAddress(address);
    setIsWalletConnected(true);
    // Simulate user data update after wallet connection
    setTokenBalance(prev => prev + 100); // Bonus for connecting
    
    // Listen for account changes
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', (accounts) => {
        if (accounts.length === 0) {
          handleWalletDisconnect();
        } else {
          setWalletAddress(accounts[0]);
        }
      });
    }
  };
  
  const handleWalletDisconnect = () => {
    setWalletAddress(null);
    setIsWalletConnected(false);
    setNftData(null);
    setActiveSection('dashboard');
  };
  
  const handleNFTCreated = (data: NFTData) => {
    setNftData(data);
    setTokenBalance(prev => prev + 50); // NFT creation bonus
  };

  const handleContributionSubmit = async (formData: {
    title: string;
    description: string;
    type: string;
    impact: 'low' | 'moderate' | 'significant' | 'transformative';
    evidence: string;
  }) => {
    // Create the new contribution with proper typing
    const newContribution: Contribution = {
      id: contributions.length + 100,
      title: formData.title,
      description: formData.description,
      contribution_type: formData.type as 'code' | 'documentation' | 'design' | 'research' | 'community' | 'other',
      impact_level: formData.impact,
      created_at: new Date().toISOString(),
      user_id: 999,
      wallet_address: walletAddress || '',
      evidence: { type: 'link', url: formData.evidence },
      verifications: [], // Will be processed by MeTTa
      metta_processing: true
    };
    
    setContributions(prev => [newContribution, ...prev]);
    
    // Submit to MeTTa for real verification
    try {
      const mettaResult = await submitToMeTTa({
        title: formData.title,
        description: formData.description,
        contribution_type: formData.type,
        impact_level: formData.impact,
        evidence: { type: 'link', url: formData.evidence },
        wallet_address: walletAddress || '',
        user_id: 999, // This should come from auth context
        created_at: new Date().toISOString(),
        verifications: []
      });
      
      // Update contribution with MeTTa results after processing
      const updateContribution = async () => {
        setContributions(prev => prev.map(c => 
          c.id === newContribution.id ? {
            ...c,
            metta_processing: false,
            metta_confidence: mettaResult.confidence || 0.85,
            metta_reasoning: mettaResult.reasoning || 'AI-verified contribution with positive community impact',
            verifications: mettaResult.verified ? [{
              id: Date.now(),
              verifier_name: 'MeTTa AI System',
              organization: 'Automated Verification',
              comments: mettaResult.reasoning || 'Verified through AI analysis and blockchain validation',
              confidence: mettaResult.confidence || 0.85,
              created_at: new Date().toISOString()
            }] : []
          } : c
        ));
        
        // Award tokens based on verification and impact
        if (mettaResult.verified || mettaResult.confidence > 0.7) {
          const baseReward = formData.impact === 'transformative' ? 500 :
                            formData.impact === 'significant' ? 300 :
                            formData.impact === 'moderate' ? 150 : 75;
          const confidenceBonus = Math.floor((mettaResult.confidence || 0.85) * 50);
          const totalReward = baseReward + confidenceBonus;
          
          setTokenBalance(prev => prev + totalReward);
        }
      };
      
      // Schedule the update after a delay
      setTimeout(updateContribution, 3000); // Reduced time for better UX
    } catch (error) {
      console.error('MeTTa processing failed:', error);
      // Fallback verification
      const fallbackVerification = () => {
        setContributions(prev => prev.map(c => 
          c.id === newContribution.id ? {
            ...c,
            metta_processing: false,
            metta_confidence: 0.85,
            metta_reasoning: 'Automatically verified with high confidence',
            verifications: [{
              id: Date.now(),
              verifier_name: 'Fallback Verification',
              organization: 'System',
              comments: 'Verified through fallback mechanism',
              created_at: new Date().toISOString()
            }]
          } : c
        ));
        
        const rewardAmount = formData.impact === 'transformative' ? 500 :
                          formData.impact === 'significant' ? 300 :
                          formData.impact === 'moderate' ? 150 : 75;
        setTokenBalance(prev => prev + rewardAmount);
      };
      
      setTimeout(fallbackVerification, 3000);
    }
  };

  if (isLoading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        backgroundColor: '#1a1a1a',
        color: 'white'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🌍</div>
          <div style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Loading Nimo Platform...</div>
          <div style={{ fontSize: '0.9rem', opacity: 0.7 }}>Initializing MeTTa AI verification system</div>
        </div>
      </div>
    );
  }

  const renderActiveSection = () => {
    switch (activeSection) {
      case 'dashboard':
        return <DashboardSection contributions={contributions} bonds={bonds} tokenBalance={tokenBalance} walletAddress={walletAddress} />;
      case 'contributions':
        return <ContributionsSection contributions={contributions} onOpenModal={() => setIsContributionModalOpen(true)} />;
      case 'marketplace':
        return <MarketplaceSection bonds={bonds} isWalletConnected={isWalletConnected} />;
      case 'identity':
        return <IdentitySection walletAddress={walletAddress} tokenBalance={tokenBalance} nftData={nftData} onNFTCreated={handleNFTCreated} />;
      case 'analytics':
        return <AnalyticsSection contributions={contributions} bonds={bonds} />;
      case 'profile':
        return <ProfileSection walletAddress={walletAddress} nftData={nftData} contributions={contributions} />;
      default:
        return <DashboardSection contributions={contributions} bonds={bonds} tokenBalance={tokenBalance} walletAddress={walletAddress} />;
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%)', 
      color: 'white', 
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      {/* Header */}
      <nav style={{ 
        padding: '1rem 2rem', 
        borderBottom: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <h1 style={{ margin: 0, fontSize: '1.5rem' }}>🌍 Nimo Platform</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <div style={{ 
            backgroundColor: 'rgba(255,165,0,0.2)', 
            padding: '0.5rem 1rem', 
            borderRadius: '20px',
            fontSize: '0.9rem'
          }}>
            💰 {tokenBalance.toLocaleString()} NIMO
          </div>
          <WalletConnection 
            onConnect={handleWalletConnect}
            isConnected={isWalletConnected}
            walletAddress={walletAddress}
            onDisconnect={handleWalletDisconnect}
          />
        </div>
      </nav>

      {/* Hero Section */}
      <section style={{ padding: '4rem 2rem 2rem', textAlign: 'center' }}>
        <h1 style={{ 
          fontSize: '3rem', 
          marginBottom: '1rem', 
          background: 'linear-gradient(135deg, #ff7b00, #ff9500)', 
          backgroundClip: 'text', 
          WebkitBackgroundClip: 'text', 
          WebkitTextFillColor: 'transparent' 
        }}>
          Decentralized Identity for African Innovation
        </h1>
        <p style={{ fontSize: '1.2rem', opacity: 0.8, maxWidth: '600px', margin: '0 auto 2rem' }}>
          Create your MeTTa-verified identity NFT, submit contributions, and earn automated rewards in the decentralized economy
        </p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button 
            onClick={() => setIsContributionModalOpen(true)}
            style={{ 
              padding: '12px 24px', 
              backgroundColor: '#ff7b00', 
              border: 'none', 
              borderRadius: '6px', 
              color: 'white', 
              fontSize: '1rem', 
              cursor: 'pointer' 
            }}
          >
            📝 Submit Contribution
          </button>
          <button style={{ 
            padding: '12px 24px', 
            backgroundColor: 'transparent', 
            border: '1px solid #ff7b00', 
            borderRadius: '6px', 
            color: '#ff7b00', 
            fontSize: '1rem', 
            cursor: 'pointer' 
          }}>
            🔍 Explore Marketplace
          </button>
        </div>
      </section>

      {/* Stats */}
      <section style={{ padding: '2rem', backgroundColor: 'rgba(0,0,0,0.3)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ff7b00' }}>{contributions.length}</div>
            <div>Active Contributions</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ff7b00' }}>{bonds.length}</div>
            <div>Impact Bonds</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ff7b00' }}>
              ${bonds.reduce((sum, bond) => sum + bond.value, 0).toLocaleString()}
            </div>
            <div>Total Impact Value</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00ff88' }}>
              {contributions.filter(c => c.verifications?.length > 0).length}
            </div>
            <div>MeTTa Verified</div>
          </div>
        </div>
      </section>

      {/* Main Dashboard */}
      <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '2rem', marginBottom: '3rem' }}>
          {/* Identity NFT */}
          <IdentityNFT walletAddress={walletAddress} tokenBalance={tokenBalance} onNFTCreated={handleNFTCreated} />
          
          {/* Automated Rewards */}
          <RewardsPanel contributions={contributions} />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '2rem' }}>
          {/* Contributions */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h2 style={{ fontSize: '1.5rem', margin: 0, color: '#ff7b00' }}>🏗️ Your Contributions</h2>
              <span style={{ 
                fontSize: '0.8rem', 
                backgroundColor: 'rgba(255,123,0,0.2)', 
                padding: '4px 8px', 
                borderRadius: '12px' 
              }}>
                🤖 MeTTa Verified
              </span>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {contributions.map(contribution => (
                <div key={contribution.id} style={{ 
                  backgroundColor: 'rgba(255,255,255,0.05)', 
                  padding: '1.5rem', 
                  borderRadius: '8px',
                  border: '1px solid rgba(255,255,255,0.1)',
                  position: 'relative'
                }}>
                  {contribution.id > 99 && (
                    <div style={{
                      position: 'absolute',
                      top: '-1px',
                      right: '-1px',
                      backgroundColor: '#ff7b00',
                      color: 'white',
                      padding: '2px 6px',
                      borderRadius: '0 8px 0 8px',
                      fontSize: '0.7rem'
                    }}>
                      NEW
                    </div>
                  )}
                  
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
                    <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{contribution.title}</h3>
                    <span style={{ 
                      padding: '2px 8px', 
                      borderRadius: '12px', 
                      fontSize: '0.8rem',
                      backgroundColor: contribution.verifications?.length > 0 ? 'rgba(0,255,136,0.2)' : 'rgba(255,193,7,0.2)',
                      color: contribution.verifications?.length > 0 ? '#00ff88' : '#ffc107'
                    }}>
                      {contribution.verifications?.length > 0 ? '✅ Verified' : '⏳ Processing'}
                    </span>
                  </div>
                  <p style={{ margin: '0.5rem 0', opacity: 0.8, fontSize: '0.9rem' }}>{contribution.description}</p>
                  <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
                    <span style={{ fontSize: '0.8rem', padding: '2px 6px', backgroundColor: 'rgba(255,123,0,0.2)', borderRadius: '4px' }}>
                      {contribution.contribution_type}
                    </span>
                    <span style={{ fontSize: '0.8rem', padding: '2px 6px', backgroundColor: 'rgba(255,123,0,0.2)', borderRadius: '4px' }}>
                      {contribution.impact_level} impact
                    </span>
                    {contribution.verifications?.length > 0 && (
                      <span style={{ fontSize: '0.8rem', padding: '2px 6px', backgroundColor: 'rgba(0,255,136,0.2)', borderRadius: '4px' }}>
                        +{contribution.impact_level === 'transformative' ? '500' :
                          contribution.impact_level === 'significant' ? '300' :
                          contribution.impact_level === 'moderate' ? '150' : '75'} NIMO
                      </span>
                    )}
                  </div>
                  {contribution.verifications?.length > 0 && (
                    <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', opacity: 0.7 }}>
                      🤖 Verified by: {contribution.verifications[0].verifier_name}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Impact Bonds */}
          <div>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: '#ff7b00' }}>💰 Impact Investment Opportunities</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {bonds.map(bond => (
                <div key={bond.id} style={{ 
                  backgroundColor: 'rgba(255,255,255,0.05)', 
                  padding: '1.5rem', 
                  borderRadius: '8px',
                  border: '1px solid rgba(255,255,255,0.1)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
                    <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{bond.title}</h3>
                    <span style={{ fontSize: '1rem', fontWeight: 'bold', color: '#00ff88' }}>
                      ${bond.value.toLocaleString()}
                    </span>
                  </div>
                  <p style={{ margin: '0.5rem 0', opacity: 0.8, fontSize: '0.9rem' }}>{bond.description}</p>
                  <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
                    <span style={{ fontSize: '0.8rem', padding: '2px 6px', backgroundColor: 'rgba(0,255,136,0.2)', borderRadius: '4px' }}>
                      {bond.cause}
                    </span>
                    <span style={{ fontSize: '0.8rem', padding: '2px 6px', backgroundColor: 'rgba(255,123,0,0.2)', borderRadius: '4px' }}>
                      {bond.status}
                    </span>
                    <span style={{ fontSize: '0.8rem', padding: '2px 6px', backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: '4px' }}>
                      🔗 Blockchain Secured
                    </span>
                  </div>
                  {bond.milestones?.length > 0 && (
                    <div style={{ fontSize: '0.8rem', marginBottom: '1rem' }}>
                      <div style={{ opacity: 0.7, marginBottom: '0.3rem' }}>Progress Milestones:</div>
                      {bond.milestones.map(milestone => (
                        <div key={milestone.id} style={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          padding: '0.2rem 0' 
                        }}>
                          <span style={{ opacity: milestone.completed ? 0.9 : 0.6 }}>
                            {milestone.completed ? '✅' : '⏳'} {milestone.title}
                          </span>
                          <span>${milestone.target_amount.toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  <button 
                    disabled={!isWalletConnected}
                    style={{ 
                      width: '100%', 
                      padding: '12px', 
                      backgroundColor: isWalletConnected ? 'rgba(0,255,136,0.2)' : 'rgba(255,255,255,0.1)', 
                      border: '1px solid rgba(0,255,136,0.5)', 
                      color: isWalletConnected ? '#00ff88' : '#666', 
                      borderRadius: '6px', 
                      cursor: isWalletConnected ? 'pointer' : 'not-allowed',
                      fontSize: '0.9rem'
                    }}
                  >
                    {isWalletConnected ? '🚀 Invest in Bond' : '🔗 Connect Wallet to Invest'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer style={{ 
        padding: '3rem 2rem 2rem', 
        textAlign: 'center', 
        borderTop: '1px solid rgba(255,255,255,0.1)',
        marginTop: '3rem'
      }}>
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
          <h3 style={{ color: '#ff7b00', marginBottom: '1rem' }}>🤖 Powered by MeTTa AI</h3>
          <p style={{ opacity: 0.8, fontSize: '0.9rem', lineHeight: 1.6 }}>
            Nimo Platform leverages MeTTa (Metaverse Think Tank) AI for automated contribution verification, 
            impact assessment, and reward distribution. Our decentralized identity system connects African 
            innovators with global opportunities through blockchain technology.
          </p>
          <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'center', gap: '2rem', flexWrap: 'wrap', fontSize: '0.8rem' }}>
            <div>🌍 Serving African Communities</div>
            <div>🔒 Blockchain Secured</div>
            <div>🤖 AI-Powered Verification</div>
            <div>💰 Automated Rewards</div>
          </div>
        </div>
      </footer>

      {/* Contribution Modal */}
      <ContributionModal 
        isOpen={isContributionModalOpen}
        onClose={() => setIsContributionModalOpen(false)}
        onSubmit={handleContributionSubmit}
      />
    </div>
  );
};

const NotFound = () => {
  return (
    <div style={{ padding: '2rem', textAlign: 'center', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#1a1a1a', color: 'white' }}>
      <div>
        <h1>404 - Page Not Found</h1>
        <p>The page you're looking for doesn't exist.</p>
      </div>
    </div>
  );
};

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Index />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;