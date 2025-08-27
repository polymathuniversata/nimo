import React from 'react';
import { Navbar } from '@/components/Navbar';
import { IdentityNftCard } from '@/components/IdentityNftCard';
import { ContributionCard } from '@/components/ContributionCard';
import { ImpactBondCard } from '@/components/ImpactBondCard';
import { SubmitContribution } from '@/components/SubmitContribution';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, Users, Zap, Globe, Award, Target, Plus } from 'lucide-react';
import heroBackground from '@/assets/hero-bg.jpg';

const Index = () => {
  // Sample data
  const sampleContributions = [
    {
      id: 'contrib-456',
      title: 'KRNL Hackathon Project',
      category: 'coding',
      description: 'Built a decentralized learning platform for African universities using blockchain technology.',
      status: 'verified' as const,
      impact: 'significant' as const,
      tokenReward: 280,
      evidenceUrl: 'https://github.com/kwame/krnl-project',
      verifierName: 'KRNL_Org'
    },
    {
      id: 'contrib-789',
      title: 'Community Workshop Series',
      category: 'community_building',
      description: 'Organized 5 blockchain workshops reaching 200+ young developers across Lagos.',
      status: 'pending' as const,
      impact: 'moderate' as const,
      tokenReward: 150,
      evidenceUrl: 'https://photos.google.com/workshops'
    }
  ];

  const sampleBonds = [
    {
      id: 'bond-123',
      title: 'Lagos Tech Hub Expansion',
      description: 'Expanding co-working spaces and providing free blockchain training to 500 youth in Lagos.',
      location: 'Lagos, Nigeria',
      targetAmount: 50000,
      currentAmount: 32000,
      deadline: '2024-12-31',
      category: 'Education',
      impactMetrics: ['500 Youth Trained', '50 Jobs Created', '10 Startups Launched']
    },
    {
      id: 'bond-456',
      title: 'Ghana Rural Internet Initiative',
      description: 'Bringing high-speed internet to 20 rural communities in Ghana to enable remote work opportunities.',
      location: 'Accra Region, Ghana',
      targetAmount: 75000,
      currentAmount: 18500,
      deadline: '2025-06-15',
      category: 'Infrastructure',
      impactMetrics: ['20 Communities Connected', '1000 People Online', '200 Remote Jobs']
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-20"
          style={{ backgroundImage: `url(${heroBackground})` }}
        />
        <div className="absolute inset-0 bg-gradient-hero" />
        <div className="relative container mx-auto px-4 py-20">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              Decentralized Identity for
              <span className="block bg-gradient-primary bg-clip-text text-transparent">
                African Innovation
              </span>
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Verify your contributions, earn tokens, and unlock opportunities in the global economy through blockchain-powered identity and AI verification.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-gradient-primary text-lg px-8">
                <Zap className="w-5 h-5 mr-2" />
                Create Identity NFT
              </Button>
              <Button variant="outline" size="lg" className="text-lg px-8">
                <Globe className="w-5 h-5 mr-2" />
                Explore Marketplace
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 bg-muted/50">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary mb-2">12,500+</div>
              <div className="text-sm text-muted-foreground">Verified Identities</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-token-gold mb-2">2.4M</div>
              <div className="text-sm text-muted-foreground">NIMO Tokens Distributed</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-verification-green mb-2">8,900+</div>
              <div className="text-sm text-muted-foreground">Contributions Verified</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-impact-blue mb-2">$580K</div>
              <div className="text-sm text-muted-foreground">Impact Bonds Funded</div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Dashboard */}
      <main className="container mx-auto px-4 py-12">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Identity & Quick Actions */}
          <div className="space-y-6">
            <IdentityNftCard
              userName="Kwame Asante"
              userId="user-123"
              tokenBalance={320}
              verifiedContributions={12}
              reputation="Community Builder"
            />
            
            <Card className="shadow-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="w-5 h-5 text-token-gold" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full justify-start">
                  <TrendingUp className="w-4 h-4 mr-2" />
                  Submit Contribution
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Users className="w-4 h-4 mr-2" />
                  Join DAO Governance
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Target className="w-4 h-4 mr-2" />
                  Browse Impact Bonds
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Middle Column - Contributions */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Your Contributions</h2>
              <Badge variant="secondary" className="text-sm">
                {sampleContributions.length} Total
              </Badge>
            </div>
            
            {sampleContributions.map((contribution) => (
              <ContributionCard key={contribution.id} {...contribution} />
            ))}
            
            <SubmitContribution />
          </div>

          {/* Right Column - Impact Bonds */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Impact Bonds</h2>
              <Badge variant="outline" className="text-sm border-impact-blue text-impact-blue">
                Live Opportunities
              </Badge>
            </div>
            
            {sampleBonds.map((bond) => (
              <ImpactBondCard key={bond.id} {...bond} />
            ))}
            
            <Card className="shadow-card border-dashed border-2">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-3">
                  <Plus className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-semibold mb-2">Create Impact Bond</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Launch your own community project and attract diaspora investment
                </p>
                <Button variant="outline" size="sm">
                  Get Started
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;
