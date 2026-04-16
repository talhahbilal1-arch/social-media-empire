# FitOver35 Body Recomposition Blueprint

The $97 signature product for the FitOver35 brand. A complete 12-week body recomposition system for men aged 35 to 55.

## Chapter Index

| File | Chapter | Target Words | Status |
|------|---------|-------------|--------|
| `00-cover.md` | Cover Page | 30 | Done |
| `01-introduction.md` | Introduction | 400-600 | Done |
| `02-why-over-35-is-different.md` | Why Over 35 Is Different | 800-1000 | Done |
| `03-the-5-pillars.md` | The 5 Pillars | 500 | Done |
| `04-training-the-12-week-program.md` | Training: The 12-Week Program | 1800-2400 | Done |
| `05-nutrition-macros-and-meal-structure.md` | Nutrition: Macros and Meal Structure | 1200-1600 | Done |
| `06-recovery-sleep-and-stress.md` | Recovery: Sleep and Stress | 900-1200 | Done |
| `07-mobility-and-joint-protection.md` | Mobility and Joint Protection | 800-1100 | Done |
| `08-supplement-decision-tree.md` | Supplement Decision Tree | 700-900 | Done |
| `09-measuring-progress.md` | Measuring Progress | 600-800 | Done |
| `10-common-mistakes-and-troubleshooting.md` | Common Mistakes and Troubleshooting | 800-1000 | Done |
| `11-the-macro-calculator.md` | The Macro Calculator (Worked Example) | 300-400 | Done |
| `12-90-day-quick-start.md` | The 90-Day Quick Start | 600-800 | Done |
| `13-resources-and-next-steps.md` | Resources and Next Steps | 400-600 | Done |

## Total Word Count

Target: 12,000 to 15,000 words across all chapters.

## Build Instructions

To render all chapters into a single PDF:

```bash
# Using Pandoc (recommended)
cd products/signature/blueprint-pdf/
pandoc 00-cover.md 01-introduction.md 02-why-over-35-is-different.md \
  03-the-5-pillars.md 04-training-the-12-week-program.md \
  05-nutrition-macros-and-meal-structure.md 06-recovery-sleep-and-stress.md \
  07-mobility-and-joint-protection.md 08-supplement-decision-tree.md \
  09-measuring-progress.md 10-common-mistakes-and-troubleshooting.md \
  11-the-macro-calculator.md 12-90-day-quick-start.md \
  13-resources-and-next-steps.md \
  -o fitover35-body-recomposition-blueprint.pdf \
  --pdf-engine=xelatex \
  -V geometry:margin=1in \
  -V fontsize=11pt

# Using WeasyPrint (alternative)
pandoc *.md -t html -o blueprint.html
weasyprint blueprint.html fitover35-body-recomposition-blueprint.pdf
```

## Post-Build Checklist

1. Review all chapters for accuracy
2. Add custom PDF cover page design (Canva or Figma)
3. Upload to Gumroad via `automation/playwright/gumroad-zip-uploader.js`
4. Seed Pinterest pins via `products/signature/pinterest/seed_pins.py`
5. Launch email sequence via Kit (see `email_marketing/blueprint_launch/`)
