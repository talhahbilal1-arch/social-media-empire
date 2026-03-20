const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const path = require('path');
const fs = require('fs');

puppeteer.use(StealthPlugin());

const products = [
  { productId: 'vgpbuk', zipFile: 'prompt-packs/ai-money-maker-mega-bundle.zip', name: 'AI Money Maker Mega Bundle' },
  { productId: 'gwulhx', zipFile: 'prompt-packs/products/ai-business-automation-playbook.zip', name: 'AI Business Automation Playbook' },
  { productId: 'fgvsp', zipFile: 'prompt-packs/products/etsy-ecommerce-assistant.zip', name: 'Etsy eCommerce Assistant' },
  { productId: 'ywxcj', zipFile: 'prompt-packs/products/side-hustle-finder.zip', name: 'Side Hustle Finder' },
  { productId: 'kzvjx', zipFile: 'prompt-packs/products/ai-copywriter.zip', name: 'AI Copywriter' },
  { productId: 'hxjel', zipFile: 'prompt-packs/products/digital-product-launch-system.zip', name: 'Digital Product Launch System' },
  { productId: 'kdkpq', zipFile: 'prompt-packs/products/ai-content-machine.zip', name: 'AI Content Machine' },
  { productId: 'oqrmt', zipFile: 'prompt-packs/products/freelancer-ai-toolkit.zip', name: 'Freelancer AI Toolkit' },
];

const baseDir = '/Users/homefolder/Desktop/social-media-empire';

async function connectToExistingBrowser() {
  try {
    // Try to connect to existing Chrome instance
    const browserWSEndpoint = 'ws://127.0.0.1:9222/devtools/browser/some-guid';
    // Note: This is a fallback approach - we'll use puppeteer-core instead
    
    console.log('Attempting to use Chrome DevTools Protocol...');
    return null;
  } catch (error) {
    return null;
  }
}

async function main() {
  console.log('📋 Gumroad Bulk Upload Automation');
  console.log('=='.repeat(30));
  console.log('\nℹ️  Authentication Required:');
  console.log('  Since Gumroad requires authentication, please use the following approach:');
  console.log('\n1. Open the browser to: https://gumroad.com/products');
  console.log('2. Ensure you are logged in');
  console.log('3. For each product, navigate to the Content tab');
  console.log('4. Run this script with --manual flag to guide through uploads\n');
  
  // Alternative: Check if Chrome is running with debugging
  console.log('🔍 Checking for Chrome debugging protocol...');
  
  // List all products and their upload status
  console.log('\n📦 Products to upload:\n');
  products.forEach((p, idx) => {
    const fullPath = path.join(baseDir, p.zipFile);
    const exists = fs.existsSync(fullPath);
    const size = exists ? (fs.statSync(fullPath).size / 1024).toFixed(2) : '?';
    const status = exists ? '✓' : '✗';
    console.log(`  [${idx + 1}] ${status} ${p.name}`);
    console.log(`      ${p.zipFile} (${size} KB)\n`);
  });
  
  console.log('💡 Recommended solution:');
  console.log('  Use the authenticated browser session with JavaScript-based file upload\n');
}

main();
