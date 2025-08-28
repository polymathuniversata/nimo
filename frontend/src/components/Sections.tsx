// Clean Sections.tsx file
import React, { useState } from 'react';
import { useWallet } from '@/hooks/useWallet';

// Types
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

interface NFTData {
  id: number;
  walletAddress: string;
  tokenBalance: number;
  traits: {
    reputation: number;
    verificationLevel: string;
    joinDate: string;
  };
}

// Mock data for bonds
const MOCK_BONDS: Bond[] = [
  {
    id: 1,
    name: 'Community Development Bond',
    description: 'Fund for local infrastructure projects',
    yield: 8.5,
    minInvestment: 100,
    maturityDate: '2024-12-31',
    available: 50000,
    totalSupply: 100000,
    issuer: 'Nimo DAO'
  },
  {
    id: 2,
    name: 'Green Energy Fund',
    description: 'Renewable energy projects in Africa',
    yield: 12.0,
    minInvestment: 200,
    maturityDate: '2025-06-30',
    available: 75000,
    totalSupply: 200000,
    issuer: 'EcoFund'
  },
  {
    id: 3,
    name: 'Education Initiative',
    description: 'Funding for tech education programs',
    yield: 6.5,
    minInvestment: 50,
    maturityDate: '2024-09-30',
    available: 25000,
    totalSupply: 50000,
    issuer: 'EduChain'
  }
];

interface ContributionsSectionProps {
  contributions: Contribution[];
  onOpenModal: () => void;
}

export const ContributionsSection: React.FC<ContributionsSectionProps> = ({ contributions, onOpenModal }) => {
  return (
    <div style={{ padding: '2rem 0' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 style={{ fontSize: '1.5rem', margin: 0, color: '#ff7b00' }}>���️ My Contributions</h2>
        <button
          onClick={onOpenModal}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#ff7b00',
            border: 'none',
            borderRadius: '6px',
            color: 'white',
            cursor: 'pointer',
            fontSize: '0.9rem'
          }}
        >
          + New Contribution
        </button>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {contributions.length > 0 ? (
          contributions.map((contribution) => (
            <div key={contribution.id} style={{
              backgroundColor: 'rgba(255,255,255,0.05)',
              padding: '1.5rem',
              borderRadius: '8px',
              border: '1px solid rgba(255,255,255,0.1)'
            }}>
              <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.1rem' }}>{contribution.title}</h3>
              <p style={{ margin: '0 0 1rem 0', opacity: 0.8, fontSize: '0.9rem' }}>{contribution.description}</p>
              <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                <span style={{
                  fontSize: '0.8rem',
                  padding: '2px 6px',
                  backgroundColor: 'rgba(255,123,0,0.2)',
                  borderRadius: '4px'
                }}>
                  Status: {contribution.status || 'Pending'}
                </span>
                <span style={{
                  fontSize: '0.8rem',
                  padding: '2px 6px',
                  backgroundColor: 'rgba(0,255,136,0.2)',
                  borderRadius: '4px'
                }}>
                  Reward: {contribution.reward || 0} NIMO
                </span>
              </div>
            </div>
          ))
        ) : (
          <p style={{ opacity: 0.7, textAlign: 'center', padding: '2rem' }}>
            No contributions yet. Start by creating your first contribution!
          </p>
        )}
      </div>
    </div>
  );
};

interface MarketplaceSectionProps {
  bonds?: Bond[];
  isWalletConnected?: boolean;
}

