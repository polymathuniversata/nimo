#!/usr/bin/env node

/**
 * Simple validation script for the Nimo color system
 */

const fs = require('fs');
const path = require('path');

console.log('🎨 Validating Nimo Color System...\n');

// Read the main CSS file
const cssPath = path.join(__dirname, 'src', 'index.css');
const cssContent = fs.readFileSync(cssPath, 'utf8');

// Check for required color variables
const requiredVariables = [
  '--primary',
  '--primary-foreground',
  '--secondary',
  '--secondary-foreground',
  '--background',
  '--foreground',
  '--shadow-button',
  '--shadow-button-hover',
  '--shadow-glow-hover'
];

console.log('✅ Checking required CSS variables:');
let missingVariables = [];

requiredVariables.forEach(variable => {
  if (cssContent.includes(variable)) {
    console.log(`   ✓ ${variable}`);
  } else {
    console.log(`   ✗ ${variable} - MISSING`);
    missingVariables.push(variable);
  }
});

// Check for dark theme implementation
console.log('\n✅ Checking dark theme implementation:');
if (cssContent.includes('.dark {')) {
  console.log('   ✓ Dark theme class found');
  
  // Check for enhanced dark mode colors
  const darkModeChecks = [
    'hsl(231 81% 74%)', // Enhanced primary for dark mode
    'hsl(280 71% 76%)', // Enhanced secondary for dark mode
  ];
  
  darkModeChecks.forEach((color, index) => {
    if (cssContent.includes(color)) {
      console.log(`   ✓ Enhanced dark mode color ${index + 1}`);
    } else {
      console.log(`   ⚠ Enhanced dark mode color ${index + 1} not found`);
    }
  });
} else {
  console.log('   ✗ Dark theme implementation not found');
}

// Check Tailwind config
console.log('\n✅ Checking Tailwind configuration:');
const tailwindPath = path.join(__dirname, 'tailwind.config.ts');
if (fs.existsSync(tailwindPath)) {
  const tailwindContent = fs.readFileSync(tailwindPath, 'utf8');
  
  const tailwindChecks = [
    'shadow-button',
    'shadow-button-hover',
    'shadow-glow-hover'
  ];
  
  tailwindChecks.forEach(shadow => {
    if (tailwindContent.includes(`'${shadow}'`)) {
      console.log(`   ✓ ${shadow} shadow defined`);
    } else {
      console.log(`   ✗ ${shadow} shadow missing`);
    }
  });
} else {
  console.log('   ✗ Tailwind config not found');
}

// Check component files
console.log('\n✅ Checking component implementations:');
const componentChecks = [
  { file: 'src/components/ColorSystemTest.tsx', name: 'Color System Test Component' },
  { file: 'src/utils/colorValidation.ts', name: 'Color Validation Utilities' },
  { file: 'src/contexts/ThemeContext.tsx', name: 'Theme Context' }
];

componentChecks.forEach(({ file, name }) => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    console.log(`   ✓ ${name}`);
  } else {
    console.log(`   ✗ ${name} - MISSING`);
  }
});

// Summary
console.log('\n📊 Validation Summary:');
if (missingVariables.length === 0) {
  console.log('   ✅ All required CSS variables are present');
} else {
  console.log(`   ⚠ ${missingVariables.length} missing CSS variables`);
}

console.log('\n🎯 Next Steps:');
console.log('   1. Test the ColorSystemTest component in your app');
console.log('   2. Run accessibility validation with colorValidation utils');
console.log('   3. Verify theme switching works correctly');
console.log('   4. Test dark mode visibility improvements');

console.log('\n✨ Color system validation complete!');