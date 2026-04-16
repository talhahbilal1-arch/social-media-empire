# Spreadsheet Specification: Fillable Macro Tracker

This document specifies the Google Sheet / Excel template that accompanies the Meal Planner PDF. The user fills in their stats once, and the sheet calculates macros, generates a weekly template, and tracks daily adherence.

## Sheet 1: Setup (User Input)

| Cell | Label | Input Type | Validation |
|------|-------|------------|------------|
| B2 | Name | Text | Optional |
| B3 | Age | Number | 18-99 |
| B4 | Weight (lbs) | Number | 80-400 |
| B5 | Height (inches) | Number | 48-84 |
| B6 | Activity Level | Dropdown | Sedentary / Lightly Active / Moderately Active / Very Active |
| B7 | Goal | Dropdown | Fat Loss / Maintenance / Muscle Gain |
| B8 | Protein per lb | Number | Default 1.0, range 0.7-1.2 |
| B9 | Fat per lb | Number | Default 0.4, range 0.3-0.5 |

## Sheet 1: Calculated Output (Auto-Filled)

| Cell | Label | Formula |
|------|-------|---------|
| D3 | BMR | =(10 * B4/2.205) + (6.25 * B5*2.54) - (5 * B3) + 5 |
| D4 | TDEE | =D3 * VLOOKUP(B6, multiplier_table, 2) |
| D5 | Target Calories | =IF(B7="Fat Loss", D4-400, IF(B7="Muscle Gain", D4+300, D4)) |
| D6 | Protein (g) | =B4 * B8 |
| D7 | Protein (cal) | =D6 * 4 |
| D8 | Fat (g) | =B4 * B9 |
| D9 | Fat (cal) | =D8 * 9 |
| D10 | Carbs (cal) | =D5 - D7 - D9 |
| D11 | Carbs (g) | =D10 / 4 |

**Multiplier table (hidden range):**

| Activity Level | Multiplier |
|---|---|
| Sedentary | 1.2 |
| Lightly Active | 1.375 |
| Moderately Active | 1.55 |
| Very Active | 1.725 |

## Sheet 2: Weekly Planner

7-day grid matching the template rotation format from Chapter 6.

| Column | Content |
|--------|---------|
| A | Day (Mon-Sun) |
| B | Breakfast Template (dropdown from template list) |
| C | Lunch Template |
| D | Dinner Template |
| E | Snack Template |
| F | Estimated Protein (auto-calc from template macros) |
| G | Estimated Carbs |
| H | Estimated Fat |
| I | Estimated Calories |
| J | Delta vs Target (=I - target_calories, conditional format: green if within 100, yellow if within 200, red if over 200) |

## Sheet 3: Daily Tracker (12 Weeks)

84 rows (one per day), columns:

| Column | Content | Type |
|--------|---------|------|
| A | Date | Auto-filled from start date |
| B | Day of Week | =TEXT(A,"ddd") |
| C | Weight (morning) | User input |
| D | Protein (g) | User input |
| E | Carbs (g) | User input |
| F | Fat (g) | User input |
| G | Total Calories | =(D*4)+(E*4)+(F*9) |
| H | Protein Target Hit? | =IF(D>=target_protein, "Y", "N") |
| I | Calorie Delta | =G - target_calories |
| J | Steps | User input |
| K | Sleep (hours) | User input |
| L | Training? | Dropdown: Rest / Train |
| M | Notes | Free text |

## Sheet 4: Progress Dashboard

Charts (auto-generated from Sheet 3 data):

1. **Weight trend line** — 7-day rolling average, not raw daily weights
2. **Weekly average calories vs. target** — bar chart, 12 bars
3. **Protein adherence** — percentage of days hitting target, displayed as a single large number
4. **Steps trend** — daily with 7-day average overlay

## Conditional Formatting Rules

- Weight column: no formatting (daily fluctuations are normal, coloring them causes anxiety)
- Protein column: green background if >= target, red if < target - 20g
- Calorie delta: green if -200 to +200, yellow if -400 to -200 or +200 to +400, red if outside
- Sleep: green if >= 7, yellow if 6 to 7, red if < 6

## Build Notes

To create the actual .xlsx from this spec:

```python
# Use openpyxl
pip install openpyxl
python3 products/macro-meal-planner/build_spreadsheet.py
```

The build script is a future task. This spec is the reference for that script.

---
