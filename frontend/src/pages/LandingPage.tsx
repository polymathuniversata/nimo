import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ThemeToggle } from '@/components/ThemeToggle';
import heroBgImage from '@/assets/hero-bg.jpg';

import {
  Users,
  Award,
  TrendingUp,
  Globe,
  Target,
  Zap,
  CheckCircle,
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
  ChevronDown,
  Menu,
  AlertTriangle,
  Cog,
  Gift
} from 'lucide-react';

import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';

const LandingPage = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
      setMobileMenuOpen(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
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
            <div className="flex items-center gap-4">
              <div className="hidden sm:block">
                <ThemeToggle />
              </div>
              <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
                <SheetTrigger asChild>
                  <Button variant="ghost" size="icon" className="block sm:hidden text-muted-foreground hover:text-primary transition-colors">
                    <Menu className="w-6 h-6" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="right" className="w-full sm:w-80">
                  <SheetHeader>
                    <SheetTitle className="text-left">Menu</SheetTitle>
                  </SheetHeader>
                  <div className="mt-8 flex flex-col gap-6">
                    <nav className="flex flex-col gap-4">
                      <Button variant="ghost" className="justify-start" onClick={() => scrollToSection('home')}>
                        Home
                      </Button>
                      <Button variant="ghost" className="justify-start" onClick={() => scrollToSection('problem')}>
                        Problem
                      </Button>
                      <Button variant="ghost" className="justify-start" onClick={() => scrollToSection('solution')}>
                        Solution
                      </Button>
                      <Button variant="ghost" className="justify-start" onClick={() => scrollToSection('how-it-works')}>
                        How It Works
                      </Button>
                      <Button variant="ghost" className="justify-start" onClick={() => scrollToSection('impact')}>
                        Impact
                      </Button>
                      <Button variant="ghost" className="justify-start" onClick={() => scrollToSection('team')}>
                        Team
                      </Button>
                    </nav>
                    <div className="border-t pt-4">
                      <div className="flex flex-col gap-2">
                        <p className="text-sm font-medium">Theme</p>
                        <ThemeToggle />
                      </div>
                    </div>
                    <div className="border-t pt-4">
                      <Button className="w-full bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 shadow-lg hover:shadow-xl transition-all duration-300" asChild>
                        <Link to="/login" aria-label="Sign in to access your decentralized identity">
                          <span>Sign In</span>
                          <ArrowRight className="ml-2 w-4 h-4" aria-hidden="true" />
                        </Link>
                      </Button>
                    </div>
                  </div>
                </SheetContent>
              </Sheet>
              <Button className="hidden sm:flex bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 focus-visible-enhanced" asChild>
                <Link to="/login" aria-label="Sign in to access your decentralized identity">
                  <span>Sign In</span>
                  <ArrowRight className="ml-2 w-4 h-4" aria-hidden="true" />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section id="home" className="relative overflow-hidden bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5 min-h-screen flex items-center" aria-labelledby="hero-heading">
        {/* Background Image with Overlay */}
        <div className="absolute inset-0 z-0">
          <img
            src={heroBgImage}
            alt=""
            className="w-full h-full object-cover object-center"
            aria-hidden="true"
          />
          <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-secondary/15 to-accent/20 dark:from-primary/30 dark:via-secondary/25 dark:to-accent/30"></div>
          <div className="absolute inset-0 bg-gradient-to-t from-background/40 via-transparent to-background/20 dark:from-background/60 dark:via-background/30 dark:to-background/40"></div>
        </div>
        <div className="absolute inset-0 bg-grid-pattern opacity-5 dark:opacity-10" aria-hidden="true"></div>
        <div className="container mx-auto px-4 py-8 sm:py-12 md:py-16 lg:py-20 relative z-10">
          <div className="text-center max-w-6xl mx-auto">
            <div className="inline-flex items-center px-3 sm:px-4 py-2 rounded-full bg-primary/10 text-black font-bold text-xs sm:text-sm mb-4 sm:mb-6 animate-fade-in backdrop-blur-sm border border-primary/20" role="banner">
              <Sparkles className="w-3 h-3 sm:w-4 sm:h-4 mr-2" aria-hidden="true" />
              Empowering African Youth Through Technology
            </div>
            <h1 id="hero-heading" className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-black text-black mb-4 sm:mb-6 animate-fade-in-up leading-tight">
              Unlocking Africa's Youth Potential
            </h1>
            <p className="text-base sm:text-lg md:text-xl lg:text-2xl font-bold text-black mb-6 sm:mb-8 max-w-4xl mx-auto leading-relaxed animate-fade-in-up animation-delay-200">
              Decentralized Identity & Proof of Contribution for a Brighter Future
            </p>
            <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 justify-center items-center animate-fade-in-up animation-delay-400">
              <Button size="lg" className="bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 text-base sm:text-lg px-6 sm:px-8 py-3 sm:py-4 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 w-full sm:w-auto backdrop-blur-sm border border-white/10">
                <Lightbulb className="mr-2 w-4 h-4 sm:w-5 sm:h-5" />
                Learn More
              </Button>
              <Button size="lg" className="bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 text-base sm:text-lg px-6 sm:px-8 py-3 sm:py-4 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 w-full sm:w-auto backdrop-blur-sm border border-white/10" asChild>
                <a href="/login">
                  <Rocket className="mr-2 w-4 h-4 sm:w-5 sm:h-5" />
                  Get Started
                </a>
              </Button>
            </div>
            <div className="mt-8 sm:mt-12 animate-bounce">
              <ChevronDown className="w-6 h-6 sm:w-8 sm:h-8 text-muted-foreground mx-auto cursor-pointer hover:text-primary transition-colors" onClick={() => scrollToSection('problem')} />
            </div>
          </div>
        </div>
      </section>

      <div className="section-divider"></div>

      {/* Problem Section */}
      <section id="problem" className="relative overflow-hidden bg-gradient-to-br from-muted/30 to-background py-12 sm:py-16" aria-labelledby="problem-heading" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center' }}>
        <div className="absolute inset-0 bg-dots-pattern opacity-10" aria-hidden="true"></div>
        {/* Animated background elements */}
        <div className="absolute top-20 left-10 w-24 h-24 bg-red-500/5 rounded-full blur-xl animate-pulse" aria-hidden="true"></div>
        <div className="absolute bottom-20 right-10 w-16 h-16 bg-orange-500/5 rounded-full blur-xl animate-pulse animation-delay-1000" aria-hidden="true"></div>

        <div className="container mx-auto px-4 relative">
          <div className="max-w-5xl mx-auto">
            {/* Header Section */}
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center mb-4">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-red-500/20 via-orange-500/20 to-yellow-500/20 rounded-2xl blur-xl"></div>
                  <div className="relative bg-gradient-to-r from-red-500/10 via-orange-500/10 to-yellow-500/10 rounded-2xl px-8 py-4 border border-red-500/20 backdrop-blur-sm">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-r from-red-500 to-orange-500 flex items-center justify-center">
                        <AlertTriangle className="w-6 h-6 text-white" />
                      </div>
                      <h2 id="problem-heading" className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-red-600 via-orange-600 to-yellow-600 bg-clip-text text-transparent leading-tight">
                        The Challenge
                      </h2>
                    </div>
                  </div>
                </div>
              </div>
              <div className="max-w-3xl mx-auto mb-6">
                <p className="text-lg sm:text-xl text-muted-foreground leading-relaxed">
                  Across Africa, brilliant minds are transforming communities, but their digital contributions remain invisible.
                </p>
              </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid md:grid-cols-2 gap-6 items-center">
              {/* Challenge Cards */}
              <div className="space-y-4">
                <div className="bg-gradient-to-br from-red-50 to-red-100/50 dark:from-red-950/20 dark:to-red-900/10 rounded-xl p-4 border border-red-200/50 dark:border-red-800/20 group hover:shadow-lg transition-all duration-300">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-red-500 flex items-center justify-center flex-shrink-0">
                      <Users className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-red-800 dark:text-red-200 mb-1">Untapped Talent</h3>
                      <p className="text-sm text-red-700 dark:text-red-300">
                        Millions of young Africans contribute daily, yet go unrecognized.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-orange-50 to-orange-100/50 dark:from-orange-950/20 dark:to-orange-900/10 rounded-xl p-4 border border-orange-200/50 dark:border-orange-800/20 group hover:shadow-lg transition-all duration-300">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-orange-500 flex items-center justify-center flex-shrink-0">
                      <Shield className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-orange-800 dark:text-orange-200 mb-1">Invisible Impact</h3>
                      <p className="text-sm text-orange-700 dark:text-orange-300">
                        No verifiable digital identities make contributions invisible.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-yellow-50 to-yellow-100/50 dark:from-yellow-950/20 dark:to-yellow-900/10 rounded-xl p-4 border border-yellow-200/50 dark:border-yellow-800/20 group hover:shadow-lg transition-all duration-300">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-yellow-500 flex items-center justify-center flex-shrink-0">
                      <Target className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-yellow-800 dark:text-yellow-200 mb-1">Blocked Opportunities</h3>
                      <p className="text-sm text-yellow-700 dark:text-yellow-300">
                        Digital divide blocks access to jobs, grants, and platforms.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Statistics Section */}
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gradient-to-br from-indigo-50 to-indigo-100/50 dark:from-indigo-950/20 dark:to-indigo-900/10 rounded-lg p-4 border border-indigo-200/50 dark:border-indigo-800/20 group hover:shadow-lg transition-all duration-300">
                  <div className="text-center">
                    <div className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-1">420M+</div>
                    <div className="text-xs text-muted-foreground">African Youth</div>
                    <div className="w-full bg-indigo-200/50 dark:bg-indigo-800/20 rounded-full h-2 mt-2">
                      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 h-2 rounded-full w-3/4 transition-all duration-500 group-hover:w-4/5"></div>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-purple-50 to-purple-100/50 dark:from-purple-950/20 dark:to-purple-900/10 rounded-lg p-4 border border-purple-200/50 dark:border-purple-800/20 group hover:shadow-lg transition-all duration-300">
                  <div className="text-center">
                    <div className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-violet-600 bg-clip-text text-transparent mb-1">60%</div>
                    <div className="text-xs text-muted-foreground">Digital Gap</div>
                    <div className="w-full bg-purple-200/50 dark:bg-purple-800/20 rounded-full h-2 mt-2">
                      <div className="bg-gradient-to-r from-purple-600 to-violet-600 h-2 rounded-full w-3/5 transition-all duration-500 group-hover:w-2/3"></div>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-violet-50 to-violet-100/50 dark:from-violet-950/20 dark:to-violet-900/10 rounded-lg p-4 border border-violet-200/50 dark:border-violet-800/20 group hover:shadow-lg transition-all duration-300">
                  <div className="text-center">
                    <div className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent mb-1">$95B</div>
                    <div className="text-xs text-muted-foreground">Informal Economy</div>
                    <div className="w-full bg-violet-200/50 dark:bg-violet-800/20 rounded-full h-2 mt-2">
                      <div className="bg-gradient-to-r from-violet-600 to-indigo-600 h-2 rounded-full w-4/5 transition-all duration-500 group-hover:w-5/6"></div>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-rose-50 to-rose-100/50 dark:from-rose-950/20 dark:to-rose-900/10 rounded-lg p-4 border border-rose-200/50 dark:border-rose-800/20 group hover:shadow-lg transition-all duration-300">
                  <div className="text-center">
                    <div className="text-2xl font-bold bg-gradient-to-r from-rose-600 to-pink-600 bg-clip-text text-transparent mb-1">85%</div>
                    <div className="text-xs text-muted-foreground">Youth Unemployment</div>
                    <div className="w-full bg-rose-200/50 dark:bg-rose-800/20 rounded-full h-2 mt-2">
                      <div className="bg-gradient-to-r from-rose-600 to-pink-600 h-2 rounded-full w-5/6 transition-all duration-500 group-hover:w-full"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="section-divider"></div>

      {/* Solution Section */}
      <section id="solution" className="bg-gradient-to-br from-background to-primary/5 py-12 sm:py-16 md:py-20 lg:py-24">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12 sm:mb-16">
            <div className="inline-flex items-center justify-center mb-6">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-secondary/20 to-accent/20 rounded-2xl blur-xl"></div>
                <div className="relative bg-gradient-to-r from-primary/10 via-secondary/10 to-accent/10 rounded-2xl px-8 py-4 border border-primary/30">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-r from-primary to-secondary flex items-center justify-center">
                      <Lightbulb className="w-6 h-6 text-white" />
                    </div>
                    <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent leading-tight">
                      The Solution
                    </h2>
                  </div>
                </div>
              </div>
            </div>
            <p className="text-lg sm:text-xl md:text-2xl text-muted-foreground max-w-5xl mx-auto leading-relaxed">
              This is where Nimo steps in. We're building a decentralized reputation system that empowers African youth to create persistent digital identities and earn verifiable reputation tokens for their work, activism, and learning—bridging real-world contributions with digital recognition.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
            <Card className="p-6 text-center bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group h-full flex flex-col">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <Award className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold mb-3 text-lg">Decentralized Identity</h3>
              <p className="text-sm text-muted-foreground flex-grow">Unique NFT certificates on Cardano blockchain for true ownership</p>
            </Card>

            <Card className="p-6 text-center bg-gradient-to-br from-secondary/5 to-secondary/10 border-secondary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group h-full flex flex-col">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-secondary to-secondary/80 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <CheckCircle className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold mb-3 text-lg">Proof of Contribution</h3>
              <p className="text-sm text-muted-foreground flex-grow">Immutable record of achievements and real-world impact</p>
            </Card>

            <Card className="p-6 text-center bg-gradient-to-br from-accent/5 to-accent/10 border-accent/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group h-full flex flex-col">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-accent to-accent/80 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <TrendingUp className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold mb-3 text-lg">Reputation Tokens</h3>
              <p className="text-sm text-muted-foreground flex-grow">Native Cardano tokens earned for verified contributions</p>
            </Card>

            <Card className="p-6 text-center bg-gradient-to-br from-primary/5 to-secondary/10 border-primary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group h-full flex flex-col">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <Zap className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold mb-3 text-lg">MeTTa Intelligence</h3>
              <p className="text-sm text-muted-foreground flex-grow">AI-powered verification system for intelligent contribution analysis</p>
            </Card>
          </div>
        </div>
      </section>

      <div className="section-divider"></div>

      {/* How It Works */}
      <section id="how-it-works" className="bg-gradient-to-br from-muted/30 to-background relative overflow-hidden py-12 sm:py-16 md:py-20 lg:py-24">
        <div className="absolute inset-0 bg-circuit-pattern opacity-5"></div>
        <div className="container mx-auto px-4 relative">
          <div className="text-center mb-12 sm:mb-16">
            <div className="inline-flex items-center justify-center mb-6">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-secondary/20 via-accent/20 to-primary/20 rounded-2xl blur-xl"></div>
                <div className="relative bg-gradient-to-r from-secondary/10 via-accent/10 to-primary/10 rounded-2xl px-8 py-4 border border-secondary/30">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-r from-secondary to-accent flex items-center justify-center">
                      <Cog className="w-6 h-6 text-white" />
                    </div>
                    <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-secondary via-accent to-primary bg-clip-text text-transparent leading-tight">
                      How It Works
                    </h2>
                  </div>
                </div>
              </div>
            </div>
            <p className="text-lg sm:text-xl md:text-2xl text-muted-foreground max-w-5xl mx-auto leading-relaxed">
              At its core, Nimo leverages cutting-edge technology to create a transparent, immutable record of achievements.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6 lg:gap-8">
            <Card className="p-6 text-center bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group h-full flex flex-col">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary to-primary/80 text-white flex items-center justify-center mx-auto mb-4 text-2xl font-bold shadow-lg group-hover:scale-110 transition-all duration-300 group-hover:shadow-xl">
                1
              </div>
              <h3 className="font-semibold mb-3 text-lg">Identity Creation</h3>
              <p className="text-sm text-muted-foreground leading-relaxed flex-grow">Each identity is a unique NFT on Cardano, giving users full ownership and portability.</p>
              <div className="w-full bg-primary/20 rounded-full h-1 mt-4 group-hover:bg-primary/40 transition-colors">
                <div className="bg-gradient-to-r from-primary to-secondary h-1 rounded-full w-full"></div>
              </div>
            </Card>

            <Card className="p-6 text-center bg-gradient-to-br from-secondary/5 to-secondary/10 border-secondary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group h-full flex flex-col">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-secondary to-secondary/80 text-white flex items-center justify-center mx-auto mb-4 text-2xl font-bold shadow-lg group-hover:scale-110 transition-all duration-300 group-hover:shadow-xl">
                2
              </div>
              <h3 className="font-semibold mb-3 text-lg">Contribution Submission</h3>
              <p className="text-sm text-muted-foreground leading-relaxed flex-grow">Users submit evidence of their real-world contributions to the platform.</p>
              <div className="w-full bg-secondary/20 rounded-full h-1 mt-4 group-hover:bg-secondary/40 transition-colors">
                <div className="bg-gradient-to-r from-secondary to-accent h-1 rounded-full w-full"></div>
              </div>
            </Card>

            <Card className="p-6 text-center bg-gradient-to-br from-accent/5 to-accent/10 border-accent/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group h-full flex flex-col">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-accent to-accent/80 text-white flex items-center justify-center mx-auto mb-4 text-2xl font-bold shadow-lg group-hover:scale-110 transition-all duration-300 group-hover:shadow-xl">
                3
              </div>
              <h3 className="font-semibold mb-3 text-lg">MeTTa Verification</h3>
              <p className="text-sm text-muted-foreground leading-relaxed flex-grow">AI agents analyze contributions using MeTTa language for intelligent verification.</p>
              <div className="w-full bg-accent/20 rounded-full h-1 mt-4 group-hover:bg-accent/40 transition-colors">
                <div className="bg-gradient-to-r from-accent to-primary h-1 rounded-full w-full"></div>
              </div>
            </Card>

            <Card className="p-6 text-center bg-gradient-to-br from-primary/5 to-secondary/10 border-primary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group h-full flex flex-col">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary to-secondary text-white flex items-center justify-center mx-auto mb-4 text-2xl font-bold shadow-lg group-hover:scale-110 transition-all duration-300 group-hover:shadow-xl">
                4
              </div>
              <h3 className="font-semibold mb-3 text-lg">Token Rewards</h3>
              <p className="text-sm text-muted-foreground leading-relaxed flex-grow">Smart contracts automatically award native tokens for verified contributions.</p>
              <div className="w-full bg-primary/20 rounded-full h-1 mt-4 group-hover:bg-primary/40 transition-colors">
                <div className="bg-gradient-to-r from-primary to-secondary h-1 rounded-full w-full"></div>
              </div>
            </Card>

            <Card className="p-6 text-center bg-gradient-to-br from-secondary/5 to-accent/10 border-secondary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group h-full flex flex-col">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-secondary to-accent text-white flex items-center justify-center mx-auto mb-4 text-2xl font-bold shadow-lg group-hover:scale-110 transition-all duration-300 group-hover:shadow-xl">
                5
              </div>
              <h3 className="font-semibold mb-3 text-lg">Opportunity Access</h3>
              <p className="text-sm text-muted-foreground leading-relaxed flex-grow">Users leverage their identity and tokens to unlock access to jobs, grants, and more.</p>
              <div className="w-full bg-secondary/20 rounded-full h-1 mt-4 group-hover:bg-secondary/40 transition-colors">
                <div className="bg-gradient-to-r from-secondary to-accent h-1 rounded-full w-full"></div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      <div className="section-divider"></div>

      {/* Impact Section */}
      <section id="impact" className="bg-gradient-to-br from-background to-secondary/5 py-12 sm:py-16 md:py-20 lg:py-24">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12 sm:mb-16">
            <div className="inline-flex items-center justify-center mb-6">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-accent/20 via-primary/20 to-secondary/20 rounded-2xl blur-xl"></div>
                <div className="relative bg-gradient-to-r from-accent/10 via-primary/10 to-secondary/10 rounded-2xl px-8 py-4 border border-accent/30">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-r from-accent to-primary flex items-center justify-center">
                      <Gift className="w-6 h-6 text-white" />
                    </div>
                    <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-accent via-primary to-secondary bg-clip-text text-transparent leading-tight">
                      Unlocking Opportunities
                    </h2>
                  </div>
                </div>
              </div>
            </div>
            <p className="text-lg sm:text-xl md:text-2xl text-muted-foreground max-w-5xl mx-auto leading-relaxed">
              With Nimo, young individuals can use their verifiable identity and reputation to unlock a world of opportunities.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8 mb-12">
            <Card className="p-6 text-center bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group h-full flex flex-col">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <Users className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold mb-3 text-lg">Internships & Jobs</h3>
              <p className="text-sm text-muted-foreground flex-grow">Access opportunities with verified skills and proven contributions</p>
            </Card>

            <Card className="p-6 text-center bg-gradient-to-br from-secondary/5 to-secondary/10 border-secondary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group h-full flex flex-col">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-secondary to-secondary/80 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <Target className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold mb-3 text-lg">Grants & Funding</h3>
              <p className="text-sm text-muted-foreground flex-grow">Secure funding for projects with transparent impact tracking</p>
            </Card>

            <Card className="p-6 text-center bg-gradient-to-br from-accent/5 to-accent/10 border-accent/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group h-full flex flex-col">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-accent to-accent/80 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <TrendingUp className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold mb-3 text-lg">Freelance Gigs</h3>
              <p className="text-sm text-muted-foreground flex-grow">Build reputation and earn through verified freelance work</p>
            </Card>

            <Card className="p-6 text-center bg-gradient-to-br from-primary/5 to-secondary/10 border-primary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group h-full flex flex-col">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <Globe className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold mb-3 text-lg">DAO Participation</h3>
              <p className="text-sm text-muted-foreground flex-grow">Participate in governance and decentralized organizations</p>
            </Card>
          </div>

          {/* Impact Bond Marketplace */}
          <div className="text-center mb-16">
            <div className="bg-gradient-to-r from-primary/10 to-secondary/10 rounded-2xl p-8 border border-primary/20">
              <Network className="w-12 h-12 text-primary mx-auto mb-4" />
              <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
                We're also building an Impact Bond Marketplace, allowing diaspora investors to directly fund local projects, with transparent tracking of social and economic impact.
              </p>
            </div>
          </div>

          {/* Tech Stack */}
          <div className="text-center mb-16">
            <div className="bg-gradient-to-r from-muted/50 to-muted/30 rounded-2xl p-8 border">
              <div className="flex items-center justify-center mb-6">
                <Trophy className="w-8 h-8 text-primary mr-3" />
                <h3 className="text-2xl md:text-3xl font-bold">Powered by Innovation</h3>
              </div>
              <p className="text-muted-foreground mb-8 text-lg">Nimo leverages cutting-edge technologies to deliver a robust, scalable, and secure platform.</p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
                <Card className="bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group h-full flex flex-col">
                  <div className="p-6 flex-grow">
                    <h4 className="font-semibold mb-4 text-lg flex items-center">
                      <BookOpen className="w-5 h-5 text-primary mr-2" />
                      Frontend
                    </h4>
                    <div className="space-y-3 text-sm text-muted-foreground">
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-primary mr-3"></div>
                        React 18.3.1
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-secondary mr-3"></div>
                        Vite 5.4.19
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-accent mr-3"></div>
                        Tailwind CSS 3.4.17
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-primary mr-3"></div>
                        React Router 6.30.1
                      </div>
                    </div>
                  </div>
                </Card>

                <Card className="bg-gradient-to-br from-secondary/5 to-secondary/10 border-secondary/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group h-full flex flex-col">
                  <div className="p-6 flex-grow">
                    <h4 className="font-semibold mb-4 text-lg flex items-center">
                      <Network className="w-5 h-5 text-secondary mr-2" />
                      Backend
                    </h4>
                    <div className="space-y-3 text-sm text-muted-foreground">
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-secondary mr-3"></div>
                        Flask 3.0.3
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-accent mr-3"></div>
                        MeTTa AI (PyMeTTa)
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-primary mr-3"></div>
                        JWT Auth
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-secondary mr-3"></div>
                        SQLAlchemy 2.0.32
                      </div>
                    </div>
                  </div>
                </Card>

                <Card className="bg-gradient-to-br from-accent/5 to-accent/10 border-accent/20 hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group h-full flex flex-col">
                  <div className="p-6 flex-grow">
                    <h4 className="font-semibold mb-4 text-lg flex items-center">
                      <Shield className="w-5 h-5 text-accent mr-2" />
                      Blockchain
                    </h4>
                    <div className="space-y-3 text-sm text-muted-foreground">
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-accent mr-3"></div>
                        Cardano (Aiken/Plutus)
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-primary mr-3"></div>
                        PyCardano Integration
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-secondary mr-3"></div>
                        Blockfrost API
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-accent mr-3"></div>
                        NFT Identity System
                      </div>
                    </div>
                  </div>
                </Card>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="section-divider"></div>

      {/* Team Section */}
      <section id="team" className="bg-gradient-to-br from-muted/30 to-background relative overflow-hidden py-12 sm:py-16 md:py-20 lg:py-24">
        <div className="absolute inset-0 bg-dots-pattern opacity-10"></div>
        <div className="container mx-auto px-4 relative">
          <div className="text-center mb-12 sm:mb-16">
            <div className="inline-flex items-center justify-center mb-6">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-secondary/20 via-primary/20 to-accent/20 rounded-2xl blur-xl"></div>
                <div className="relative bg-gradient-to-r from-secondary/10 via-primary/10 to-accent/10 rounded-2xl px-8 py-4 border border-secondary/30">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-r from-secondary to-primary flex items-center justify-center">
                      <Users className="w-6 h-6 text-white" />
                    </div>
                    <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-secondary via-primary to-accent bg-clip-text text-transparent leading-tight">
                      Meet the Team
                    </h2>
                  </div>
                </div>
              </div>
            </div>
            <p className="text-lg sm:text-xl md:text-2xl text-muted-foreground max-w-5xl mx-auto leading-relaxed">
              Behind Nimo is a dedicated team of innovators committed to empowering African youth through technology.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            <Card className="p-6 bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20 hover:shadow-lg transition-all duration-300 group">
              <div className="flex items-start gap-4">
                <div className="relative w-16 h-16 flex-shrink-0">
                  <div className="w-16 h-16 rounded-full overflow-hidden shadow-md group-hover:scale-110 transition-transform duration-300">
                    <img
                      src="/team/john-koiyaki.jpg"
                      alt="John Koiyaki"
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                        const fallback = target.nextElementSibling as HTMLElement;
                        if (fallback) fallback.style.display = 'flex';
                      }}
                    />
                    <div className="w-full h-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center absolute inset-0" style={{ display: 'none' }}>
                      <span className="text-white font-semibold text-lg">JK</span>
                    </div>
                  </div>
                </div>
                <div className="flex-grow min-w-0">
                  <h3 className="text-lg font-semibold mb-1">John Koiyaki</h3>
                  <p className="text-primary text-sm font-medium mb-2">Creative Technologist & Lead Developer</p>
                  <p className="text-xs text-muted-foreground mb-3 leading-relaxed">
                    Software developer and emerging tech educator from Kenya, passionate about building tools that scale knowledge and culture.
                  </p>
                  <div className="flex flex-wrap gap-1">
                    <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20 text-xs px-2 py-0.5">Python</Badge>
                    <Badge variant="secondary" className="bg-secondary/10 text-secondary border-secondary/20 text-xs px-2 py-0.5">Blockchain</Badge>
                    <Badge variant="secondary" className="bg-accent/10 text-accent border-accent/20 text-xs px-2 py-0.5">AI</Badge>
                  </div>
                </div>
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-secondary/5 to-secondary/10 border-secondary/20 hover:shadow-lg transition-all duration-300 group">
              <div className="flex items-start gap-4">
                <div className="relative w-16 h-16 flex-shrink-0">
                  <div className="w-16 h-16 rounded-full overflow-hidden shadow-md group-hover:scale-110 transition-transform duration-300">
                    <img
                      src="/team/aisha-omar-farah.jpg"
                      alt="Aisha Omar Farah"
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                        const fallback = target.nextElementSibling as HTMLElement;
                        if (fallback) fallback.style.display = 'flex';
                      }}
                    />
                    <div className="w-full h-full bg-gradient-to-br from-secondary to-secondary/80 flex items-center justify-center absolute inset-0" style={{ display: 'none' }}>
                      <span className="text-white font-semibold text-lg">AF</span>
                    </div>
                  </div>
                </div>
                <div className="flex-grow min-w-0">
                  <h3 className="text-lg font-semibold mb-1">Aisha Omar Farah</h3>
                  <p className="text-secondary text-sm font-medium mb-2">Frontend & Web3 Developer</p>
                  <p className="text-xs text-muted-foreground mb-3 leading-relaxed">
                    Passionate frontend developer and open-source contributor with expertise in creating modern, interactive designs.
                  </p>
                  <div className="flex flex-wrap gap-1">
                    <Badge variant="secondary" className="bg-secondary/10 text-secondary border-secondary/20 text-xs px-2 py-0.5">React</Badge>
                    <Badge variant="secondary" className="bg-accent/10 text-accent border-accent/20 text-xs px-2 py-0.5">Tailwind</Badge>
                    <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20 text-xs px-2 py-0.5">UI/UX</Badge>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* GitHub Links Section */}
          <div className="text-center mt-8">
            <p className="text-sm text-muted-foreground mb-4">Connect with our team</p>
            <div className="flex justify-center gap-4">
              <a
                href="https://github.com/polymathuniversata"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary/10 text-primary hover:bg-primary/20 transition-colors text-sm font-medium"
              >
                <Github className="w-4 h-4" />
                John's GitHub
              </a>
              <a
                href="https://github.com/Aishagojo"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-secondary/10 text-secondary hover:bg-secondary/20 transition-colors text-sm font-medium"
              >
                <Github className="w-4 h-4" />
                Aisha's GitHub
              </a>
            </div>
          </div>
        </div>
      </section>

      <div className="section-divider"></div>

      {/* CTA Section */}
      <section className="bg-gradient-to-br from-primary via-secondary to-accent text-primary-foreground relative overflow-hidden py-12 sm:py-16 md:py-20 lg:py-24">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="container mx-auto px-4 text-center relative">
          <div className="max-w-5xl mx-auto">
            <div className="inline-flex items-center px-4 sm:px-6 py-2 sm:py-3 rounded-full bg-white/10 text-white text-xs sm:text-sm font-medium mb-4 sm:mb-6 backdrop-blur-sm">
              <Heart className="w-3 h-3 sm:w-4 sm:h-4 mr-2" />
              Join the Movement
            </div>
            <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold mb-4 sm:mb-6 text-white leading-tight">
              Join the Movement
            </h2>
            <p className="text-lg sm:text-xl md:text-2xl mb-6 sm:mb-8 max-w-4xl mx-auto text-white/90 leading-relaxed">
              Nimo is more than just technology; it's a movement to empower African youth and build a more inclusive digital future.
            </p>
            <p className="text-base sm:text-lg md:text-xl mb-8 sm:mb-12 max-w-4xl mx-auto text-white/80 leading-relaxed">
              With your support, we can scale this solution to reach millions, transforming lives and creating lasting change.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 justify-center">
              <Button size="lg" variant="secondary" className="text-base sm:text-lg px-6 sm:px-8 py-3 sm:py-4 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 bg-white text-primary hover:bg-white/90 w-full sm:w-auto" asChild>
                <a href="/register" className="flex items-center justify-center">
                  <Users className="mr-2 w-4 h-4 sm:w-5 sm:h-5" />
                  Join Nimo
                  <ArrowRight className="ml-2 w-4 h-4 sm:w-5 sm:h-5" />
                </a>
              </Button>
              <Button size="lg" variant="outline" className="text-base sm:text-lg px-6 sm:px-8 py-3 sm:py-4 border-2 border-white text-white hover:bg-white hover:text-primary transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 w-full sm:w-auto" asChild>
                <a href="/login" className="flex items-center justify-center">
                  <MapPin className="mr-2 w-4 h-4 sm:w-5 sm:h-5" />
                  Sign In
                  <ArrowRight className="ml-2 w-4 h-4 sm:w-5 sm:h-5" />
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
            <div className="flex flex-col sm:flex-row items-center justify-between mb-4 gap-4">
              <div className="flex items-center">
                <Calendar className="w-4 h-4 mr-2" />
                <p>&copy; 2025 Nimo. All rights reserved.</p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => scrollToSection('home')}
                className="flex items-center gap-2 hover:bg-primary hover:text-white transition-all duration-300"
              >
                <ArrowRight className="w-4 h-4 rotate-180" />
                Back to Top
              </Button>
            </div>
            <p className="text-sm">Empowering African youth through decentralized identity and proof of contribution.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;