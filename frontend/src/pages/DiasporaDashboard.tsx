import React from 'react';
import { Navbar } from '@/components/Navbar';
import { ImpactBondCard } from '@/components/ImpactBondCard';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, Users, Globe, Target, Heart, DollarSign, BarChart3 } from 'lucide-react';

const DiasporaDashboard = () => {
  // Sample data for diaspora supporters
  const availableProjects = [
    {
      id: 'diaspora-proj-123',
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
      id: 'diaspora-proj-456',
      title: 'Ghana Rural Internet Initiative',
      description: 'Bringing high-speed internet to 20 rural communities in Ghana to enable remote work opportunities.',
      location: 'Accra Region, Ghana',
      targetAmount: 75000,
      currentAmount: 18500,
      deadline: '2025-06-15',
      category: 'Infrastructure',
      impactMetrics: ['20 Communities Connected', '1000 People Online', '200 Remote Jobs']
    },
    {
      id: 'diaspora-proj-789',
      title: 'Kenya Women in Tech Program',
      description: 'Supporting 100 women entrepreneurs with mentorship, funding, and technical training.',
      location: 'Nairobi, Kenya',
      targetAmount: 30000,
      currentAmount: 12000,
      deadline: '2025-03-30',
      category: 'Empowerment',
      impactMetrics: ['100 Women Supported', '25 Businesses Launched', '15 Tech Startups']
    }
  ];

  const investmentPortfolio = [
    { project: 'Lagos Tech Hub', amount: 5000, impact: 'High', status: 'Active' },
    { project: 'Ghana Internet', amount: 7500, impact: 'High', status: 'Active' },
    { project: 'Women Tech Program', amount: 3000, impact: 'Moderate', status: 'Completed' },
  ];

  const impactStats = {
    totalInvested: 15500,
    peopleImpacted: 1250,
    projectsSupported: 8,
    communitiesHelped: 15
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary/5 to-secondary/5 py-20">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              Diaspora Dashboard
              <span className="block bg-gradient-primary bg-clip-text text-transparent">
                Invest in Your Roots
              </span>
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Support community projects, track your impact, and connect with organizations driving positive change in Africa.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-gradient-primary text-lg px-8">
                <Heart className="w-5 h-5 mr-2" />
                Browse Projects
              </Button>
              <Button variant="outline" size="lg" className="text-lg px-8">
                <BarChart3 className="w-5 h-5 mr-2" />
                View Impact
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
              <div className="text-3xl font-bold text-primary mb-2">${impactStats.totalInvested.toLocaleString()}</div>
              <div className="text-sm text-muted-foreground">Total Invested</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-token-gold mb-2">{impactStats.peopleImpacted.toLocaleString()}</div>
              <div className="text-sm text-muted-foreground">People Impacted</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-verification-green mb-2">{impactStats.projectsSupported}</div>
              <div className="text-sm text-muted-foreground">Projects Supported</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-impact-blue mb-2">{impactStats.communitiesHelped}</div>
              <div className="text-sm text-muted-foreground">Communities Helped</div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Dashboard */}
      <main className="container mx-auto px-4 py-12">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Portfolio & Profile */}
          <div className="space-y-6">
            <Card className="shadow-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="w-5 h-5 text-primary" />
                  Your Impact Portfolio
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {investmentPortfolio.map((investment, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                      <div>
                        <div className="font-semibold text-sm">{investment.project}</div>
                        <div className="text-xs text-muted-foreground">
                          Impact: <span className={`font-semibold ${
                            investment.impact === 'High' ? 'text-verification-green' :
                            investment.impact === 'Moderate' ? 'text-primary' : 'text-muted-foreground'
                          }`}>{investment.impact}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-token-gold">${investment.amount.toLocaleString()}</div>
                        <Badge variant="outline" className="text-xs">
                          {investment.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Heart className="w-5 h-5 text-primary" />
                  Diaspora Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full justify-start">
                  <DollarSign className="w-4 h-4 mr-2" />
                  Invest in Project
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Users className="w-4 h-4 mr-2" />
                  Connect with Orgs
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <BarChart3 className="w-4 h-4 mr-2" />
                  Impact Reports
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Target className="w-4 h-4 mr-2" />
                  Set Preferences
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Middle Column - Available Projects */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Available Projects</h2>
              <Badge variant="secondary" className="text-sm">
                {availableProjects.length} Open
              </Badge>
            </div>

            {availableProjects.map((project) => (
              <ImpactBondCard key={project.id} {...project} />
            ))}

            <Card className="shadow-card border-dashed border-2">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-3">
                  <TrendingUp className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-semibold mb-2">More Projects Coming Soon</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  New impact bonds are launched regularly. Set up notifications to stay updated.
                </p>
                <Button variant="outline" size="sm">
                  Enable Notifications
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Impact Tracking & Analytics */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Your Impact</h2>
              <Badge variant="outline" className="text-sm">
                Real-time
              </Badge>
            </div>

            <Card className="shadow-card">
              <CardHeader>
                <CardTitle>Impact Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Youth Trained</span>
                    <span className="font-semibold text-verification-green">450</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Jobs Created</span>
                    <span className="font-semibold text-primary">67</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Communities Connected</span>
                    <span className="font-semibold text-impact-blue">12</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Women Empowered</span>
                    <span className="font-semibold text-token-gold">89</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Investment Preferences */}
            <Card className="shadow-card">
              <CardHeader>
                <CardTitle>Investment Preferences</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Education Projects</span>
                    <Badge variant="secondary">High Priority</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Women Empowerment</span>
                    <Badge variant="secondary">High Priority</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Infrastructure</span>
                    <Badge variant="secondary">Medium Priority</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Healthcare</span>
                    <Badge variant="secondary">Low Priority</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card className="shadow-card">
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-verification-green"></div>
                    <span>Investment in Lagos Tech Hub completed milestone</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-primary"></div>
                    <span>Received impact report from Ghana Internet project</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-token-gold"></div>
                    <span>New project matching your preferences available</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DiasporaDashboard;