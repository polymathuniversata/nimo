/**
 * Migration Progress Tracker Script
 * 
 * This script analyzes the Vue and React components in the frontend
 * and updates the migration-assessment.md file with the current status.
 * 
 * Usage:
 *   node track-migration-progress.js
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const FRONTEND_DIR = path.resolve(__dirname, '../frontend/src');
const PAGES_DIR = path.join(FRONTEND_DIR, 'pages');
const COMPONENTS_DIR = path.join(FRONTEND_DIR, 'components');
const LAYOUTS_DIR = path.join(FRONTEND_DIR, 'layouts');
const MIGRATION_DOC_PATH = path.resolve(__dirname, '../docs/migration-assessment.md');

/**
 * Find all Vue and React components in the specified directories
 * @returns {Object} Object with Vue and React components
 */
function findComponents() {
  const result = {
    vue: {
      pages: [],
      components: [],
      layouts: []
    },
    react: {
      pages: [],
      components: [],
      layouts: []
    }
  };

  // Helper function to find files with specific extensions in a directory
  const findFilesWithExt = (dir, ext) => {
    if (!fs.existsSync(dir)) return [];
    
    return fs.readdirSync(dir)
      .filter(file => file.endsWith(ext))
      .map(file => ({
        name: file,
        path: path.join(dir, file)
      }));
  };

  // Find Vue components
  if (fs.existsSync(PAGES_DIR)) {
    result.vue.pages = findFilesWithExt(PAGES_DIR, '.vue');
  }
  
  if (fs.existsSync(COMPONENTS_DIR)) {
    result.vue.components = findFilesWithExt(COMPONENTS_DIR, '.vue');
  }
  
  if (fs.existsSync(LAYOUTS_DIR)) {
    result.vue.layouts = findFilesWithExt(LAYOUTS_DIR, '.vue');
  }

  // Find React components
  if (fs.existsSync(PAGES_DIR)) {
    result.react.pages = findFilesWithExt(PAGES_DIR, '.tsx')
      .filter(file => !file.name.includes('.test.tsx'));
  }
  
  if (fs.existsSync(COMPONENTS_DIR)) {
    result.react.components = findFilesWithExt(COMPONENTS_DIR, '.tsx')
      .filter(file => !file.name.includes('.test.tsx'));
  }
  
  if (fs.existsSync(LAYOUTS_DIR)) {
    result.react.layouts = findFilesWithExt(LAYOUTS_DIR, '.tsx')
      .filter(file => !file.name.includes('.test.tsx'));
  }

  return result;
}

/**
 * Check if a React component has tests
 * @param {string} componentName - Name of the component without extension
 * @returns {boolean} True if tests exist
 */
function hasTests(componentName) {
  const testFile = path.join(FRONTEND_DIR, 'components', `${componentName}.test.tsx`);
  return fs.existsSync(testFile);
}

/**
 * Map Vue component name to React component name
 * @param {string} vueFileName - Vue file name with extension
 * @returns {string} React file name
 */
function mapVueToReactName(vueFileName) {
  return vueFileName.replace('.vue', '.tsx');
}

/**
 * Check if a component has been imported in other files
 * @param {string} componentName - Name of the component without extension
 * @returns {boolean} True if component is used
 */
function isComponentUsed(componentName) {
  try {
    // Use grep to find imports of this component - use absolute path
    const frontendDirPath = path.resolve(__dirname, '../frontend/src');
    const grepResult = execSync(`grep -r "import ${componentName}" "${frontendDirPath}" --include="*.tsx" | wc -l`, 
      { encoding: 'utf8' });
    return parseInt(grepResult.trim(), 10) > 0;
  } catch (error) {
    console.error(`Error checking if ${componentName} is used:`, error.message);
    return false;
  }
}

/**
 * Analyze component complexity based on file size and content
 * @param {string} filePath - Path to the component file
 * @returns {Object} Complexity metrics
 */
