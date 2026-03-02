/**
 * Gumroad Product Autofill Script
 * Run in Chrome DevTools console when on https://app.gumroad.com/products/new
 * Call: fillProduct(1), fillProduct(2), fillProduct(3), or fillProduct(4)
 */

const PRODUCTS = {
  1: {
    name: "AI Fitness Coach Vault \u2014 Men Over 35 Edition",
    price: "27",
    summary: "75 copy-paste ChatGPT prompts written by an ISSA CPT for men over 35. Workout programming, nutrition, fat loss, hormone health + 5 complete training programs and a word-for-word discovery call script.",
  },
  2: {
    name: "Pinterest Automation Blueprint \u2014 Post 15 Pins/Day on Autopilot (Real System, Not Theory)",
    price: "47",
    summary: "The exact Make.com + Claude + GitHub Actions system that posts 15 Pinterest pins/day across 3 brands automatically. Real prompts, real workflow files, real setup guide. Running live since 2025.",
  },
  3: {
    name: "Online Coach AI Client Machine \u2014 50 Prompts + Scripts to Get Clients Without the Grind",
    price: "17",
    summary: "50 copy-paste AI prompts for online coaches: DM replies, proposals, Instagram captions, email sequences, onboarding, testimonials, and client retention. Plus word-for-word scripts for the conversations coaches dread.",
  },
  4: {
    name: "FREE: 5 AI Prompts That Save Fitness Coaches 5 Hours a Week",
    price: "0",
    summary: "5 copy-paste prompts for fitness coaches: DM replies, content planning, program design, client check-ins, and Pinterest pin titles. Taken from the full AI Fitness Coach Vault (75 prompts).",
  },
};

function setField(element, value) {
  const proto = element.tagName === 'TEXTAREA'
    ? window.HTMLTextAreaElement.prototype
    : window.HTMLInputElement.prototype;
  const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
  setter.call(element, value);
  element.dispatchEvent(new Event('input', { bubbles: true }));
  element.dispatchEvent(new Event('change', { bubbles: true }));
}

function fillProduct(num) {
  const p = PRODUCTS[num];
  if (!p) { console.error('No product:', num); return; }
  console.log('Filling:', p.name);

  const name = document.querySelector('input[name="name"]') ||
    document.querySelector('input[placeholder*="Name" i]');
  if (name) { setField(name, p.name); console.log('\u2713 Name'); }

  const price = document.querySelector('input[name="price"]') ||
    document.querySelector('input[type="number"]');
  if (price) { setField(price, p.price); console.log('\u2713 Price'); }

  const summary = document.querySelector('textarea[name="summary"]') ||
    document.querySelector('textarea[placeholder*="summary" i]');
  if (summary) { setField(summary, p.summary); console.log('\u2713 Summary'); }

  console.log('\nFilled! Full description is in prompt-packs/marketing/gumroad-listings.md');
  console.log('Copy the description from that file into the rich text editor.');
}

console.log('Autofill loaded. Run fillProduct(1..4)');
