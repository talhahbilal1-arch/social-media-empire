# 90-Day Macro Meal Planner

The $17 order bump companion to the FitOver35 Body Recomposition Blueprint ($97).

## Chapter Index

| File | Chapter | Words | Status |
|------|---------|-------|--------|
| `content/00-introduction.md` | Introduction | 533 | Done |
| `content/01-how-the-planner-works.md` | How the Planner Works | 663 | Done |
| `content/02-breakfast-templates.md` | Breakfast Templates | 739 | Done |
| `content/03-lunch-templates.md` | Lunch Templates | 838 | Done |
| `content/04-dinner-templates.md` | Dinner Templates | 893 | Done |
| `content/05-snacks-and-liquid-calories.md` | Snacks and Liquid Calories | 768 | Done |
| `content/06-grocery-list-generator.md` | Grocery List Generator | ~650 | Done |
| `content/07-meal-prep-sunday-workflow.md` | Meal Prep: Sunday Workflow | ~750 | Done |
| `content/08-eating-out-survival.md` | Eating Out: Survival Guide | ~900 | Done |
| `content/09-the-cheat-meal-rules.md` | The Cheat Meal Rules | ~700 | Done |
| `content/10-spreadsheet-spec.md` | Spreadsheet Specification | ~500 | Done |
| `MANIFEST.md` | Product Positioning | 556 | Done |
| `gumroad-description.md` | Gumroad Listing Copy | ~350 | Done |

## Build Instructions

```bash
cd products/macro-meal-planner/
pandoc content/00-introduction.md content/01-how-the-planner-works.md \
  content/02-breakfast-templates.md content/03-lunch-templates.md \
  content/04-dinner-templates.md content/05-snacks-and-liquid-calories.md \
  content/06-grocery-list-generator.md content/07-meal-prep-sunday-workflow.md \
  content/08-eating-out-survival.md content/09-the-cheat-meal-rules.md \
  -o macro-meal-planner.pdf \
  --pdf-engine=xelatex -V geometry:margin=1in -V fontsize=11pt
```

## Launch Steps

1. Render PDF from markdown chapters
2. Create Gumroad product, paste `gumroad-description.md`
3. Upload PDF via `automation/playwright/gumroad-zip-uploader.js`
4. Set as order bump on the $97 Blueprint product
5. Add to fitover35.com/products/ index page
