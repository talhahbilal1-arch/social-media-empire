const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

// Product IDs and ZIP file mappings
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

// Base directory
const baseDir = '/Users/homefolder/Desktop/social-media-empire';

async function uploadToProduct(page, product) {
  console.log(`\n[${new Date().toLocaleTimeString()}] Processing: ${product.name}`);
  
  try {
    const url = `https://gumroad.com/products/${product.productId}/edit/content`;
    console.log(`  → Navigating to: ${url}`);
    
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 15000 });
    
    // Wait for the file input to be present
    await page.waitForSelector('input[name="file"]', { timeout: 5000 });
    console.log('  ✓ File input found');
    
    // Get the full path to the ZIP file
    const fullPath = path.join(baseDir, product.zipFile);
    
    if (!fs.existsSync(fullPath)) {
      console.log(`  ✗ ZIP file not found: ${fullPath}`);
      return false;
    }
    
    const fileSize = (fs.statSync(fullPath).size / 1024).toFixed(2);
    console.log(`  → Uploading: ${product.zipFile} (${fileSize} KB)`);
    
    // Upload the file using the hidden file input
    const fileInput = await page.$('input[name="file"]');
    await fileInput.uploadFile(fullPath);
    
    console.log('  ✓ File selected in input');
    
    // Wait for the upload to initiate (look for progress or success indicators)
    await page.waitForTimeout(2000);
    
    // Check if there's a save button that needs to be clicked
    const saveButton = await page.$('button:has-text("Save"), button:contains("Save")');
    if (saveButton) {
      console.log('  → Clicking Save button');
      await saveButton.click();
      await page.waitForTimeout(2000);
    }
    
    // Wait for any upload feedback
    await page.waitForTimeout(3000);
    
    console.log(`  ✓ Upload initiated for ${product.name}`);
    return true;
    
  } catch (error) {
    console.log(`  ✗ Error: ${error.message}`);
    return false;
  }
}

async function main() {
  let browser;
  const results = { success: 0, failed: 0, errors: [] };
  
  try {
    console.log('🚀 Launching Puppeteer browser...');
    browser = await puppeteer.launch({
      headless: false,  // Show the browser so you can see progress
      args: ['--start-maximized', '--disable-blink-features=AutomationControlled'],
    });
    
    const page = await browser.newPage();
    
    // Set a custom user agent to avoid detection
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36');
    
    // Process each product
    for (let i = 0; i < products.length; i++) {
      const product = products[i];
      const success = await uploadToProduct(page, product);
      
      if (success) {
        results.success++;
      } else {
        results.failed++;
        results.errors.push(product.name);
      }
      
      // Delay between uploads to avoid rate limiting
      if (i < products.length - 1) {
        console.log(`  ⏳ Waiting 5 seconds before next product...`);
        await page.waitForTimeout(5000);
      }
    }
    
    // Print summary
    console.log('\n' + '='.repeat(60));
    console.log(`📊 Upload Summary:`);
    console.log(`   ✓ Successful: ${results.success}/${products.length}`);
    console.log(`   ✗ Failed: ${results.failed}/${products.length}`);
    
    if (results.errors.length > 0) {
      console.log(`\n   Failed products:`);
      results.errors.forEach(name => console.log(`     - ${name}`));
    }
    console.log('='.repeat(60));
    
  } catch (error) {
    console.error('Fatal error:', error);
  } finally {
    if (browser) {
      console.log('\n🛑 Closing browser...');
      await browser.close();
    }
  }
}

main();
