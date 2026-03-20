const fs = require('fs');
const path = require('path');
const https = require('https');

// Gumroad product IDs and their corresponding ZIP files
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

// Check which files exist
console.log('Checking file availability:\n');
products.forEach(p => {
  const fullPath = path.join('/Users/homefolder/Desktop/social-media-empire', p.zipFile);
  const exists = fs.existsSync(fullPath);
  const size = exists ? fs.statSync(fullPath).size : 0;
  console.log(`${exists ? '✓' : '✗'} ${p.name}`);
  console.log(`  File: ${p.zipFile}`);
  console.log(`  Size: ${exists ? (size / 1024).toFixed(2) + ' KB' : 'NOT FOUND'}\n`);
});

// Test fetching Gumroad product page to get upload endpoint
console.log('\n--- Testing Gumroad Upload Endpoint ---\n');
console.log('Need to use Gumroad\'s actual upload mechanism.');
console.log('Options:');
console.log('1. Use Puppeteer with uploadFile() to populate hidden file input');
console.log('2. Reverse-engineer the upload endpoint via network inspection');
console.log('3. Check if Gumroad has undocumented API for file uploads');
console.log('4. Use Dropbox integration instead of direct upload');
