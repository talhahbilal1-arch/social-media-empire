const puppeteer = require('puppeteer');

async function debugPage() {
  let browser;
  
  try {
    console.log('🚀 Launching Puppeteer...');
    browser = await puppeteer.launch({
      headless: true,
      args: ['--disable-blink-features=AutomationControlled'],
    });
    
    const page = await browser.newPage();
    const url = 'https://gumroad.com/products/vgpbuk/edit/content';
    
    console.log(`📄 Loading: ${url}`);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    
    // Wait a bit for dynamic content
    await new Promise(r => setTimeout(r, 3000));
    
    // Check page title
    const title = await page.title();
    console.log(`📋 Page title: ${title}`);
    
    // Find all input elements
    const inputs = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('input')).map(i => ({
        type: i.type,
        name: i.name,
        id: i.id,
        className: i.className,
        visible: i.offsetHeight > 0
      }));
    });
    
    console.log(`🔍 Found ${inputs.length} input elements:`);
    inputs.forEach((inp, idx) => {
      console.log(`  [${idx}] type="${inp.type}" name="${inp.name}" class="${inp.className}" visible=${inp.visible}`);
    });
    
    // Look for file upload button or mechanism
    const buttons = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('button')).map(b => ({
        text: b.innerText.substring(0, 30),
        className: b.className
      }));
    });
    
    console.log(`🔘 Found ${buttons.length} buttons:`);
    buttons.slice(0, 10).forEach((btn, idx) => {
      console.log(`  [${idx}] "${btn.text}"`);
    });
    
    // Check page content
    const pageContent = await page.evaluate(() => document.body.innerText.substring(0, 500));
    console.log(`\n📝 Page content preview:\n${pageContent}...`);
    
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

debugPage();
