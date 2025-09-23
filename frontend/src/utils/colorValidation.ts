/**
 * Color validation utilities for accessibility and brand compliance
 */

export interface ColorContrastResult {
  ratio: number;
  level: 'AAA' | 'AA' | 'A' | 'FAIL';
  passes: boolean;
}

export interface ColorValidationResult {
  isValid: boolean;
  contrast: ColorContrastResult;
  recommendations?: string[];
}

/**
 * Convert HSL to RGB
 */
function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  h /= 360;
  s /= 100;
  l /= 100;

  const c = (1 - Math.abs(2 * l - 1)) * s;
  const x = c * (1 - Math.abs((h * 6) % 2 - 1));
  const m = l - c / 2;

  let r = 0, g = 0, b = 0;

  if (0 <= h && h < 1/6) {
    r = c; g = x; b = 0;
  } else if (1/6 <= h && h < 1/3) {
    r = x; g = c; b = 0;
  } else if (1/3 <= h && h < 1/2) {
    r = 0; g = c; b = x;
  } else if (1/2 <= h && h < 2/3) {
    r = 0; g = x; b = c;
  } else if (2/3 <= h && h < 5/6) {
    r = x; g = 0; b = c;
  } else if (5/6 <= h && h < 1) {
    r = c; g = 0; b = x;
  }

  return [
    Math.round((r + m) * 255),
    Math.round((g + m) * 255),
    Math.round((b + m) * 255)
  ];
}

/**
 * Calculate relative luminance of a color
 */
function getLuminance(r: number, g: number, b: number): number {
  const [rs, gs, bs] = [r, g, b].map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

/**
 * Calculate contrast ratio between two colors
 */
export function calculateContrastRatio(
  color1: [number, number, number],
  color2: [number, number, number]
): number {
  const lum1 = getLuminance(...color1);
  const lum2 = getLuminance(...color2);
  
  const brightest = Math.max(lum1, lum2);
  const darkest = Math.min(lum1, lum2);
  
  return (brightest + 0.05) / (darkest + 0.05);
}

/**
 * Parse HSL color string to RGB
 */
export function parseHslToRgb(hslString: string): [number, number, number] {
  const match = hslString.match(/hsl\((\d+)\s+(\d+)%\s+(\d+)%\)/);
  if (!match) {
    throw new Error(`Invalid HSL color string: ${hslString}`);
  }
  
  const [, h, s, l] = match.map(Number);
  return hslToRgb(h, s, l);
}

/**
 * Validate color contrast for accessibility
 */
export function validateColorContrast(
  foreground: string,
  background: string,
  fontSize: number = 16,
  isBold: boolean = false
): ColorValidationResult {
  try {
    const fgRgb = parseHslToRgb(foreground);
    const bgRgb = parseHslToRgb(background);
    
    const ratio = calculateContrastRatio(fgRgb, bgRgb);
    
    // Determine required contrast ratio based on text size
    const isLargeText = fontSize >= 18 || (fontSize >= 14 && isBold);
    const requiredRatio = isLargeText ? 3.0 : 4.5;
    const aaaRatio = isLargeText ? 4.5 : 7.0;
    
    let level: ColorContrastResult['level'];
    if (ratio >= aaaRatio) {
      level = 'AAA';
    } else if (ratio >= requiredRatio) {
      level = 'AA';
    } else if (ratio >= 3.0) {
      level = 'A';
    } else {
      level = 'FAIL';
    }
    
    const passes = ratio >= requiredRatio;
    
    const recommendations: string[] = [];
    if (!passes) {
      recommendations.push(
        `Contrast ratio ${ratio.toFixed(2)}:1 is below the required ${requiredRatio}:1`
      );
      recommendations.push(
        'Consider using a darker foreground or lighter background color'
      );
    }
    
    return {
      isValid: passes,
      contrast: { ratio, level, passes },
      recommendations: recommendations.length > 0 ? recommendations : undefined
    };
  } catch (error) {
    return {
      isValid: false,
      contrast: { ratio: 0, level: 'FAIL', passes: false },
      recommendations: [`Error validating colors: ${error}`]
    };
  }
}

/**
 * Nimo brand color definitions for validation
 */
export const NIMO_COLORS = {
  light: {
    primary: 'hsl(231 48% 48%)',
    primaryForeground: 'hsl(210 40% 98%)',
    secondary: 'hsl(280 65% 60%)',
    secondaryForeground: 'hsl(210 40% 98%)',
    background: 'hsl(0 0% 100%)',
    foreground: 'hsl(222.2 84% 4.9%)',
    muted: 'hsl(210 40% 96.1%)',
    mutedForeground: 'hsl(215.4 16.3% 46.9%)',
  },
  dark: {
    primary: 'hsl(231 81% 74%)',
    primaryForeground: 'hsl(222.2 84% 4.9%)',
    secondary: 'hsl(280 71% 76%)',
    secondaryForeground: 'hsl(222.2 84% 4.9%)',
    background: 'hsl(222.2 84% 4.9%)',
    foreground: 'hsl(210 40% 98%)',
    muted: 'hsl(223 47% 11%)',
    mutedForeground: 'hsl(215.4 16.3% 65.9%)',
  }
};

/**
 * Validate all Nimo brand colors for accessibility
 */
export function validateNimoBrandColors(): Record<string, Record<string, ColorValidationResult>> {
  const results: Record<string, Record<string, ColorValidationResult>> = {};
  
  Object.entries(NIMO_COLORS).forEach(([theme, colors]) => {
    results[theme] = {};
    
    // Test primary combinations
    results[theme].primary = validateColorContrast(
      colors.primaryForeground,
      colors.primary
    );
    
    // Test secondary combinations
    results[theme].secondary = validateColorContrast(
      colors.secondaryForeground,
      colors.secondary
    );
    
    // Test body text
    results[theme].bodyText = validateColorContrast(
      colors.foreground,
      colors.background
    );
    
    // Test muted text
    results[theme].mutedText = validateColorContrast(
      colors.mutedForeground,
      colors.background
    );
  });
  
  return results;
}

/**
 * Generate accessibility report for the color system
 */
export function generateAccessibilityReport(): {
  summary: {
    totalTests: number;
    passed: number;
    failed: number;
    passRate: number;
  };
  details: Record<string, Record<string, ColorValidationResult>>;
  recommendations: string[];
} {
  const details = validateNimoBrandColors();
  
  let totalTests = 0;
  let passed = 0;
  const recommendations: string[] = [];
  
  Object.entries(details).forEach(([theme, tests]) => {
    Object.entries(tests).forEach(([testName, result]) => {
      totalTests++;
      if (result.isValid) {
        passed++;
      } else {
        recommendations.push(`${theme} theme - ${testName}: ${result.recommendations?.join(', ')}`);
      }
    });
  });
  
  return {
    summary: {
      totalTests,
      passed,
      failed: totalTests - passed,
      passRate: (passed / totalTests) * 100
    },
    details,
    recommendations
  };
}