function analyzeComponentComplexity(filePath) {
  try {
    if (!fs.existsSync(filePath)) {
      return { size: 0, linesOfCode: 0, complexity: 'Unknown' };
    }

    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    const size = content.length;
    const linesOfCode = lines.length;
    
    // Count template complexity indicators
    const vForCount = (content.match(/v-for=/g) || []).length;
    const vIfCount = (content.match(/v-if=/g) || []).length;
    const vModelCount = (content.match(/v-model=/g) || []).length;
    const propsCount = (content.match(/defineProps/g) || []).length;
    const emitsCount = (content.match(/defineEmits/g) || []).length;
    const computedCount = (content.match(/computed/g) || []).length;
    
    // Calculate weighted complexity
    const templateComplexity = vForCount * 2 + vIfCount + vModelCount * 1.5;
    const scriptComplexity = propsCount * 2 + emitsCount * 2 + computedCount * 3;
    const totalComplexity = templateComplexity + scriptComplexity;
    
    // Determine complexity level
    let complexity = 'Low';
    if (totalComplexity > 30 || linesOfCode > 300) {
      complexity = 'High';
    } else if (totalComplexity > 15 || linesOfCode > 150) {
      complexity = 'Medium';
    }
    
    return {
      size,
      linesOfCode,
      templateComplexity,
      scriptComplexity,
      totalComplexity,
      complexity
    };
  } catch (error) {
    console.error(`Error analyzing complexity for ${filePath}:`, error);
    return { size: 0, linesOfCode: 0, complexity: 'Unknown' };
  }
}

/**
 * Check if component is a core UI component
 * @param {string} componentName - Name of the component
 * @returns {boolean} True if it's a core UI component
 */
function isCoreUIComponent(componentName) {
  const coreComponentPatterns = [
    'button', 'card', 'input', 'form', 'nav', 'header', 'footer', 
    'sidebar', 'modal', 'dialog', 'menu', 'list', 'table', 'layout'
  ];
  
  const lowerName = componentName.toLowerCase();
  return coreComponentPatterns.some(pattern => lowerName.includes(pattern));
}

/**
 * Determine migration priority based on component attributes
 * @param {Object} component - Component information
 * @param {Object} complexity - Component complexity metrics
 * @returns {string} Priority level
 */
function determineMigrationPriority(component, complexity) {
  // Core UI components should be migrated first
  if (isCoreUIComponent(component.name)) {
    return 'High';
  }
  
  // Pages have higher priority than regular components
  if (component.path.includes('/pages/')) {
    if (component.name.includes('Dashboard') || 
        component.name.includes('Index') || 
        component.name.includes('Login')) {
      return 'High';
    }
    return 'Medium';
  }
  
  // Consider complexity
  if (complexity.complexity === 'High') {
    return 'Medium'; // Complex components need more planning
  } else if (complexity.complexity === 'Low') {
    return 'High'; // Simple components are easier to migrate
  }
  
  return 'Medium';
}

/**
 * Generate migration status for components
 * @param {Object} components - Object with Vue and React components
 * @returns {Object} Migration status
 */
