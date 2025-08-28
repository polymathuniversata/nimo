import React, { useState, useEffect } from 'react';
import { useWallet } from '@/hooks/useWallet';
import { Button } from '@/components/ui/button';
import { toast } from '@/components/ui/use-toast';

// Mock data for bonds
const MOCK_BONDS = [
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
  contributions: any[];
  onOpenModal: () => void;
}

export const ContributionsSection: React.FC<ContributionsSectionProps> = ({ contributions, onOpenModal }) => {
  return (
    <div className="section-container">
      <div className="section-header">
        <h2>My Contributions</h2>
        <button 
          onClick={onOpenModal}
          className="primary-button"
        >
          + New Contribution
        </button>
      </div>
      <div className="contributions-list">
        {contributions.length > 0 ? (
          contributions.map((contribution) => (
            <div key={contribution.id} className="contribution-card">
              <h3>{contribution.title}</h3>
              <p>{contribution.description}</p>
              <div className="contribution-meta">
                <span>Status: {contribution.status}</span>
                <span>Reward: {contribution.reward} NIMO</span>
              </div>
            </div>
          ))
        ) : (
          <p>No contributions yet. Start by creating your first contribution!</p>
        )}
      </div>
    </div>
  );
};

interface MarketplaceSectionProps {
  bonds?: any[];
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

  const [activeTab, setActiveTab] = useState('bonds');
  const [searchQuery, setSearchQuery] = useState('');
  const [bonds, setBonds] = useState(propBonds || MOCK_BONDS);
  const [isLoading, setIsLoading] = useState(false);
  const [myInvestments, setMyInvestments] = useState<any[]>([]);

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
      const investment = {
        ...bond,
        investmentAmount: amount,
        investmentDate: new Date().toISOString(),
        expectedReturn: amount * (1 + bond.yield / 100)
      };
      
      setMyInvestments(prev => [...prev, investment]);
      
