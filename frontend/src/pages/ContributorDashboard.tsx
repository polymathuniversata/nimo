import React from 'react';
import { Navbar } from '@/components/Navbar';
import { IdentityNftCard } from '@/components/IdentityNftCard';
import { ContributionCard } from '@/components/ContributionCard';
import { SubmitContribution } from '@/components/SubmitContribution';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, Users, Zap, Award, Target, Plus, Star, CheckCircle } from 'lucide-react';

const ContributorDashboard = () => {
  // Sample data for contributors
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
      status: 'verified' as const,
      impact: 'moderate' as const,
      tokenReward: 150,
      evidenceUrl: 'https://photos.google.com/workshops'
    },
    {
      id: 'contrib-101',
      title: 'Open Source Contribution',
      category: 'open_source',
      description: 'Contributed to Nimo core repository with bug fixes and feature enhancements.',
      status: 'verified' as const,
      impact: 'significant' as const,
      tokenReward: 420,
      evidenceUrl: 'https://github.com/nimo/nimo-core/pull/123',
      verifierName: 'Nimo_Core'
    }
  ];

  const leaderboardData = [
    { rank: 1, name: 'Amara Johnson', contributions: 45, tokens: 12500 },
    { rank: 2, name: 'Kofi Mensah', contributions: 38, tokens: 9800 },
    { rank: 3, name: 'Zara Ahmed', contributions: 32, tokens: 8750 },
    { rank: 4, name: 'Jelani Brown', contributions: 28, tokens: 7200 },
    { rank: 5, name: 'Nia Williams', contributions: 25, tokens: 6500 },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary/5 to-secondary/5 py-20">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              Contributor Dashboard
              <span className="block bg-gradient-primary bg-clip-text text-transparent">
                Build Your Legacy
              </span>
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Track your verified contributions, earn reputation tokens, and climb the leaderboard in the Nimo ecosystem.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-gradient-primary text-lg px-8">
                <Plus className="w-5 h-5 mr-2" />
                Submit New Contribution
              </Button>
              <Button variant="outline" size="lg" className="text-lg px-8">
                <TrendingUp className="w-5 h-5 mr-2" />
                View Leaderboard
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
              <div className="text-3xl font-bold text-primary mb-2">156</div>
              <div className="text-sm text-muted-foreground">Total Contributions</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-token-gold mb-2">12,450</div>
              <div className="text-sm text-muted-foreground">NIMO Tokens Earned</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-verification-green mb-2">142</div>
              <div className="text-sm text-muted-foreground">Verified Contributions</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-impact-blue mb-2">#8</div>
              <div className="text-sm text-muted-foreground">Global Ranking</div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Dashboard */}
      <main className="container mx-auto px-4 py-12">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Profile & Quick Actions */}
          <div className="space-y-6">
            <IdentityNftCard
              userName="Amara Johnson"
              userId="user-456"
              tokenBalance={12450}
              verifiedContributions={142}
              reputation="Top Contributor"
            />

            <Card className="shadow-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Star className="w-5 h-5 text-yellow-500" />
                  Contributor Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full justify-start">
                  <Plus className="w-4 h-4 mr-2" />
                  Submit Contribution
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Verify Pending
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Users className="w-4 h-4 mr-2" />
                  Mentor Others
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Award className="w-4 h-4 mr-2" />
                  Claim Rewards
                </Button>
              </CardContent>
            </Card>

            {/* Achievement Badges */}
            <Card className="shadow-card">
              <CardHeader>
                <CardTitle>Achievements</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                    <Star className="w-3 h-3 mr-1" />
                    Top 10 Contributor
                  </Badge>
                  <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    100+ Verifications
                  </Badge>
                  <Badge variant="secondary" className="bg-green-100 text-green-800">
                    <Target className="w-3 h-3 mr-1" />
                    Community Builder
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Middle Column - Contributions */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Your Contributions</h2>
              <Badge variant="secondary" className="text-sm">
                {sampleContributions.length} Recent
              </Badge>
            </div>

            {sampleContributions.map((contribution) => (
              <ContributionCard key={contribution.id} {...contribution} />
            ))}

            <SubmitContribution />
          </div>

          {/* Right Column - Leaderboard */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Top Contributors</h2>
              <Badge variant="outline" className="text-sm">
                This Month
              </Badge>
            </div>

            <Card className="shadow-card">
              <CardContent className="p-6">
                <div className="space-y-4">
                  {leaderboardData.map((user) => (
                    <div key={user.rank} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-sm font-bold">
                          {user.rank}
                        </div>
                        <div>
                          <div className="font-semibold">{user.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {user.contributions} contributions
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-token-gold">{user.tokens.toLocaleString()}</div>
                        <div className="text-xs text-muted-foreground">NIMO</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-card">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-3">
                  <TrendingUp className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-semibold mb-2">Climb the Ranks</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Submit more contributions to increase your ranking and earn bonus rewards
                </p>
                <Button variant="outline" size="sm">
                  View Full Leaderboard
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ContributorDashboard;