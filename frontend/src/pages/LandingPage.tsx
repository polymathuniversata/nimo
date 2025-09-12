import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Users,
  Award,
  TrendingUp,
  Globe,
  Target,
  Zap,
  CheckCircle,
  Star,
  Github,
  Twitter,
  Mail,
  ArrowRight,
  Sparkles,
  Shield,
  Heart,
  Lightbulb,
  Rocket,
  Network,
  BookOpen,
  Trophy,
  MapPin,
  Calendar,
  ChevronDown
} from 'lucide-react';

const LandingPage = () => {
  // Hot reload test - this comment should trigger a reload
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    element?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <main className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b bg-white/95 backdrop-blur-sm sticky top-0 z-50 shadow-sm" role="navigation" aria-label="Main navigation">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-8">
              <Link to="/" className="flex items-center space-x-2 focus-visible-enhanced" aria-label="Nimo homepage">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" aria-hidden="true" />
                </div>
                <h1 className="text-2xl font-bold text-primary">Nimo</h1>
              </Link>
              <div className="hidden md:flex space-x-6" role="menubar">
                <button onClick={() => scrollToSection('home')} className="text-muted-foreground hover:text-primary transition-all duration-200 hover:scale-105 focus-visible-enhanced" role="menuitem">
                  Home
                </button>
                <button onClick={() => scrollToSection('problem')} className="text-muted-foreground hover:text-primary transition-all duration-200 hover:scale-105 focus-visible-enhanced" role="menuitem">
                  Problem
                </button>
                <button onClick={() => scrollToSection('solution')} className="text-muted-foreground hover:text-primary transition-all duration-200 hover:scale-105 focus-visible-enhanced" role="menuitem">
                  Solution
                </button>
                <button onClick={() => scrollToSection('how-it-works')} className="text-muted-foreground hover:text-primary transition-all duration-200 hover:scale-105 focus-visible-enhanced" role="menuitem">
                  How It Works
                </button>
                <button onClick={() => scrollToSection('impact')} className="text-muted-foreground hover:text-primary transition-all duration-200 hover:scale-105 focus-visible-enhanced" role="menuitem">
                  Impact
                </button>
                <button onClick={() => scrollToSection('team')} className="text-muted-foreground hover:text-primary transition-all duration-200 hover:scale-105 focus-visible-enhanced" role="menuitem">
                  Team
                </button>
                <Link to="/login" className="text-muted-foreground hover:text-primary transition-all duration-200 hover:scale-105 focus-visible-enhanced" role="menuitem">
                  Login
                </Link>
                <Link to="/register" className="text-muted-foreground hover:text-primary transition-all duration-200 hover:scale-105 focus-visible-enhanced" role="menuitem">
                  Sign Up
                </Link>
              </div>
            </div>
            <Button className="bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 focus-visible-enhanced" asChild>
              <Link to="/login" aria-label="Get started with Nimo">
                <span>Get Started</span>
                <ArrowRight className="ml-2 w-4 h-4" aria-hidden="true" />
              </Link>
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section id="home" className="relative overflow-hidden bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5 min-h-screen flex items-center" aria-labelledby="hero-heading">
        <div className="absolute inset-0 bg-grid-pattern opacity-5" aria-hidden="true"></div>
        <div className="layout-container py-8 sm:py-12 md:py-16">
          <div className="text-center max-w-5xl mx-auto">
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6 animate-fade-in" role="banner">
              <Sparkles className="w-4 h-4 mr-2" aria-hidden="true" />
              Empowering African Youth Through Technology
            </div>
            <h1 id="hero-heading" className="responsive-text-hero font-bold mb-6 bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent animate-fade-in-up">
              Nimo: Unlocking Africa's Youth Potential
            </h1>
            <p className="responsive-text-body text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed animate-fade-in-up animation-delay-200">
              Decentralized Identity & Proof of Contribution for a Brighter Future
            </p>
            <div className="responsive-flex-actions animate-fade-in-up animation-delay-400">
              <Button size="lg" className="bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 text-lg px-8 py-4 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1">
                <Lightbulb className="mr-2 w-5 h-5" />
                Learn More
              </Button>
              <Button variant="outline" size="lg" className="text-lg px-8 py-4 border-2 hover:bg-primary hover:text-white transition-all duration-300 transform hover:scale-105 hover:-translate-y-1" asChild>
                <a href="/login">
                  <Rocket className="mr-2 w-5 h-5" />
                  Get Started
                </a>
              </Button>
            </div>
            <div className="mt-12 animate-bounce">
              <ChevronDown className="w-8 h-8 text-muted-foreground mx-auto cursor-pointer hover:text-primary transition-colors" onClick={() => scrollToSection('problem')} />
            </div>
          </div>
        </div>
      </section>

      <div className="section-divider"></div>

      {/* Problem Section */}
      <section id="problem" className="relative overflow-hidden bg-gradient-to-br from-muted/30 to-background section-spacing" aria-labelledby="problem-heading">
        <div className="absolute inset-0 bg-dots-pattern opacity-10" aria-hidden="true"></div>
        <div className="container mx-auto px-4 relative">
          <header className="text-center mb-16">
            <Badge variant="outline" className="mb-4 px-4 py-2 text-sm font-medium">
              The Challenge
            </Badge>
            <h2 id="problem-heading" className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
              Decentralized Identity in Africa
            </h2>
            <h3 className="text-2xl md:text-3xl text-muted-foreground mb-8">
              The Unseen Potential
            </h3>
          </header>

          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
                  <Users className="w-6 h-6 text-red-600" />
                </div>
                <div>
                  <p className="text-lg text-muted-foreground leading-relaxed">
                    Millions of talented, driven young people across Africa are building, learning, and contributing to their communities every day.
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center flex-shrink-0">
                  <Shield className="w-6 h-6 text-orange-600" />
                </div>
                <div>
                  <p className="text-lg text-muted-foreground leading-relaxed">
                    But their efforts often go unrecognized in the digital world. They lack verifiable digital identities and a way to prove their valuable contributions.
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 rounded-full bg-yellow-100 flex items-center justify-center flex-shrink-0">
                  <Target className="w-6 h-6 text-yellow-600" />
                </div>
                <div>
                  <p className="text-lg text-muted-foreground leading-relaxed">
                    This invisible barrier prevents them from accessing life-changing opportunities – jobs, grants, and global platforms.
                  </p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-6">
              <Card className="p-8 bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20 hover:shadow-lg transition-all duration-300 transform hover:scale-105">
                <div className="text-center">
                  <div className="text-4xl md:text-5xl font-bold mb-2 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">420M+</div>
                  <div className="text-muted-foreground font-medium">African youth population</div>
                  <div className="w-full bg-primary/20 rounded-full h-2 mt-4">
                    <div className="bg-gradient-to-r from-primary to-secondary h-2 rounded-full w-3/4"></div>
                  </div>
                </div>
              </Card>
              <Card className="p-8 bg-gradient-to-br from-secondary/5 to-secondary/10 border-secondary/20 hover:shadow-lg transition-all duration-300 transform hover:scale-105">
                <div className="text-center">
                  <div className="text-4xl md:text-5xl font-bold mb-2 bg-gradient-to-r from-secondary to-accent bg-clip-text text-transparent">60%</div>
                  <div className="text-muted-foreground font-medium">Lack formal digital identity</div>
                  <div className="w-full bg-secondary/20 rounded-full h-2 mt-4">
                    <div className="bg-gradient-to-r from-secondary to-accent h-2 rounded-full w-3/5"></div>
                  </div>
                </div>
              </Card>
              <Card className="p-8 bg-gradient-to-br from-accent/5 to-accent/10 border-accent/20 hover:shadow-lg transition-all duration-300 transform hover:scale-105">
                <div className="text-center">
                  <div className="text-4xl md:text-5xl font-bold mb-2 bg-gradient-to-r from-accent to-primary bg-clip-text">$95B</div>
                  <div className="text-muted-foreground font-medium">Informal economy value</div>
                  <div className="w-full bg-accent/20 rounded-full h-2 mt-4">
                    <div className="bg-gradient-to-r from-accent to-primary h-2 rounded-full w-4/5"></div>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </section>

      <div className="section-divider"></div>

      {/* Solution Section */}
      <section id="solution" className="bg-gradient-to-br from-background to-primary/5 section-spacing">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <Badge variant="outline" className="mb-4 px-4 py-2 text-sm font-medium bg-primary/10 text-primary border-primary/20">
              The Solution
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-primary to-secondary bg-clip-text">
              The Nimo Solution: Bridging the Gap
            </h2>
            <p className="text-xl md:text-2xl text-muted-foreground max-w-4xl mx-auto leading-relaxed">
              This is where Nimo steps in. We are building a decentralized reputation system, a bridge between real-world contributions and digital recognition.
            </p>
          </div>

          <div className="text-center mb-12">
            <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto bg-muted/50 rounded-lg p-6 border">
              Nimo empowers African youth to create persistent digital identities and earn verifiable reputation tokens for their work, activism, and learning.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
            <Card className="p-6 text-center bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <Award className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold mb-2 text-lg">Decentralized Identity</h3>
              <p className="text-sm text-muted-foreground">Unique NFT certificates on Ethereum</p>
            </Card>

            <Card className="p-6 text-center bg-gradient-to-br from-secondary/5 to-secondary/10 border-secondary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-secondary to-secondary/80 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <CheckCircle className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold mb-2 text-lg">Proof of Contribution</h3>
              <p className="text-sm text-muted-foreground">Immutable record of achievements</p>
            </Card>

            <Card className="p-6 text-center bg-gradient-to-br from-accent/5 to-accent/10 border-accent/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-accent to-accent/80 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <TrendingUp className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold mb-2 text-lg">Reputation Tokens</h3>
              <p className="text-sm text-muted-foreground">ERC20 tokens for verified contributions</p>
            </Card>

            <Card className="p-6 text-center bg-gradient-to-br from-primary/5 to-secondary/10 border-primary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <Zap className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold mb-2 text-lg">MeTTa Intelligence</h3>
              <p className="text-sm text-muted-foreground">AI-powered verification system</p>
            </Card>
          </div>
        </div>
      </section>

      <div className="section-divider"></div>

      {/* How It Works */}
      <section id="how-it-works" className="bg-gradient-to-br from-muted/30 to-background relative overflow-hidden section-spacing">
        <div className="absolute inset-0 bg-circuit-pattern opacity-5"></div>
        <div className="container mx-auto px-4 relative">
          <div className="text-center mb-16">
            <Badge variant="outline" className="mb-4 px-4 py-2 text-sm font-medium">
              How It Works
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text">
              How Nimo Works: A Glimpse into the Future
            </h2>
            <p className="text-xl md:text-2xl text-muted-foreground max-w-4xl mx-auto leading-relaxed">
              At its core, Nimo leverages cutting-edge technology to create a transparent, immutable record of achievements.
            </p>
          </div>

          <div className="grid md:grid-cols-5 gap-6 lg:gap-8">
            <div className="text-center group">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary to-primary/80 text-white flex items-center justify-center mx-auto mb-4 text-2xl font-bold shadow-lg group-hover:scale-110 transition-all duration-300 group-hover:shadow-xl">
                1
              </div>
              <h3 className="font-semibold mb-2 text-lg">Identity Creation</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">Each identity is a unique NFT on Ethereum, giving users full ownership and portability.</p>
              <div className="w-full bg-primary/20 rounded-full h-1 mt-4 group-hover:bg-primary/40 transition-colors">
                <div className="bg-gradient-to-r from-primary to-secondary h-1 rounded-full w-full"></div>
              </div>
            </div>

            <div className="text-center group">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-secondary to-secondary/80 text-white flex items-center justify-center mx-auto mb-4 text-2xl font-bold shadow-lg group-hover:scale-110 transition-all duration-300 group-hover:shadow-xl">
                2
              </div>
              <h3 className="font-semibold mb-2 text-lg">Contribution Submission</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">Users submit evidence of their real-world contributions to the platform.</p>
              <div className="w-full bg-secondary/20 rounded-full h-1 mt-4 group-hover:bg-secondary/40 transition-colors">
                <div className="bg-gradient-to-r from-secondary to-accent h-1 rounded-full w-full"></div>
              </div>
            </div>

            <div className="text-center group">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-accent to-accent/80 text-white flex items-center justify-center mx-auto mb-4 text-2xl font-bold shadow-lg group-hover:scale-110 transition-all duration-300 group-hover:shadow-xl">
                3
              </div>
              <h3 className="font-semibold mb-2 text-lg">MeTTa Verification</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">AI agents analyze contributions using MeTTa language for intelligent verification.</p>
              <div className="w-full bg-accent/20 rounded-full h-1 mt-4 group-hover:bg-accent/40 transition-colors">
                <div className="bg-gradient-to-r from-accent to-primary h-1 rounded-full w-full"></div>
              </div>
            </div>

            <div className="text-center group">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary to-secondary text-white flex items-center justify-center mx-auto mb-4 text-2xl font-bold shadow-lg group-hover:scale-110 transition-all duration-300 group-hover:shadow-xl">
                4
              </div>
              <h3 className="font-semibold mb-2 text-lg">Token Rewards</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">Smart contracts automatically award ERC20 reputation tokens for verified contributions.</p>
              <div className="w-full bg-primary/20 rounded-full h-1 mt-4 group-hover:bg-primary/40 transition-colors">
                <div className="bg-gradient-to-r from-primary to-secondary h-1 rounded-full w-full"></div>
              </div>
            </div>

            <div className="text-center group">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-secondary to-accent text-white flex items-center justify-center mx-auto mb-4 text-2xl font-bold shadow-lg group-hover:scale-110 transition-all duration-300 group-hover:shadow-xl">
                5
              </div>
              <h3 className="font-semibold mb-2 text-lg">Opportunity Access</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">Users leverage their identity and tokens to unlock access to jobs, grants, and more.</p>
              <div className="w-full bg-secondary/20 rounded-full h-1 mt-4 group-hover:bg-secondary/40 transition-colors">
                <div className="bg-gradient-to-r from-secondary to-accent h-1 rounded-full w-full"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="section-divider"></div>

      {/* Impact Section */}
      <section id="impact" className="bg-gradient-to-br from-background to-secondary/5 section-spacing">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <Badge variant="outline" className="mb-4 px-4 py-2 text-sm font-medium bg-secondary/10 text-secondary border-secondary/20">
              The Impact
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-secondary to-accent bg-clip-text">
              Impact: Unlocking Opportunities
            </h2>
            <p className="text-xl md:text-2xl text-muted-foreground max-w-4xl mx-auto leading-relaxed">
              With Nimo, young individuals can use their verifiable identity and reputation to unlock a world of opportunities.
            </p>
          </div>

          <div className="text-center mb-12">
            <div className="bg-gradient-to-r from-primary/10 to-secondary/10 rounded-2xl p-8 border border-primary/20">
              <Network className="w-12 h-12 text-primary mx-auto mb-4" />
              <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
                We're also building an Impact Bond Marketplace, allowing diaspora investors to directly fund local projects, with transparent tracking of social and economic impact.
              </p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8 mb-16">
            <Card className="p-6 text-center bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <Users className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold mb-2 text-lg">Internships & Jobs</h3>
              <p className="text-sm text-muted-foreground">with verified skills</p>
            </Card>

            <Card className="p-6 text-center bg-gradient-to-br from-secondary/5 to-secondary/10 border-secondary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-secondary to-secondary/80 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <Target className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold mb-2 text-lg">Grants & Funding</h3>
              <p className="text-sm text-muted-foreground">for projects</p>
            </Card>

            <Card className="p-6 text-center bg-gradient-to-br from-accent/5 to-accent/10 border-accent/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-accent to-accent/80 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <TrendingUp className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold mb-2 text-lg">Freelance Gigs</h3>
              <p className="text-sm text-muted-foreground">with reputation</p>
            </Card>

            <Card className="p-6 text-center bg-gradient-to-br from-primary/5 to-secondary/10 border-primary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <Globe className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold mb-2 text-lg">DAO Participation</h3>
              <p className="text-sm text-muted-foreground">& governance</p>
            </Card>
          </div>

          {/* Tech Stack */}
          <div className="text-center mb-16">
            <div className="bg-gradient-to-r from-muted/50 to-muted/30 rounded-2xl p-8 border">
              <div className="flex items-center justify-center mb-6">
                <Trophy className="w-8 h-8 text-primary mr-3" />
                <h3 className="text-2xl md:text-3xl font-bold">Powered by Innovation</h3>
              </div>
              <p className="text-muted-foreground mb-8 text-lg">Nimo leverages cutting-edge technologies to deliver a robust, scalable, and secure platform.</p>

              <div className="grid md:grid-cols-3 gap-8">
                <div className="bg-background/50 rounded-lg p-6 border border-primary/20">
                  <h4 className="font-semibold mb-4 text-lg flex items-center">
                    <BookOpen className="w-5 h-5 text-primary mr-2" />
                    Frontend
                  </h4>
                  <div className="space-y-3 text-sm text-muted-foreground">
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-primary mr-3"></div>
                      React 19.1.1
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-secondary mr-3"></div>
                      Vite 7.1.2
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-accent mr-3"></div>
                      Tailwind CSS
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-primary mr-3"></div>
                      React Router
                    </div>
                  </div>
                </div>

                <div className="bg-background/50 rounded-lg p-6 border border-secondary/20">
                  <h4 className="font-semibold mb-4 text-lg flex items-center">
                    <Network className="w-5 h-5 text-secondary mr-2" />
                    Backend
                  </h4>
                  <div className="space-y-3 text-sm text-muted-foreground">
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-secondary mr-3"></div>
                      Flask (Python)
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-accent mr-3"></div>
                      Web3.py
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-primary mr-3"></div>
                      JWT Auth
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-secondary mr-3"></div>
                      IPFS Storage
                    </div>
                  </div>
                </div>

                <div className="bg-background/50 rounded-lg p-6 border border-accent/20">
                  <h4 className="font-semibold mb-4 text-lg flex items-center">
                    <Shield className="w-5 h-5 text-accent mr-2" />
                    Blockchain
                  </h4>
                  <div className="space-y-3 text-sm text-muted-foreground">
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-accent mr-3"></div>
                      Base Network (L2)
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-primary mr-3"></div>
                      Solidity + OpenZeppelin
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-secondary mr-3"></div>
                      Foundry
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-accent mr-3"></div>
                      NFT Identity
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="section-divider"></div>

      {/* Team Section */}
      <section id="team" className="bg-gradient-to-br from-muted/30 to-background relative overflow-hidden section-spacing">
        <div className="absolute inset-0 bg-dots-pattern opacity-10"></div>
        <div className="container mx-auto px-4 relative">
          <div className="text-center mb-16">
            <Badge variant="outline" className="mb-4 px-4 py-2 text-sm font-medium">
              Our Team
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text">
              Meet the Team
            </h2>
            <p className="text-xl md:text-2xl text-muted-foreground max-w-4xl mx-auto leading-relaxed">
              Behind Nimo is a dedicated team of innovators committed to empowering African youth through technology.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 lg:gap-12 max-w-5xl mx-auto">
            <Card className="p-8 bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group">
              <div className="text-center">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <span className="text-3xl font-bold text-white">JK</span>
                </div>
                <h3 className="text-xl md:text-2xl font-semibold mb-2">John Koiyaki</h3>
                <p className="text-muted-foreground mb-4 font-medium">Creative Technologist & Lead Developer</p>
                <p className="text-sm text-muted-foreground mb-6 leading-relaxed">
                  Based in Kenya, John is a software developer and emerging tech educator with a background in ICT and technical writing. He's passionate about building tools that scale knowledge and culture.
                </p>
                <div className="flex flex-wrap gap-2 justify-center">
                  <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">Python</Badge>
                  <Badge variant="secondary" className="bg-secondary/10 text-secondary border-secondary/20">Blockchain</Badge>
                  <Badge variant="secondary" className="bg-accent/10 text-accent border-accent/20">Web3</Badge>
                  <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">EdTech</Badge>
                  <Badge variant="secondary" className="bg-secondary/10 text-secondary border-secondary/20">AI + RAG</Badge>
                </div>
              </div>
            </Card>

            <Card className="p-8 bg-gradient-to-br from-secondary/5 to-secondary/10 border-secondary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group">
              <div className="text-center">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-secondary to-accent flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <span className="text-3xl font-bold text-white">AF</span>
                </div>
                <h3 className="text-xl md:text-2xl font-semibold mb-2">Aisha Omar Farah</h3>
                <p className="text-muted-foreground mb-4 font-medium">Frontend & Web3 Developer</p>
                <p className="text-sm text-muted-foreground mb-6 leading-relaxed">
                  Aisha is a passionate frontend developer and open-source contributor with expertise in creating interactive, modern, and visually appealing designs. She's a regular hackathon participant.
                </p>
                <div className="flex flex-wrap gap-2 justify-center">
                  <Badge variant="secondary" className="bg-secondary/10 text-secondary border-secondary/20">React</Badge>
                  <Badge variant="secondary" className="bg-accent/10 text-accent border-accent/20">Tailwind CSS</Badge>
                  <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">JavaScript</Badge>
                  <Badge variant="secondary" className="bg-secondary/10 text-secondary border-secondary/20">Web3</Badge>
                  <Badge variant="secondary" className="bg-accent/10 text-accent border-accent/20">UI/UX</Badge>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      <div className="section-divider"></div>

      {/* CTA Section */}
      <section className="bg-gradient-to-br from-primary via-secondary to-accent text-primary-foreground relative overflow-hidden section-spacing">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="container mx-auto px-4 text-center relative">
          <div className="max-w-4xl mx-auto">
            <div className="inline-flex items-center px-6 py-3 rounded-full bg-white/10 text-white text-sm font-medium mb-6 backdrop-blur-sm">
              <Heart className="w-4 h-4 mr-2" />
              Join the Movement
            </div>
            <h2 className="text-4xl md:text-6xl font-bold mb-6 text-white">
              Join the Movement
            </h2>
            <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto text-white/90 leading-relaxed">
              Nimo is more than just technology; it's a movement to empower African youth and build a more inclusive digital future.
            </p>
            <p className="text-lg md:text-xl mb-12 max-w-3xl mx-auto text-white/80 leading-relaxed">
              With your support, we can scale this solution to reach millions, transforming lives and creating lasting change.
            </p>
            <div className="flex flex-col sm:flex-row gap-6 justify-center">
              <Button size="lg" variant="secondary" className="text-lg px-8 py-4 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 bg-white text-primary hover:bg-white/90" asChild>
                <a href="/register" className="flex items-center">
                  <Users className="mr-2 w-5 h-5" />
                  Join Nimo
                  <ArrowRight className="ml-2 w-5 h-5" />
                </a>
              </Button>
              <Button size="lg" variant="outline" className="text-lg px-8 py-4 border-2 border-white text-white hover:bg-white hover:text-primary transition-all duration-300 transform hover:scale-105 hover:-translate-y-1" asChild>
                <a href="/login" className="flex items-center">
                  <MapPin className="mr-2 w-5 h-5" />
                  Sign In
                  <ArrowRight className="ml-2 w-5 h-5" />
                </a>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-muted py-16 lg:py-20">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 mb-12">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-xl font-bold">Nimo</h3>
              </div>
              <p className="text-muted-foreground leading-relaxed">
                Empowering African youth through decentralized identity and proof of contribution.
              </p>
            </div>

            <div>
              <h4 className="font-semibold mb-4 text-lg">Contact</h4>
              <div className="space-y-3 text-sm text-muted-foreground">
                <div className="flex items-center">
                  <Globe className="w-4 h-4 mr-2 text-primary" />
                  nimo.network
                </div>
                <div className="flex items-center">
                  <Mail className="w-4 h-4 mr-2 text-primary" />
                  hello@nimo.network
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-4 text-lg">Follow Us</h4>
              <div className="flex space-x-4">
                <a href="#" className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary hover:bg-primary hover:text-white transition-all duration-300 transform hover:scale-110" aria-label="Follow us on Twitter">
                  <Twitter className="w-5 h-5" />
                </a>
                <a href="#" className="w-10 h-10 rounded-full bg-secondary/10 flex items-center justify-center text-secondary hover:bg-secondary hover:text-white transition-all duration-300 transform hover:scale-110" aria-label="Follow us on GitHub">
                  <Github className="w-5 h-5" />
                </a>
                <a href="#" className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center text-accent hover:bg-accent hover:text-white transition-all duration-300 transform hover:scale-110" aria-label="Contact us via email">
                  <Mail className="w-5 h-5" />
                </a>
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-4 text-lg">Legal</h4>
              <div className="space-y-3 text-sm text-muted-foreground">
                <a href="#" className="hover:text-primary transition-colors duration-200 flex items-center">
                  <Shield className="w-4 h-4 mr-2" />
                  Privacy Policy
                </a>
                <a href="#" className="hover:text-primary transition-colors duration-200 flex items-center">
                  <BookOpen className="w-4 h-4 mr-2" />
                  Terms of Service
                </a>
              </div>
            </div>
          </div>

          <div className="border-t pt-8 text-center text-muted-foreground">
            <div className="flex items-center justify-center mb-4">
              <Calendar className="w-4 h-4 mr-2" />
              <p>&copy; 2025 Nimo. All rights reserved.</p>
            </div>
            <p className="text-sm">Empowering African youth through decentralized identity and proof of contribution.</p>
          </div>
        </div>
      </footer>
    </main>
  );
};

export default LandingPage;