/**
 * Vue Component Cleanup Script
 * 
 * This script helps clean up Vue component files that have been successfully 
 * migrated to React. It compares the migration status in the migration-assessment.md 
 * document and deletes Vue files marked for deletion.
 * 
 * Usage: 
 *   node cleanup-vue-files.js [--dry-run] [--force]
 * 
 * Options:
 *   --dry-run   Show which files would be deleted without actually deleting them
 *   --force     Skip confirmation and delete files immediately
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Configuration
const MIGRATION_DOC_PATH = path.resolve(__dirname, '../docs/migration-assessment.md');
const FRONTEND_SRC_PATH = path.resolve(__dirname, '../frontend/src');

// Parse command line arguments
const args = process.argv.slice(2);
const DRY_RUN = args.includes('--dry-run');
const FORCE = args.includes('--force');

/**
 * Parse the migration assessment document to find Vue files ready for deletion
 * @returns {Array<{vueFile: string, reactFile: string, status: string}>}
 */
function parseMigrationDocument() {
  try {
    const content = fs.readFileSync(MIGRATION_DOC_PATH, 'utf8');
    
    // Find the component migration table
    const tableRegex = /\| `([^`]+\.vue)` \| `([^`]+\.tsx)` \| ([^|]+) \| ([^|]+) \|/g;
    const components = [];
    
    let match;
    while ((match = tableRegex.exec(content)) !== null) {
      const vueFile = match[1];
      const reactFile = match[2];
      const status = match[3].trim();
      const deleteFlag = match[4].trim();
      
      // Only add components marked for deletion with "Yes" or "✅ Yes"
      if (status === 'Completed' && (deleteFlag === 'Yes' || deleteFlag.includes('✅'))) {
        components.push({ vueFile, reactFile, status });
      }
    }
    
    return components;
  } catch (err) {
    console.error('Error reading migration document:', err);
    return [];
  }
}

/**
 * Check if a React file exists in the frontend/src directory
 * @param {string} reactFilename - React filename like "ComponentName.tsx"
 * @returns {boolean}
 */
function checkReactFileExists(reactFilename) {
  // Look for the React file in the entire src directory
  let found = false;
  
  function searchDirectory(dirPath) {
    const files = fs.readdirSync(dirPath);
    
    for (const file of files) {
      const fullPath = path.join(dirPath, file);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory()) {
        searchDirectory(fullPath);
      } else if (file === reactFilename) {
        found = true;
        return;
      }
    }
  }
  
  searchDirectory(FRONTEND_SRC_PATH);
  return found;
}

/**
 * Find all instances of a Vue file in the frontend/src directory
 * @param {string} vueFilename - Vue filename like "ComponentName.vue"
 * @returns {Array<string>} - Array of full paths to the Vue file
 */
function findVueFiles(vueFilename) {
  const vuePaths = [];
  
  function searchDirectory(dirPath) {
    const files = fs.readdirSync(dirPath);
    
    for (const file of files) {
      const fullPath = path.join(dirPath, file);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory()) {
        searchDirectory(fullPath);
      } else if (file === vueFilename) {
        vuePaths.push(fullPath);
      }
    }
  }
  
  searchDirectory(FRONTEND_SRC_PATH);
  return vuePaths;
}

/**
 * Delete a file with confirmation
 * @param {string} filePath - Path to the file to delete
 * @returns {Promise<boolean>} - Whether the file was deleted
 */
async function deleteFileWithConfirmation(filePath) {
  if (DRY_RUN) {
    console.log(`[DRY RUN] Would delete: ${filePath}`);
    return true;
  }
  
  if (FORCE) {
    try {
      fs.unlinkSync(filePath);
      console.log(`Deleted: ${filePath}`);
      return true;
    } catch (err) {
      console.error(`Failed to delete ${filePath}:`, err);
      return false;
    }
  }
  
  // Interactive confirmation
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  return new Promise((resolve) => {
    rl.question(`Delete ${filePath}? (y/n) `, (answer) => {
      rl.close();
      
      if (answer.toLowerCase() === 'y') {
        try {
          fs.unlinkSync(filePath);
          console.log(`Deleted: ${filePath}`);
          resolve(true);
        } catch (err) {
          console.error(`Failed to delete ${filePath}:`, err);
          resolve(false);
        }
      } else {
        console.log(`Skipped: ${filePath}`);
        resolve(false);
      }
    });
  });
}

/**
 * Main function to run the cleanup process
 */
async function main() {
  console.log('Vue Component Cleanup Script');
  console.log('===========================');
  
  if (DRY_RUN) {
    console.log('Running in DRY RUN mode - no files will be deleted');
  }
  
  // Get components ready for deletion
  const componentsToDelete = parseMigrationDocument();
  
  if (componentsToDelete.length === 0) {
    console.log('No Vue components are marked for deletion in the migration document.');
    return;
  }
  
  console.log(`Found ${componentsToDelete.length} components marked for deletion.`);
  
  for (const component of componentsToDelete) {
    console.log(`\nProcessing: ${component.vueFile} → ${component.reactFile}`);
    
    // Check if React file exists
    const reactFileExists = checkReactFileExists(component.reactFile);
    
    if (!reactFileExists) {
      console.warn(`Warning: React file ${component.reactFile} not found. Skipping deletion of ${component.vueFile}`);
      continue;
    }
    
    // Find Vue files to delete
    const vueFilePaths = findVueFiles(component.vueFile);
    
    if (vueFilePaths.length === 0) {
      console.log(`No instances of ${component.vueFile} found.`);
      continue;
    }
    
    console.log(`Found ${vueFilePaths.length} instance(s) of ${component.vueFile}`);
    
    // Delete each instance
    for (const filePath of vueFilePaths) {
      await deleteFileWithConfirmation(filePath);
    }
  }
  
  console.log('\nCleanup process completed.');
}

// Run the script
main().catch(err => {
  console.error('Error running cleanup script:', err);
  process.exit(1);
});