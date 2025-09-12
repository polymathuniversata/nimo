import React from 'react';
import { Navbar } from '@/components/Navbar';
import { IdentityNftCard } from '@/components/IdentityNftCard';
import { ContributionCard } from '@/components/ContributionCard';
import { ImpactBondCard } from '@/components/ImpactBondCard';
import { SubmitContribution } from '@/components/SubmitContribution';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp,
  Users,
  Zap,
  Globe,
  Award,
  Target,
  Plus,
  Sparkles,
  Trophy,
  BarChart3,
  ArrowRight,
  CheckCircle,
  Clock,
  Star
} from 'lucide-react';

const UserDashboard = () => {
  console.log('UserDashboard component rendering...');

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
      <section className="relative overflow-hidden bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5">
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
        <div className="layout-container py-20 lg:py-32">
          <div className="text-center max-w-5xl mx-auto">
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6 animate-fade-in">
              <Sparkles className="w-4 h-4 mr-2" />
              Welcome Back to Your Dashboard
            </div>
            <h1 className="responsive-text-hero font-bold mb-6 bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent animate-fade-in-up">
              Your Nimo Dashboard
            </h1>
            <p className="responsive-text-body text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed animate-fade-in-up animation-delay-200">
              Track your impact, verify contributions, and unlock opportunities in the global economy through blockchain-powered identity and AI verification.
            </p>
            <div className="responsive-flex-actions animate-fade-in-up animation-delay-400">
              <Button size="lg" className="bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 text-lg px-8 py-4 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1">
                <Zap className="w-5 h-5 mr-2" />
                Create Identity NFT
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
              <Button variant="outline" size="lg" className="text-lg px-8 py-4 border-2 hover:bg-primary hover:text-white transition-all duration-300 transform hover:scale-105 hover:-translate-y-1">
                <Globe className="w-5 h-5 mr-2" />
                Explore Marketplace
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 lg:py-20 bg-gradient-to-br from-muted/30 to-background relative overflow-hidden">
        <div className="absolute inset-0 bg-dots-pattern opacity-10"></div>
        <div className="container mx-auto px-4 relative">
          <div className="text-center mb-12">
            <Badge variant="outline" className="mb-4 px-4 py-2 text-sm font-medium bg-primary/10 text-primary border-primary/20">
              Your Impact Metrics
            </Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
              Platform Statistics
            </h2>
          </div>

          <div className="responsive-grid-stats">
            <Card className="p-6 bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group">
              <div className="text-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                  <Users className="w-8 h-8 text-white" />
                </div>
                <div className="text-3xl md:text-4xl font-bold mb-2 bg-gradient-to-r from-primary to-secondary bg-clip-text">12,500+</div>
                <div className="text-sm text-muted-foreground font-medium">Verified Identities</div>
                <div className="w-full bg-primary/20 rounded-full h-1 mt-4">
                  <div className="bg-gradient-to-r from-primary to-secondary h-1 rounded-full w-4/5"></div>
                </div>
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-secondary/5 to-secondary/10 border-secondary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group">
              <div className="text-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-secondary to-secondary/80 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                  <Trophy className="w-8 h-8 text-white" />
                </div>
                <div className="text-3xl md:text-4xl font-bold mb-2 bg-gradient-to-r from-secondary to-accent bg-clip-text">2.4M</div>
                <div className="text-sm text-muted-foreground font-medium">NIMO Tokens Distributed</div>
                <div className="w-full bg-secondary/20 rounded-full h-1 mt-4">
                  <div className="bg-gradient-to-r from-secondary to-accent h-1 rounded-full w-3/5"></div>
                </div>
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-accent/5 to-accent/10 border-accent/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group">
              <div className="text-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-accent to-accent/80 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                  <CheckCircle className="w-8 h-8 text-white" />
                </div>
                <div className="text-3xl md:text-4xl font-bold mb-2 bg-gradient-to-r from-accent to-primary bg-clip-text">8,900+</div>
                <div className="text-sm text-muted-foreground font-medium">Contributions Verified</div>
                <div className="w-full bg-accent/20 rounded-full h-1 mt-4">
                  <div className="bg-gradient-to-r from-accent to-primary h-1 rounded-full w-4/5"></div>
                </div>
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-primary/5 to-secondary/10 border-primary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group">
              <div className="text-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                  <BarChart3 className="w-8 h-8 text-white" />
                </div>
                <div className="text-3xl md:text-4xl font-bold mb-2 bg-gradient-to-r from-primary to-secondary bg-clip-text">$580K</div>
                <div className="text-sm text-muted-foreground font-medium">Impact Bonds Funded</div>
                <div className="w-full bg-primary/20 rounded-full h-1 mt-4">
                  <div className="bg-gradient-to-r from-primary to-secondary h-1 rounded-full w-2/3"></div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* Main Dashboard */}
      <main className="layout-container py-8 md:py-12 lg:py-16 xl:py-20">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8 xl:gap-12">
          {/* Left Column - Identity & Quick Actions */}
          <div className="space-y-8">
            <IdentityNftCard
              userName="Kwame Asante"
              userId="user-123"
              tokenBalance={320}
              verifiedContributions={12}
              reputation="Community Builder"
            />

            <Card className="shadow-lg border-primary/20 bg-gradient-to-br from-primary/5 to-primary/10 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-3 text-xl">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                    <Award className="w-5 h-5 text-white" />
                  </div>
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button variant="outline" className="w-full justify-start py-3 hover:bg-primary hover:text-white transition-all duration-300 transform hover:scale-105 hover:-translate-y-1">
                  <TrendingUp className="w-5 h-5 mr-3" />
                  Submit Contribution
                  <ArrowRight className="ml-auto w-4 h-4" />
                </Button>
                <Button variant="outline" className="w-full justify-start py-3 hover:bg-secondary hover:text-white transition-all duration-300 transform hover:scale-105 hover:-translate-y-1">
                  <Users className="w-5 h-5 mr-3" />
                  Join DAO Governance
                  <ArrowRight className="ml-auto w-4 h-4" />
                </Button>
                <Button variant="outline" className="w-full justify-start py-3 hover:bg-accent hover:text-white transition-all duration-300 transform hover:scale-105 hover:-translate-y-1">
                  <Target className="w-5 h-5 mr-3" />
                  Browse Impact Bonds
                  <ArrowRight className="ml-auto w-4 h-4" />
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Middle Column - Contributions */}
          <div className="space-y-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text">
                  Your Contributions
                </h2>
                <p className="text-muted-foreground">Track and manage your verified impact</p>
              </div>
              <Badge variant="secondary" className="text-sm px-3 py-1 bg-primary/10 text-primary border-primary/20">
                {sampleContributions.length} Total
              </Badge>
            </div>

            <div className="space-y-6">
              {sampleContributions.map((contribution) => (
                <ContributionCard key={contribution.id} {...contribution} />
              ))}
            </div>

            <div className="bg-gradient-to-r from-primary/10 to-secondary/10 rounded-2xl p-6 border border-primary/20">
              <SubmitContribution />
            </div>
          </div>

          {/* Right Column - Impact Bonds */}
          <div className="space-y-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text">
                  Impact Bonds
                </h2>
                <p className="text-muted-foreground">Support community projects</p>
              </div>
              <Badge variant="outline" className="text-sm px-3 py-1 border-secondary text-secondary bg-secondary/10">
                Live Opportunities
              </Badge>
            </div>

            <div className="space-y-6">
              {sampleBonds.map((bond) => (
                <ImpactBondCard key={bond.id} {...bond} />
              ))}
            </div>

            <Card className="shadow-lg border-dashed border-2 border-primary/30 bg-gradient-to-br from-primary/5 to-secondary/5 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2">
              <CardContent className="p-8 text-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center mx-auto mb-4 hover:scale-110 transition-transform duration-300">
                  <Plus className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-3">Create Impact Bond</h3>
                <p className="text-muted-foreground mb-6 leading-relaxed">
                  Launch your own community project and attract diaspora investment with transparent impact tracking
                </p>
                <Button className="bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1">
                  <Star className="w-4 h-4 mr-2" />
                  Get Started
                  <ArrowRight className="ml-2 w-4 h-4" />
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
};

export default UserDashboard;