function generateMigrationStatus(components) {
  const status = {
    pages: [],
    components: [],
    layouts: [],
    recommendations: []
  };

  // Process pages
  for (const vuePage of components.vue.pages) {
    const baseName = vuePage.name.replace('.vue', '');
    const reactName = mapVueToReactName(vuePage.name);
    const reactPage = components.react.pages.find(p => p.name === reactName);
    
    // Analyze complexity
    const complexity = analyzeComponentComplexity(vuePage.path);
    const priority = reactPage ? 'Completed' : determineMigrationPriority(vuePage, complexity);
    
    const pageInfo = {
      vueName: vuePage.name,
      reactName,
      status: reactPage ? 'Completed' : 'Not Started',
      deleteVue: reactPage ? '✅ Yes' : 'No',
      complexity: complexity.complexity,
      priority
    };
    
    status.pages.push(pageInfo);
    
    // Add to recommendations if not completed and high priority
    if (!reactPage && priority === 'High') {
      status.recommendations.push({
        type: 'Page',
        ...pageInfo
      });
    }
  }

  // Process components
  for (const vueComponent of components.vue.components) {
    const baseName = vueComponent.name.replace('.vue', '');
    const reactName = mapVueToReactName(vueComponent.name);
    const reactComponent = components.react.components.find(c => c.name === reactName);
    
    // Analyze complexity
    const complexity = analyzeComponentComplexity(vueComponent.path);
    const priority = reactComponent ? 'Completed' : determineMigrationPriority(vueComponent, complexity);
    
    const componentInfo = {
      vueName: vueComponent.name,
      reactName,
      status: reactComponent ? 'Completed' : 'Not Started',
      deleteVue: reactComponent && hasTests(baseName) && isComponentUsed(baseName) ? '✅ Yes' : 'No',
      complexity: complexity.complexity,
      priority
    };
    
    status.components.push(componentInfo);
    
    // Add to recommendations if not completed and high priority
    if (!reactComponent && priority === 'High') {
      status.recommendations.push({
        type: 'Component',
        ...componentInfo
      });
    }
  }

  // Process layouts
  for (const vueLayout of components.vue.layouts) {
    const baseName = vueLayout.name.replace('.vue', '');
    const reactName = mapVueToReactName(vueLayout.name);
    const reactLayout = components.react.layouts.find(l => l.name === reactName);
    
    // Analyze complexity
    const complexity = analyzeComponentComplexity(vueLayout.path);
    const priority = reactLayout ? 'Completed' : determineMigrationPriority(vueLayout, complexity);
    
    const layoutInfo = {
      vueName: vueLayout.name,
      reactName,
      status: reactLayout ? 'Completed' : 'Not Started',
      deleteVue: reactLayout ? '✅ Yes' : 'No',
      complexity: complexity.complexity,
      priority
    };
    
    status.layouts.push(layoutInfo);
    
    // Add to recommendations if not completed and high priority
    if (!reactLayout && priority === 'High') {
      status.recommendations.push({
        type: 'Layout',
        ...layoutInfo
      });
    }
  }

  // Sort recommendations by priority (keeping 'High' at the top)
  status.recommendations.sort((a, b) => {
    if (a.priority === b.priority) {
      if (a.complexity === b.complexity) {
        return a.vueName.localeCompare(b.vueName);
      }
      return a.complexity === 'Low' ? -1 : 1;
    }
    return a.priority === 'High' ? -1 : 1;
  });

  return status;
}

/**
 * Update the migration-assessment.md file with the current status
 * @param {Object} status - Migration status object
 */
