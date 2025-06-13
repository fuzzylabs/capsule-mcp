#!/usr/bin/env node

/**
 * Generate Cursor deeplink for MCP server installation
 * 
 * This script generates the base64-encoded configuration URL for Cursor's
 * MCP deeplink installation feature. Run this whenever the server configuration
 * changes to keep the README.md deeplink in sync.
 * 
 * Usage:
 *   node scripts/generate-cursor-link.js
 *   node scripts/generate-cursor-link.js --custom-path /my/custom/path
 */

const fs = require('fs');
const path = require('path');

// Default configuration template
const DEFAULT_CONFIG = {
  'capsule-crm': {
    command: 'uv',
    args: [
      'run',
      '--directory',
      '/path/to/your/capsule-mcp',
      'python',
      'capsule_mcp/server.py'
    ],
    env: {
      CAPSULE_API_TOKEN: 'your_capsule_api_token_here'
    }
  }
};

function generateDeeplink(config = DEFAULT_CONFIG, serverName = 'capsule-crm') {
  const configJson = JSON.stringify(config);
  const base64Config = Buffer.from(configJson).toString('base64');
  const deeplink = `cursor://anysphere.cursor-deeplink/mcp/install?name=${serverName}&config=${base64Config}`;
  
  return {
    config: config,
    configJson: configJson,
    base64Config: base64Config,
    deeplink: deeplink
  };
}

function updateReadme(deeplink) {
  const readmePath = path.join(__dirname, '..', 'README.md');
  
  if (!fs.existsSync(readmePath)) {
    console.error('❌ README.md not found');
    return false;
  }
  
  let content = fs.readFileSync(readmePath, 'utf8');
  
  // Find and replace the Cursor deeplink
  const linkPattern = /(<a href="cursor:\/\/[^"]*"[^>]*>)/;
  const match = content.match(linkPattern);
  
  if (match) {
    const oldLink = match[1];
    const newLink = oldLink.replace(/cursor:\/\/[^"]*/, deeplink);
    content = content.replace(oldLink, newLink);
    
    fs.writeFileSync(readmePath, content);
    console.log('✅ README.md updated with new Cursor deeplink');
    return true;
  } else {
    console.error('❌ Could not find Cursor deeplink in README.md');
    return false;
  }
}

function main() {
  const args = process.argv.slice(2);
  const customPathIndex = args.indexOf('--custom-path');
  
  let config = { ...DEFAULT_CONFIG };
  
  // Handle custom path argument
  if (customPathIndex !== -1 && args[customPathIndex + 1]) {
    const customPath = args[customPathIndex + 1];
    config['capsule-crm'].args[2] = customPath;
    console.log(`📁 Using custom path: ${customPath}`);
  }
  
  console.log('🔧 Generating Cursor deeplink...\n');
  
  const result = generateDeeplink(config);
  
  console.log('📋 Configuration:');
  console.log(JSON.stringify(result.config, null, 2));
  console.log('\n🔗 Deeplink:');
  console.log(result.deeplink);
  console.log('\n📦 Base64 Config:');
  console.log(result.base64Config);
  
  // Update README.md
  console.log('\n📝 Updating README.md...');
  const updated = updateReadme(result.deeplink);
  
  if (updated) {
    console.log('\n✅ All done! README.md has been updated with the new deeplink.');
    console.log('💡 Don\'t forget to commit the changes.');
  } else {
    console.log('\n⚠️  README.md was not updated. You may need to manually replace the deeplink.');
  }
  
  // Validation reminder
  console.log('\n🔍 Next steps:');
  console.log('1. Review the updated README.md');
  console.log('2. Test the deeplink in Cursor');
  console.log('3. Run: python scripts/validate-configs.py');
  console.log('4. Commit your changes');
}

if (require.main === module) {
  main();
}

module.exports = { generateDeeplink, updateReadme };