import React from 'react';
import { Navbar } from '@/components/Navbar';
import { ImpactBondCard } from '@/components/ImpactBondCard';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, Users, Building, Target, Plus, DollarSign, BarChart3 } from 'lucide-react';

const OrganizationDashboard = () => {
  // Sample data for organizations
  const organizationProjects = [
    {
      id: 'org-proj-123',
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
      id: 'org-proj-456',
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
      id: 'org-proj-789',
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

  const fundingStats = {
    totalRaised: 247500,
    totalProjects: 12,
    activeInvestors: 89,
    averageProjectSize: 35000
  };

  const recentInvestments = [
    { investor: 'TechForward Africa', amount: 15000, project: 'Lagos Tech Hub', date: '2024-09-01' },
    { investor: 'Diaspora Impact Fund', amount: 25000, project: 'Ghana Internet', date: '2024-08-28' },
    { investor: 'WomenTech Global', amount: 10000, project: 'Kenya Women Program', date: '2024-08-25' },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary/5 to-secondary/5 py-20">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              Organization Dashboard
              <span className="block bg-gradient-primary bg-clip-text text-transparent">
                Drive Social Impact
              </span>
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Launch impact bonds, attract diaspora investment, and track your social impact metrics in real-time.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-gradient-primary text-lg px-8">
                <Plus className="w-5 h-5 mr-2" />
                Create Impact Bond
              </Button>
              <Button variant="outline" size="lg" className="text-lg px-8">
                <BarChart3 className="w-5 h-5 mr-2" />
                View Analytics
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
              <div className="text-3xl font-bold text-primary mb-2">${fundingStats.totalRaised.toLocaleString()}</div>
              <div className="text-sm text-muted-foreground">Total Funds Raised</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-token-gold mb-2">{fundingStats.totalProjects}</div>
              <div className="text-sm text-muted-foreground">Active Projects</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-verification-green mb-2">{fundingStats.activeInvestors}</div>
              <div className="text-sm text-muted-foreground">Active Investors</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-impact-blue mb-2">${fundingStats.averageProjectSize.toLocaleString()}</div>
              <div className="text-sm text-muted-foreground">Avg Project Size</div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Dashboard */}
      <main className="container mx-auto px-4 py-12">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Organization Profile & Actions */}
          <div className="space-y-6">
            <Card className="shadow-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building className="w-5 h-5 text-primary" />
                  TechForward Africa
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Organization Type</p>
                    <p className="font-semibold">Non-Profit</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Focus Areas</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      <Badge variant="secondary">Education</Badge>
                      <Badge variant="secondary">Technology</Badge>
                      <Badge variant="secondary">Youth Empowerment</Badge>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Impact Score</p>
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-2 bg-muted rounded-full">
                        <div className="w-4/5 h-full bg-primary rounded-full"></div>
                      </div>
                      <span className="text-sm font-semibold">85/100</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5 text-primary" />
                  Organization Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full justify-start">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Impact Bond
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Users className="w-4 h-4 mr-2" />
                  Find Investors
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <BarChart3 className="w-4 h-4 mr-2" />
                  Impact Reports
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <DollarSign className="w-4 h-4 mr-2" />
                  Withdraw Funds
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Middle Column - Active Projects */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Active Projects</h2>
              <Badge variant="secondary" className="text-sm">
                {organizationProjects.length} Live
              </Badge>
            </div>

            {organizationProjects.map((project) => (
              <ImpactBondCard key={project.id} {...project} />
            ))}

            <Card className="shadow-card border-dashed border-2">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-3">
                  <Plus className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-semibold mb-2">Launch New Project</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Create an impact bond to attract diaspora investment for your next initiative
                </p>
                <Button variant="outline" size="sm">
                  Get Started
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Funding & Analytics */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Recent Investments</h2>
              <Badge variant="outline" className="text-sm">
                Last 30 Days
              </Badge>
            </div>

            <Card className="shadow-card">
              <CardContent className="p-6">
                <div className="space-y-4">
                  {recentInvestments.map((investment, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="font-semibold text-sm">{investment.investor}</div>
                        <div className="text-xs text-muted-foreground">{investment.project}</div>
                        <div className="text-xs text-muted-foreground">{investment.date}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-token-gold">${investment.amount.toLocaleString()}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Funding Analytics */}
            <Card className="shadow-card">
              <CardHeader>
                <CardTitle>Funding Analytics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Average Time to Fund</span>
                    <span className="font-semibold">14 days</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Success Rate</span>
                    <span className="font-semibold text-verification-green">87%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Avg Investor Amount</span>
                    <span className="font-semibold">$8,500</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Total Diaspora Investors</span>
                    <span className="font-semibold">156</span>
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

export default OrganizationDashboard;