      toast({
        title: 'Investment Successful',
        description: `You've successfully invested ${amount} NIMO in ${bond.name}`,
      });
      
    } catch (error) {
      toast({
        title: 'Investment Failed',
        description: error instanceof Error ? error.message : 'Failed to process investment',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Format wallet address
  const formatAddress = (addr: string) => 
    `${addr.substring(0, 6)}...${addr.substring(addr.length - 4)}`;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">NIMO Marketplace</h2>
          <p className="text-muted-foreground">Discover and invest in community bonds</p>
        </div>
        
        <div className="relative w-full md:w-64">
          <input
            type="text"
            placeholder="Search bonds..."
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-input bg-background text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground"
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
        <div className="rounded-xl border border-dashed p-8 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-6 w-6 text-primary"
            >
              <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"></path>
              <path d="M3 5v14a2 2 0 0 0 2 2h16v-5"></path>
              <path d="M18 12a2 2 0 1 0 0-4 2 2 0 0 0 0 4z"></path>
            </svg>
          </div>
          <h3 className="mt-4 text-lg font-medium">Connect your wallet</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Connect your wallet to explore and invest in community bonds
          </p>
          <button 
            onClick={connectWallet}
            className="mt-4 inline-flex items-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            disabled={isLoading}
          >
            {isLoading ? 'Connecting...' : 'Connect Wallet'}
          </button>
          
          {chainId && (
            <div className="mt-4 text-xs text-muted-foreground">
              Connected to: {networkName || 'Unknown Network'} ({chainId})
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          <div className="border-b">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('bonds')}
                className={`whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium ${activeTab === 'bonds' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:border-muted-foreground hover:text-foreground'}`}
              >
                All Bonds
              </button>
              <button
                onClick={() => setActiveTab('my-investments')}
                className={`whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium ${activeTab === 'my-investments' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:border-muted-foreground hover:text-foreground'}`}
              >
                My Investments
              </button>
            </nav>
          </div>

          {activeTab === 'bonds' && (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {filteredBonds.length > 0 ? (
                filteredBonds.map((bond) => (
                  <div key={bond.id} className="group relative overflow-hidden rounded-xl border bg-card p-6 shadow-sm transition-all hover:shadow-md">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-medium">{bond.name}</h3>
                      <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
                        {bond.yield}% APY
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-muted-foreground">
                      {bond.description || 'Community development bond with competitive returns'}
                    </p>
                    <div className="mt-4 space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Min. Investment</span>
                        <span className="font-medium">{bond.minInvestment} NIMO</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Maturity</span>
                        <span className="font-medium">{new Date(bond.maturityDate).toLocaleDateString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Available</span>
                        <span className="font-medium">{bond.available} / {bond.totalSupply}</span>
                      </div>
                    </div>
                    <div className="mt-6">
                      <button 
                        onClick={() => handleInvest(bond.id, bond.minInvestment)}
                        disabled={isLoading || bond.available <= 0}
                        className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isLoading ? 'Processing...' : `Invest ${bond.minInvestment} NIMO`}
                      </button>
                      {bond.available <= 0 && (
                        <p className="mt-2 text-xs text-center text-amber-600">
                          Bond is currently sold out
                        </p>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-full py-12 text-center">
                  <svg
                    className="mx-auto h-12 w-12 text-muted-foreground"
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
                  <h3 className="mt-2 text-sm font-medium text-foreground">No bonds found</h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    {searchQuery ? 'No bonds match your search.' : 'No bonds available at the moment. Check back later!'}
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'my-investments' && (
            <div className="space-y-4">
              <div className="bg-card p-4 rounded-lg border">
                <h3 className="font-medium">Wallet Information</h3>
                <div className="mt-2 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Connected Wallet</span>
                    <span className="font-mono">{address ? formatAddress(address) : 'Not connected'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Network</span>
                    <span>{networkName || 'Unknown'}</span>
                  </div>
                </div>
                <button 
                  onClick={disconnectWallet}
                  className="mt-4 w-full text-sm text-red-600 hover:text-red-700"
                >
                  Disconnect Wallet
                </button>
              </div>

              {myInvestments.length > 0 ? (
                <div className="space-y-4">
                  {myInvestments.map((investment) => (
                    <div key={`${investment.id}-${investment.investmentDate}`} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-medium">{investment.name}</h4>
                          <p className="text-sm text-muted-foreground">
                            Invested: {new Date(investment.investmentDate).toLocaleDateString()}
                          </p>
                        </div>
                        <span className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                          Active
                        </span>
                      </div>
                      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-muted-foreground">Amount</p>
                          <p className="font-medium">{investment.investmentAmount} NIMO</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Expected Return</p>
                          <p className="font-medium">{investment.expectedReturn.toFixed(2)} NIMO</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Maturity</p>
                          <p className="font-medium">{new Date(investment.maturityDate).toLocaleDateString()}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">APY</p>
                          <p className="font-medium text-green-600">{investment.yield}%</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="rounded-lg border bg-card p-8 text-center">
                  <svg
                    className="mx-auto h-12 w-12 text-muted-foreground"
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
                  <h3 className="mt-2 text-sm font-medium text-foreground">No investments yet</h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    You haven't invested in any bonds yet. Start by exploring available bonds.
                  </p>
                  <div className="mt-6">
                    <button
                      onClick={() => setActiveTab('bonds')}
                      className="inline-flex items-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
                    >
                      Explore Bonds
                    </button>
                  </div>
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
  nftData: any;
  onNFTCreated: (nftData: any) => void;
}

export const IdentitySection: React.FC<IdentitySectionProps> = ({
  walletAddress,
  tokenBalance,
  nftData,
  onNFTCreated
}) => {
  const [isLoading, setIsLoading] = React.useState(false);

  const handleCreateNFT = async () => {
    setIsLoading(true);
    try {
      // Simulate NFT creation
      await new Promise(resolve => setTimeout(resolve, 2000));
      const newNFT = {
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
    <div className="section-container">
      <h2>Digital Identity</h2>
      {nftData ? (
        <div className="identity-card">
          <h3>Your Digital Identity</h3>
          <p>Wallet: {walletAddress}</p>
          <p>Reputation Score: {nftData.traits.reputation}/1000</p>
          <p>Verification: {nftData.traits.verificationLevel}</p>
          <p>Member Since: {new Date(nftData.traits.joinDate).toLocaleDateString()}</p>
        </div>
      ) : (
        <div className="create-identity">
          <p>You don't have a digital identity yet. Create one to access all features.</p>
          <button 
            onClick={handleCreateNFT} 
            disabled={isLoading}
            className="primary-button"
          >
            {isLoading ? 'Creating...' : 'Create Digital Identity'}
          </button>
        </div>
      )}
    </div>
  );
};
