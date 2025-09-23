import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useTheme } from '@/hooks/useTheme';
import { Sun, Moon, Monitor, Palette, CheckCircle, AlertTriangle, XCircle, Info } from 'lucide-react';

export const ColorSystemTest: React.FC = () => {
  const { theme, setTheme, actualTheme } = useTheme();

  const colorTests = [
    {
      name: 'Primary Colors',
      colors: [
        { name: 'Primary 500', class: 'bg-primary text-primary-foreground' },
        { name: 'Primary 400', class: 'bg-primary/80 text-primary-foreground' },
        { name: 'Primary 600', class: 'bg-primary/120 text-primary-foreground' },
      ]
    },
    {
      name: 'Secondary Colors',
      colors: [
        { name: 'Secondary 500', class: 'bg-secondary text-secondary-foreground' },
        { name: 'Secondary 400', class: 'bg-secondary/80 text-secondary-foreground' },
        { name: 'Secondary 600', class: 'bg-secondary/120 text-secondary-foreground' },
      ]
    },
    {
      name: 'Semantic Colors',
      colors: [
        { name: 'Success', class: 'bg-verification-green text-white' },
        { name: 'Warning', class: 'bg-token-gold text-white' },
        { name: 'Error', class: 'bg-destructive text-destructive-foreground' },
        { name: 'Info', class: 'bg-impact-blue text-white' },
      ]
    }
  ];

  return (
    <div className="p-8 space-y-8 bg-background text-foreground min-h-screen">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              Nimo Color System Test
            </h1>
            <p className="text-muted-foreground mt-2">
              Testing enhanced colors and dark mode visibility across all themes
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <Badge variant="outline" className="text-sm">
              Current: {theme} ({actualTheme})
            </Badge>
            <div className="flex gap-2">
              <Button
                variant={theme === 'light' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setTheme('light')}
              >
                <Sun className="w-4 h-4 mr-2" />
                Light
              </Button>
              <Button
                variant={theme === 'dark' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setTheme('dark')}
              >
                <Moon className="w-4 h-4 mr-2" />
                Dark
              </Button>
              <Button
                variant={theme === 'system' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setTheme('system')}
              >
                <Monitor className="w-4 h-4 mr-2" />
                System
              </Button>
            </div>
          </div>
        </div>

        {/* Color Palette Tests */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {colorTests.map((section) => (
            <Card key={section.name} variant="elevated" className="p-6">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg">{section.name}</CardTitle>
                <CardDescription>
                  Testing contrast and visibility in {actualTheme} mode
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {section.colors.map((color) => (
                  <div
                    key={color.name}
                    className={`${color.class} p-4 rounded-lg text-center font-medium transition-all hover:scale-105`}
                  >
                    {color.name}
                  </div>
                ))}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Button Variants Test */}
        <Card variant="outlined" className="p-6 mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Palette className="w-5 h-5" />
              Button Variants & Interactions
            </CardTitle>
            <CardDescription>
              Testing all button styles with enhanced shadows and hover effects
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              <Button variant="default">Default</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="gradient">Gradient</Button>
              <Button variant="destructive">Destructive</Button>
              <Button variant="success">Success</Button>
              <Button variant="warning">Warning</Button>
            </div>
          </CardContent>
        </Card>

        {/* Card Variants Test */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card variant="default" hover>
            <CardHeader>
              <CardTitle className="text-base">Default Card</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Standard card with hover effects and proper contrast.
              </p>
            </CardContent>
          </Card>

          <Card variant="elevated" hover>
            <CardHeader>
              <CardTitle className="text-base">Elevated Card</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Enhanced shadow and gradient background.
              </p>
            </CardContent>
          </Card>

          <Card variant="outlined" hover>
            <CardHeader>
              <CardTitle className="text-base">Outlined Card</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Prominent border with hover shadow.
              </p>
            </CardContent>
          </Card>

          <Card variant="gradient" hover>
            <CardHeader>
              <CardTitle className="text-base">Gradient Card</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Subtle gradient with glow effect.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Status Indicators Test */}
        <Card variant="default" className="p-6 mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-verification-green" />
              Status Indicators & Badges
            </CardTitle>
            <CardDescription>
              Testing semantic colors and accessibility in {actualTheme} mode
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-verification-green" />
                <Badge className="bg-verification-green/10 text-verification-green border-verification-green/20">
                  Success
                </Badge>
              </div>
              
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-token-gold" />
                <Badge className="bg-token-gold/10 text-token-gold border-token-gold/20">
                  Warning
                </Badge>
              </div>
              
              <div className="flex items-center gap-2">
                <XCircle className="w-4 h-4 text-destructive" />
                <Badge className="bg-destructive/10 text-destructive border-destructive/20">
                  Error
                </Badge>
              </div>
              
              <div className="flex items-center gap-2">
                <Info className="w-4 h-4 text-impact-blue" />
                <Badge className="bg-impact-blue/10 text-impact-blue border-impact-blue/20">
                  Info
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Accessibility Notes */}
        <Card variant="outlined" className="p-6">
          <CardHeader>
            <CardTitle className="text-lg text-verification-green">
              ✓ Accessibility Improvements
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold mb-2">Dark Mode Enhancements:</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Brighter primary colors for better visibility</li>
                  <li>• Enhanced shadow opacity for depth perception</li>
                  <li>• Improved text contrast ratios (4.5:1+)</li>
                  <li>• Better border visibility and separation</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-2">UX Improvements:</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Smooth theme transitions (300ms)</li>
                  <li>• System theme preference detection</li>
                  <li>• Enhanced focus indicators</li>
                  <li>• Reduced motion support</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ColorSystemTest;