export const MarketplaceSection: React.FC<MarketplaceSectionProps> = ({
  bonds: propBonds,
  isWalletConnected: propIsConnected
}) => {
  const {
    isConnected,
    address,
    connectWallet,
    disconnectWallet,
    chainId,
    networkName
  } = useWallet();

  const [activeTab, setActiveTab] = useState<'bonds' | 'my-investments'>('bonds');
  const [searchQuery, setSearchQuery] = useState('');
  const [bonds, setBonds] = useState<Bond[]>(propBonds || MOCK_BONDS);
  const [isLoading, setIsLoading] = useState(false);
  const [myInvestments, setMyInvestments] = useState<Investment[]>([]);

  // Use prop value or hook value for connection status
  const walletConnected = propIsConnected !== undefined ? propIsConnected : isConnected;

  // Filter bonds based on search query
  const filteredBonds = bonds.filter(bond =>
    bond.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    bond.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Mock investment function
  const handleInvest = async (bondId: number, amount: number) => {
    if (!walletConnected) {
      await connectWallet();
      return;
    }

    setIsLoading(true);

    // Simulate API call
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));

      const bond = bonds.find(b => b.id === bondId);
      if (!bond) throw new Error('Bond not found');

      if (amount < bond.minInvestment) {
        throw new Error(`Minimum investment is ${bond.minInvestment} NIMO`);
      }

      // Update bond availability
      const updatedBonds = bonds.map(b =>
        b.id === bondId
          ? { ...b, available: Math.max(0, b.available - amount) }
          : b
      );

      setBonds(updatedBonds);

      // Add to my investments
      const investment: Investment = {
        ...bond,
        investmentAmount: amount,
        investmentDate: new Date().toISOString(),
        expectedReturn: amount * (1 + bond.yield / 100)
      };

      setMyInvestments(prev => [...prev, investment]);

      alert(`Investment successful! You've invested ${amount} NIMO in ${bond.name}`);

    } catch (error) {
      alert(`Investment failed: ${error instanceof Error ? error.message : 'Failed to process investment'}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Format wallet address
  const formatAddress = (addr: string) =>
    `${addr.substring(0, 6)}...${addr.substring(addr.length - 4)}`;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        gap: '1rem',
        marginBottom: '1rem'
      }}>
        <div>
          <h2 style={{
            fontSize: '1.8rem',
            marginBottom: '0.5rem',
            color: '#ff7b00',
            fontWeight: 'bold'
          }}>
            NIMO Marketplace
          </h2>
          <p style={{
            opacity: 0.8,
            margin: 0,
            fontSize: '0.9rem'
          }}>
            Discover and invest in community bonds
          </p>
        </div>

        <div style={{
          position: 'relative',
          width: '100%',
          maxWidth: '300px'
        }}>
          <input
            type="text"
            placeholder="Search bonds..."
            style={{
              width: '100%',
              padding: '0.5rem 1rem',
              paddingRight: '2.5rem',
              borderRadius: '6px',
              border: '1px solid rgba(255,255,255,0.2)',
              backgroundColor: 'rgba(255,255,255,0.1)',
              color: 'white',
              fontSize: '0.9rem'
            }}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <svg
            xmlns="http://www.w3.org/2000/svg"
            style={{
              position: 'absolute',
              right: '0.75rem',
              top: '50%',
              transform: 'translateY(-50%)',
              width: '1rem',
              height: '1rem',
              opacity: 0.6
            }}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
      </div>

      {!walletConnected ? (
        <div style={{
          borderRadius: '12px',
          border: '1px dashed rgba(255,123,0,0.5)',
          padding: '2rem',
          textAlign: 'center',
          backgroundColor: 'rgba(255,123,0,0.05)'
        }}>
          <div style={{
            margin: '0 auto',
            width: '3rem',
            height: '3rem',
            borderRadius: '50%',
            backgroundColor: 'rgba(255,123,0,0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '1rem'
          }}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#ff7b00"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"></path>
              <path d="M3 5v14a2 2 0 0 0 2 2h16v-5"></path>
              <path d="M18 12a2 2 0 1 0 0-4 2 2 0 0 0 0 4z"></path>
            </svg>
          </div>
          <h3 style={{
            fontSize: '1.2rem',
            marginBottom: '0.5rem',
            color: '#ff7b00'
          }}>
            Connect your wallet
          </h3>
          <p style={{
            opacity: 0.8,
            marginBottom: '1.5rem',
            fontSize: '0.9rem'
          }}>
            Connect your wallet to explore and invest in community bonds
          </p>
          <button
            onClick={connectWallet}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#ff7b00',
              border: 'none',
              borderRadius: '6px',
              color: 'white',
              fontSize: '0.9rem',
              cursor: 'pointer',
              fontWeight: '600'
            }}
            disabled={isLoading}
          >
            {isLoading ? 'Connecting...' : 'Connect Wallet'}
          </button>

          {chainId && (
            <div style={{
              marginTop: '1rem',
              fontSize: '0.8rem',
              opacity: 0.6
            }}>
              Connected to: {networkName || 'Unknown Network'} ({chainId})
            </div>
          )}
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{
            borderBottom: '1px solid rgba(255,255,255,0.1)',
            paddingBottom: '0.5rem'
          }}>
            <nav style={{
              display: 'flex',
              gap: '2rem'
            }}>
              <button
                onClick={() => setActiveTab('bonds')}
                style={{
                  padding: '0.5rem 0',
                  borderBottom: activeTab === 'bonds' ? '2px solid #ff7b00' : '2px solid transparent',
                  color: activeTab === 'bonds' ? '#ff7b00' : 'rgba(255,255,255,0.6)',
                  backgroundColor: 'transparent',
                  border: 'none',
                  borderTop: 'none',
                  borderLeft: 'none',
                  borderRight: 'none',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  fontWeight: activeTab === 'bonds' ? '600' : '400'
                }}
              >
                All Bonds
              </button>
              <button
                onClick={() => setActiveTab('my-investments')}
                style={{
                  padding: '0.5rem 0',
                  borderBottom: activeTab === 'my-investments' ? '2px solid #ff7b00' : '2px solid transparent',
                  color: activeTab === 'my-investments' ? '#ff7b00' : 'rgba(255,255,255,0.6)',
                  backgroundColor: 'transparent',
                  border: 'none',
                  borderTop: 'none',
                  borderLeft: 'none',
                  borderRight: 'none',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  fontWeight: activeTab === 'my-investments' ? '600' : '400'
                }}
              >
                My Investments
              </button>
            </nav>
          </div>

          {activeTab === 'bonds' && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '1.5rem'
            }}>
              {filteredBonds.length > 0 ? (
                filteredBonds.map((bond) => (
                  <div key={bond.id} style={{
                    overflow: 'hidden',
                    borderRadius: '12px',
                    border: '1px solid rgba(255,255,255,0.1)',
                    backgroundColor: 'rgba(255,255,255,0.05)',
                    padding: '1.5rem',
                    transition: 'all 0.3s ease',
                    cursor: 'pointer'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 8px 25px rgba(255,123,0,0.2)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                  >
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start',
                      marginBottom: '1rem'
                    }}>
                      <h3 style={{
                        fontSize: '1.1rem',
                        margin: 0,
                        fontWeight: '600'
                      }}>
                        {bond.name}
                      </h3>
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '12px',
                        fontSize: '0.75rem',
                        fontWeight: '600',
                        backgroundColor: 'rgba(0,255,136,0.2)',
                        color: '#00ff88'
                      }}>
                        {bond.yield}% APY
                      </span>
                    </div>
                    <p style={{
                      margin: '0 0 1rem 0',
                      opacity: 0.8,
                      fontSize: '0.9rem',
                      lineHeight: '1.4'
                    }}>
                      {bond.description || 'Community development bond with competitive returns'}
                    </p>
                    <div style={{
                      display: 'grid',
                      gridTemplateColumns: '1fr 1fr',
                      gap: '0.5rem',
                      fontSize: '0.8rem',
                      marginBottom: '1.5rem'
                    }}>
                      <div>
                        <div style={{ opacity: 0.7 }}>Min. Investment</div>
                        <div style={{ fontWeight: '600' }}>{bond.minInvestment} NIMO</div>
                      </div>
                      <div>
                        <div style={{ opacity: 0.7 }}>Maturity</div>
                        <div style={{ fontWeight: '600' }}>
                          {new Date(bond.maturityDate).toLocaleDateString()}
                        </div>
                      </div>
                      <div style={{ gridColumn: 'span 2' }}>
                        <div style={{ opacity: 0.7 }}>Available</div>
                        <div style={{ fontWeight: '600' }}>
                          {bond.available.toLocaleString()} / {bond.totalSupply.toLocaleString()}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => handleInvest(bond.id, bond.minInvestment)}
                      disabled={isLoading || bond.available <= 0}
                      style={{
                        width: '100%',
                        padding: '0.75rem',
                        backgroundColor: isLoading || bond.available <= 0 ? 'rgba(255,123,0,0.5)' : '#ff7b00',
                        border: 'none',
                        borderRadius: '6px',
                        color: 'white',
                        fontSize: '0.9rem',
                        cursor: isLoading || bond.available <= 0 ? 'not-allowed' : 'pointer',
                        fontWeight: '600',
                        transition: 'all 0.3s ease'
                      }}
                    >
                      {isLoading ? 'Processing...' : `Invest ${bond.minInvestment} NIMO`}
                    </button>
                    {bond.available <= 0 && (
                      <p style={{
                        marginTop: '0.5rem',
                        fontSize: '0.75rem',
                        textAlign: 'center',
                        color: '#ffc107',
                        opacity: 0.8
                      }}>
                        Bond is currently sold out
                      </p>
                    )}
                  </div>
                ))
              ) : (
                <div style={{
                  gridColumn: '1 / -1',
                  padding: '3rem',
                  textAlign: 'center'
                }}>
                  <svg
                    style={{
                      margin: '0 auto',
                      width: '3rem',
                      height: '3rem',
                      opacity: 0.6,
                      marginBottom: '1rem'
                    }}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      vectorEffect="non-scaling-stroke"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <h3 style={{
                    fontSize: '1.1rem',
                    marginBottom: '0.5rem',
                    opacity: 0.8
                  }}>
                    No bonds found
                  </h3>
                  <p style={{
                    opacity: 0.6,
                    fontSize: '0.9rem'
                  }}>
                    {searchQuery ? 'No bonds match your search.' : 'No bonds available at the moment. Check back later!'}
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'my-investments' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{
                padding: '1rem',
                borderRadius: '8px',
                backgroundColor: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.1)'
              }}>
                <h3 style={{
                  fontSize: '1rem',
                  marginBottom: '0.5rem',
                  fontWeight: '600'
                }}>
                  Wallet Information
                </h3>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '0.5rem',
                  fontSize: '0.8rem'
                }}>
                  <div>
                    <div style={{ opacity: 0.7 }}>Connected Wallet</div>
                    <div style={{ fontFamily: 'monospace' }}>
                      {address ? formatAddress(address) : 'Not connected'}
                    </div>
                  </div>
                  <div>
                    <div style={{ opacity: 0.7 }}>Network</div>
                    <div>{networkName || 'Unknown'}</div>
                  </div>
                </div>
                <button
                  onClick={disconnectWallet}
                  style={{
                    marginTop: '1rem',
                    padding: '0.5rem 1rem',
                    fontSize: '0.8rem',
                    color: '#ff4444',
                    backgroundColor: 'transparent',
                    border: '1px solid #ff4444',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Disconnect Wallet
                </button>
              </div>

              {myInvestments.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {myInvestments.map((investment) => (
                    <div key={`${investment.id}-${investment.investmentDate}`} style={{
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '8px',
                      padding: '1rem'
                    }}>
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                        marginBottom: '0.5rem'
                      }}>
                        <div>
                          <h4 style={{
                            fontSize: '1rem',
                            margin: '0 0 0.25rem 0',
                            fontWeight: '600'
                          }}>
                            {investment.name}
                          </h4>
                          <p style={{
                            fontSize: '0.8rem',
                            opacity: 0.7,
                            margin: 0
                          }}>
                            Invested: {new Date(investment.investmentDate).toLocaleDateString()}
                          </p>
                        </div>
                        <span style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          padding: '0.25rem 0.5rem',
                          borderRadius: '12px',
                          fontSize: '0.7rem',
                          fontWeight: '600',
                          backgroundColor: 'rgba(0,255,136,0.2)',
                          color: '#00ff88'
                        }}>
                          Active
                        </span>
                      </div>
                      <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                        gap: '1rem',
                        fontSize: '0.8rem',
                        marginTop: '1rem'
                      }}>
                        <div>
                          <p style={{ opacity: 0.7, margin: '0 0 0.25rem 0' }}>Amount</p>
                          <p style={{ fontWeight: '600', margin: 0 }}>{investment.investmentAmount} NIMO</p>
                        </div>
                        <div>
                          <p style={{ opacity: 0.7, margin: '0 0 0.25rem 0' }}>Expected Return</p>
                          <p style={{ fontWeight: '600', margin: 0 }}>{investment.expectedReturn.toFixed(2)} NIMO</p>
                        </div>
                        <div>
                          <p style={{ opacity: 0.7, margin: '0 0 0.25rem 0' }}>Maturity</p>
                          <p style={{ fontWeight: '600', margin: 0 }}>
                            {new Date(investment.maturityDate).toLocaleDateString()}
                          </p>
                        </div>
                        <div>
                          <p style={{ opacity: 0.7, margin: '0 0 0.25rem 0' }}>APY</p>
                          <p style={{ fontWeight: '600', color: '#00ff88', margin: 0 }}>{investment.yield}%</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{
                  borderRadius: '8px',
                  border: '1px solid rgba(255,255,255,0.1)',
                  backgroundColor: 'rgba(255,255,255,0.05)',
                  padding: '2rem',
                  textAlign: 'center'
                }}>
                  <svg
                    style={{
                      margin: '0 auto',
                      width: '3rem',
                      height: '3rem',
                      opacity: 0.6,
                      marginBottom: '1rem'
                    }}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      vectorEffect="non-scaling-stroke"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                  <h3 style={{
                    fontSize: '1.1rem',
                    marginBottom: '0.5rem',
                    opacity: 0.8
                  }}>
                    No investments yet
                  </h3>
                  <p style={{
                    opacity: 0.6,
                    fontSize: '0.9rem',
                    marginBottom: '1.5rem'
                  }}>
                    You haven't invested in any bonds yet. Start by exploring available bonds.
                  </p>
                  <button
                    onClick={() => setActiveTab('bonds')}
                    style={{
                      padding: '0.75rem 1.5rem',
                      backgroundColor: '#ff7b00',
                      border: 'none',
                      borderRadius: '6px',
                      color: 'white',
                      fontSize: '0.9rem',
                      cursor: 'pointer',
                      fontWeight: '600'
                    }}
                  >
                    Explore Bonds
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

interface IdentitySectionProps {
  walletAddress: string;
  tokenBalance: number;
  nftData: NFTData | null;
  onNFTCreated: (nftData: NFTData) => void;
}

export const IdentitySection: React.FC<IdentitySectionProps> = ({
  walletAddress,
  tokenBalance,
  nftData,
  onNFTCreated
}) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleCreateNFT = async () => {
    setIsLoading(true);
    try {
      // Simulate NFT creation
      await new Promise(resolve => setTimeout(resolve, 2000));
      const newNFT: NFTData = {
        id: Date.now(),
        walletAddress,
        tokenBalance,
        traits: {
          reputation: Math.floor(Math.random() * 1000),
          verificationLevel: 'Verified',
          joinDate: new Date().toISOString()
        }
      };
      onNFTCreated(newNFT);
    } catch (error) {
      console.error('Error creating NFT:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem 0' }}>
      <h2 style={{ fontSize: '1.5rem', marginBottom: '2rem', color: '#ff7b00' }}>��� Digital Identity</h2>
      {nftData ? (
        <div style={{
          backgroundColor: 'rgba(255,255,255,0.05)',
          padding: '2rem',
          borderRadius: '16px',
          border: '1px solid rgba(255,255,255,0.1)'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.2rem' }}>Your Digital Identity</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.9rem' }}>
            <div>
              <div style={{ opacity: 0.7, marginBottom: '0.25rem' }}>Wallet</div>
              <div style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                {walletAddress.substring(0, 6)}...{walletAddress.substring(walletAddress.length - 4)}
              </div>
            </div>
            <div>
              <div style={{ opacity: 0.7, marginBottom: '0.25rem' }}>Reputation Score</div>
              <div style={{ fontWeight: '600', color: '#00ff88' }}>
                {nftData.traits.reputation}/1000
              </div>
            </div>
            <div>
              <div style={{ opacity: 0.7, marginBottom: '0.25rem' }}>Verification</div>
              <div style={{ fontWeight: '600' }}>{nftData.traits.verificationLevel}</div>
            </div>
            <div>
              <div style={{ opacity: 0.7, marginBottom: '0.25rem' }}>Member Since</div>
              <div>{new Date(nftData.traits.joinDate).toLocaleDateString()}</div>
            </div>
          </div>
        </div>
      ) : (
        <div style={{
          backgroundColor: 'rgba(255,255,255,0.05)',
          padding: '2rem',
          borderRadius: '16px',
          border: '1px solid rgba(255,255,255,0.1)',
          textAlign: 'center'
        }}>
          <p style={{ marginBottom: '1.5rem', opacity: 0.8 }}>
            You don't have a digital identity yet. Create one to access all features.
          </p>
          <button
            onClick={handleCreateNFT}
            disabled={isLoading}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: isLoading ? 'rgba(255,123,0,0.5)' : '#ff7b00',
              border: 'none',
              borderRadius: '6px',
              color: 'white',
              fontSize: '0.9rem',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              fontWeight: '600'
            }}
          >
            {isLoading ? 'Creating...' : 'Create Digital Identity'}
          </button>
        </div>
      )}
    </div>
  );
};

// Dashboard Section
interface DashboardSectionProps {
  contributions: Contribution[];
  bonds: Bond[];
  tokenBalance: number;
  walletAddress: string | null;
}

export const DashboardSection: React.FC<DashboardSectionProps> = ({ contributions, bonds, tokenBalance, walletAddress }) => {
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
            {bonds.length}
          </div>
          <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>Available Bonds</div>
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

// Analytics Section
interface AnalyticsSectionProps {
  contributions: Contribution[];
  bonds: Bond[];
}

export const AnalyticsSection: React.FC<AnalyticsSectionProps> = ({ contributions, bonds }) => {
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

// Profile Section
interface ProfileSectionProps {
  walletAddress: string | null;
  nftData: NFTData | null;
  contributions: Contribution[];
}

export const ProfileSection: React.FC<ProfileSectionProps> = ({ walletAddress, nftData, contributions }) => {
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
