---
phase: 07-cli-interface
plan: 01
subsystem: cli
tags:
  - argparse
  - cli
  - progress-display
  - batch-generation

dependency-graph:
  requires:
    - 06-01 (VideoGenerator.generate_batch, generate_for_brands)
  provides:
    - cli.py (command-line interface for video generation)
    - tests/test_cli.py (comprehensive CLI tests)
  affects:
    - 08-automation (GitHub Actions will invoke CLI)

tech-stack:
  added: []
  patterns:
    - argparse-based CLI with subcommand pattern
    - Mock-based testing for API-dependent code

key-files:
  created:
    - cli.py
    - tests/test_cli.py
  modified: []

decisions:
  - id: "exit-code-convention"
    choice: "0 for all success, 1 for any failure"
    rationale: "Standard Unix convention, easy CI/CD integration"
  - id: "summary-table-format"
    choice: "Fixed-width columns with pipe separators"
    rationale: "Consistent alignment, readable in terminal output"
  - id: "brand-all-expansion"
    choice: "list_brands() at runtime"
    rationale: "Dynamic discovery of brands, no hardcoded list"

metrics:
  duration: 3.5 min
  completed: 2026-01-24
---

# Phase 7 Plan 01: CLI Interface Summary

**One-liner:** argparse-based CLI with --brand/--count/--no-upload, progress display, and aligned summary table

## What Was Built

### cli.py (248 lines)
Command-line interface for video generation with:

1. **Argument parsing (argparse)**
   - `--brand` (required): Brand slug or "all" for all brands
   - `--count` (optional, default=1): Videos per brand
   - `--no-upload` (optional flag): Skip Supabase upload

2. **Brand resolution**
   - "all" expands to all brands via `list_brands()`
   - Single brand validated by attempting load
   - Helpful error messages with available brands

3. **Progress display**
   - Brand header: `[Brand: menopause-planner] Generating N video(s)...`
   - Per-video status: `Video N/M: SUCCESS` or `Video N/M: FAILED - {error}`

4. **Summary table**
   - Fixed-width columns with aligned separators
   - Per-brand success/failed/total counts
   - TOTAL row summing all brands
   - Elapsed time in seconds

5. **Exit codes**
   - 0: All videos generated successfully
   - 1: One or more videos failed

### tests/test_cli.py (445 lines)
Comprehensive test coverage with 23 tests:

- **TestParseArgs** (7 tests): Argument validation
- **TestResolveBrands** (5 tests): Brand resolution logic
- **TestExitCodes** (3 tests): Success/failure exit codes
- **TestSummaryTable** (3 tests): Formatting and alignment
- **TestProgressOutput** (3 tests): Progress messages
- **TestMultiBrandGeneration** (2 tests): All-brands processing

## API Integration

```python
# From cli.py
from src.orchestration import VideoGenerator
from src.orchestration.video_generator import BatchResult
from src.utils.brand_loader import BrandLoader, list_brands

# Single brand generation
generator = VideoGenerator()
batch_result = generator.generate_batch(brand_config, count=args.count, upload=not args.no_upload)

# Multi-brand via loop (not generate_for_brands to enable per-video progress)
for brand_slug in brand_slugs:
    brand_config = loader.load(brand_slug)
    batch_result = generator.generate_batch(brand_config, ...)
```

## Example Output

```
[Brand: menopause-planner] Generating 2 video(s)...
  Video 1/2: SUCCESS
  Video 2/2: SUCCESS
[Brand: daily-deal-darling] Generating 2 video(s)...
  Video 1/2: SUCCESS
  Video 2/2: FAILED - API rate limit exceeded

================================================================================
GENERATION SUMMARY
================================================================================
Brand                    | Success | Failed | Total
-------------------------+---------+--------+------
menopause-planner        |       2 |      0 |     2
daily-deal-darling       |       1 |      1 |     2
-------------------------+---------+--------+------
TOTAL                    |       3 |      1 |     4
================================================================================
Total time: 45.3s
```

## Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Exit code convention | 0=success, 1=failure | Standard Unix, easy CI/CD integration |
| Summary table format | Fixed-width columns with pipes | Consistent alignment in terminal |
| Brand "all" expansion | Runtime list_brands() call | Dynamic discovery, no hardcoding |
| Progress per-video | Loop with generate_batch per brand | Enables immediate feedback vs batched |

## Deviations from Plan

None - plan executed exactly as written.

## Commits

| Commit | Type | Description |
|--------|------|-------------|
| 5ef2cc2 | feat | Create CLI with argument parsing and brand resolution |
| dfb1b65 | test | Add CLI integration tests with full mock coverage |

## Test Results

```
tests/test_cli.py::TestParseArgs::test_required_brand_argument PASSED
tests/test_cli.py::TestParseArgs::test_brand_argument PASSED
tests/test_cli.py::TestParseArgs::test_brand_all PASSED
tests/test_cli.py::TestParseArgs::test_count_default PASSED
tests/test_cli.py::TestParseArgs::test_count_custom PASSED
tests/test_cli.py::TestParseArgs::test_count_invalid PASSED
tests/test_cli.py::TestParseArgs::test_no_upload_flag PASSED
tests/test_cli.py::TestResolveBrands::test_resolve_all_brands PASSED
tests/test_cli.py::TestResolveBrands::test_resolve_all_case_insensitive PASSED
tests/test_cli.py::TestResolveBrands::test_resolve_all_no_brands PASSED
tests/test_cli.py::TestResolveBrands::test_resolve_valid_brand PASSED
tests/test_cli.py::TestResolveBrands::test_resolve_invalid_brand PASSED
tests/test_cli.py::TestExitCodes::test_exit_code_zero_on_success PASSED
tests/test_cli.py::TestExitCodes::test_exit_code_one_on_failure PASSED
tests/test_cli.py::TestExitCodes::test_exit_code_one_all_failures PASSED
tests/test_cli.py::TestSummaryTable::test_summary_table_format PASSED
tests/test_cli.py::TestSummaryTable::test_summary_table_alignment PASSED
tests/test_cli.py::TestSummaryTable::test_summary_totals_calculation PASSED
tests/test_cli.py::TestProgressOutput::test_progress_shows_brand_header PASSED
tests/test_cli.py::TestProgressOutput::test_progress_shows_success PASSED
tests/test_cli.py::TestProgressOutput::test_progress_shows_failure_with_error PASSED
tests/test_cli.py::TestMultiBrandGeneration::test_all_brands_processed PASSED
tests/test_cli.py::TestMultiBrandGeneration::test_multiple_videos_per_brand PASSED

========================= 23 passed in 1.01s =========================
```

## Next Phase Readiness

Phase 8 (Automation) can now:
- Invoke `python cli.py --brand all --count N` from GitHub Actions
- Check exit code for CI pass/fail
- Parse summary table output for logging

No blockers for Phase 8.