function updateMigrationDoc(status) {
  if (!fs.existsSync(MIGRATION_DOC_PATH)) {
    console.error('Migration assessment document not found:', MIGRATION_DOC_PATH);
    return;
  }

  // Read the current document
  let docContent = fs.readFileSync(MIGRATION_DOC_PATH, 'utf8');

  // Generate pages table content
  let pagesTable = '| Vue Component | React Component | Status | Complexity | Priority | Delete Vue File? |\n';
  pagesTable += '|---------------|----------------|--------|------------|----------|------------------|\n';
  
  for (const page of status.pages) {
    pagesTable += `| \`${page.vueName}\` | \`${page.reactName}\` | ${page.status} | ${page.complexity || 'N/A'} | ${page.priority || 'N/A'} | ${page.deleteVue} |\n`;
  }

  // Calculate statistics
  const totalPages = status.pages.length;
  const completedPages = status.pages.filter(p => p.status === 'Completed').length;
  const totalComponents = status.components.length;
  const completedComponents = status.components.filter(c => c.status === 'Completed').length;
  const totalLayouts = status.layouts.length;
  const completedLayouts = status.layouts.filter(l => l.status === 'Completed').length;

  // Create statistics section
  const statsSection = `## Migration Statistics

| Category | Total | Migrated | Remaining | Progress |
|----------|-------|----------|-----------|----------|
| Pages    | ${totalPages} | ${completedPages} | ${totalPages - completedPages} | ${Math.round((completedPages / totalPages) * 100)}% |
| Components | ${totalComponents} | ${completedComponents} | ${totalComponents - completedComponents} | ${Math.round((completedComponents / totalComponents) * 100)}% |
| Layouts  | ${totalLayouts} | ${completedLayouts} | ${totalLayouts - completedLayouts} | ${Math.round((completedLayouts / totalLayouts) * 100)}% |
`;

  // Create recommendations section
  let recommendationsSection = `## Migration Recommendations

The following components are recommended for migration in priority order:

| Type | Vue Component | Complexity | Priority |
|------|--------------|------------|----------|
`;

  // Add recommendations to the table
  status.recommendations.slice(0, 10).forEach(rec => {
    recommendationsSection += `| ${rec.type} | \`${rec.vueName}\` | ${rec.complexity} | ${rec.priority} |\n`;
  });

  // Look for the pages table marker and update it
  const pagesTablePattern = /### Pages Migration Status\n\n\|[^]*?\n\n/;
  if (docContent.match(pagesTablePattern)) {
    docContent = docContent.replace(pagesTablePattern, `### Pages Migration Status\n\n${pagesTable}\n\n`);
  }

  // Look for the stats section and update it
  const statsPattern = /## Migration Statistics\n\n\|[^]*?\n\n/;
  if (docContent.match(statsPattern)) {
    docContent = docContent.replace(statsPattern, `${statsSection}\n\n`);
  } else {
    // If stats section doesn't exist, add it after the "Component Migration Tracker" heading
    const trackerHeading = /## Component Migration Tracker/;
    if (docContent.match(trackerHeading)) {
      docContent = docContent.replace(trackerHeading, `## Migration Statistics\n\n${statsSection}\n\n## Component Migration Tracker`);
    }
  }

  // Look for the recommendations section and update it
  const recommendationsPattern = /## Migration Recommendations\n\nThe following components[^]*?\|[^]*?\n\n/;
  if (docContent.match(recommendationsPattern)) {
    docContent = docContent.replace(recommendationsPattern, `${recommendationsSection}\n\n`);
  } else {
    // If recommendations section doesn't exist, add it after the statistics section
    const statsHeading = /## Migration Statistics/;
    if (docContent.match(statsHeading)) {
      docContent = docContent.replace(statsHeading, `${recommendationsSection}\n\n## Migration Statistics`);
    }
  }

  // Write the updated document
  fs.writeFileSync(MIGRATION_DOC_PATH, docContent, 'utf8');
  console.log('Migration assessment document updated successfully.');
  
  // Log recommendations to the console for easy access
  console.log('\nTop Migration Recommendations:');
  console.log('-----------------------------');
  status.recommendations.slice(0, 5).forEach((rec, index) => {
    console.log(`${index + 1}. ${rec.vueName} (${rec.type}, ${rec.complexity} complexity, ${rec.priority} priority)`);
  });
}

/**
 * Main function
 */
function main() {
  console.log('Running Migration Progress Tracker...');

  // Find all Vue and React components
  const components = findComponents();
  console.log(`Found ${components.vue.pages.length} Vue pages and ${components.react.pages.length} React pages`);
  console.log(`Found ${components.vue.components.length} Vue components and ${components.react.components.length} React components`);
  console.log(`Found ${components.vue.layouts.length} Vue layouts and ${components.react.layouts.length} React layouts`);

  // Generate migration status
  const status = generateMigrationStatus(components);

  // Update the migration document
  updateMigrationDoc(status);

  console.log('Migration progress tracking completed.');
}

// Run the script
main();