"""Tests for CLI module.

This module tests the command-line interface for video generation,
including argument parsing, brand resolution, exit codes, and
summary table formatting.
"""

import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cli import main, parse_args, resolve_brands, print_summary
from src.orchestration.video_generator import BatchResult, GenerationResult


class TestParseArgs:
    """Tests for argument parsing."""

    def test_required_brand_argument(self):
        """--brand is required."""
        with pytest.raises(SystemExit) as exc_info:
            parse_args([])
        assert exc_info.value.code == 2  # argparse error code

    def test_brand_argument(self):
        """--brand accepts a brand slug."""
        args = parse_args(["--brand", "menopause-planner"])
        assert args.brand == "menopause-planner"

    def test_brand_all(self):
        """--brand accepts 'all' for all brands."""
        args = parse_args(["--brand", "all"])
        assert args.brand == "all"

    def test_count_default(self):
        """--count defaults to 1."""
        args = parse_args(["--brand", "test"])
        assert args.count == 1

    def test_count_custom(self):
        """--count accepts custom value."""
        args = parse_args(["--brand", "test", "--count", "5"])
        assert args.count == 5

    def test_count_invalid(self):
        """--count rejects non-integer values."""
        with pytest.raises(SystemExit):
            parse_args(["--brand", "test", "--count", "abc"])

    def test_no_upload_flag(self):
        """--no-upload is a boolean flag."""
        args = parse_args(["--brand", "test"])
        assert args.no_upload is False

        args = parse_args(["--brand", "test", "--no-upload"])
        assert args.no_upload is True


class TestResolveBrands:
    """Tests for brand resolution logic."""

    @patch("cli.list_brands")
    def test_resolve_all_brands(self, mock_list_brands):
        """'all' resolves to all brand slugs."""
        mock_list_brands.return_value = [
            "daily-deal-darling",
            "fitness-made-easy",
            "menopause-planner",
        ]

        result = resolve_brands("all")
        assert result == [
            "daily-deal-darling",
            "fitness-made-easy",
            "menopause-planner",
        ]

    @patch("cli.list_brands")
    def test_resolve_all_case_insensitive(self, mock_list_brands):
        """'ALL' and 'All' also work."""
        mock_list_brands.return_value = ["brand1", "brand2"]

        result = resolve_brands("ALL")
        assert result == ["brand1", "brand2"]

        result = resolve_brands("All")
        assert result == ["brand1", "brand2"]

    @patch("cli.list_brands")
    def test_resolve_all_no_brands(self, mock_list_brands):
        """Exits with error when no brands found."""
        mock_list_brands.return_value = []

        with pytest.raises(SystemExit) as exc_info:
            resolve_brands("all")
        assert exc_info.value.code == 1

    @patch("cli.BrandLoader")
    def test_resolve_valid_brand(self, mock_loader_class):
        """Valid brand slug is returned as single-item list."""
        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader

        result = resolve_brands("menopause-planner")
        assert result == ["menopause-planner"]
        mock_loader.load.assert_called_once_with("menopause-planner")

    @patch("cli.BrandLoader")
    def test_resolve_invalid_brand(self, mock_loader_class):
        """Invalid brand exits with error."""
        mock_loader = MagicMock()
        mock_loader.load.side_effect = FileNotFoundError("Brand 'invalid' not found.")
        mock_loader_class.return_value = mock_loader

        with pytest.raises(SystemExit) as exc_info:
            resolve_brands("invalid")
        assert exc_info.value.code == 1


class TestExitCodes:
    """Tests for exit code logic."""

    @patch("cli.resolve_brands")
    @patch("cli.VideoGenerator")
    @patch("cli.BrandLoader")
    def test_exit_code_zero_on_success(self, mock_loader_class, mock_generator_class, mock_resolve):
        """Exit code 0 when all videos succeed."""
        mock_resolve.return_value = ["brand1"]

        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader

        # Create success result
        mock_batch = BatchResult(
            results=[GenerationResult(success=True)],
            total_duration_ms=1000,
        )
        mock_generator = MagicMock()
        mock_generator.generate_batch.return_value = mock_batch
        mock_generator_class.return_value = mock_generator

        exit_code = main(["--brand", "brand1", "--count", "1", "--no-upload"])
        assert exit_code == 0

    @patch("cli.resolve_brands")
    @patch("cli.VideoGenerator")
    @patch("cli.BrandLoader")
    def test_exit_code_one_on_failure(self, mock_loader_class, mock_generator_class, mock_resolve):
        """Exit code 1 when any video fails."""
        mock_resolve.return_value = ["brand1"]

        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader

        # Create mixed result with one failure
        mock_batch = BatchResult(
            results=[
                GenerationResult(success=True),
                GenerationResult(success=False, error="Test error"),
            ],
            total_duration_ms=2000,
        )
        mock_generator = MagicMock()
        mock_generator.generate_batch.return_value = mock_batch
        mock_generator_class.return_value = mock_generator

        exit_code = main(["--brand", "brand1", "--count", "2", "--no-upload"])
        assert exit_code == 1

    @patch("cli.resolve_brands")
    @patch("cli.VideoGenerator")
    @patch("cli.BrandLoader")
    def test_exit_code_one_all_failures(self, mock_loader_class, mock_generator_class, mock_resolve):
        """Exit code 1 when all videos fail."""
        mock_resolve.return_value = ["brand1"]

        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader

        # Create all failures
        mock_batch = BatchResult(
            results=[
                GenerationResult(success=False, error="Error 1"),
                GenerationResult(success=False, error="Error 2"),
            ],
            total_duration_ms=500,
        )
        mock_generator = MagicMock()
        mock_generator.generate_batch.return_value = mock_batch
        mock_generator_class.return_value = mock_generator

        exit_code = main(["--brand", "brand1", "--count", "2", "--no-upload"])
        assert exit_code == 1


class TestSummaryTable:
    """Tests for summary table formatting."""

    def test_summary_table_format(self, capsys):
        """Summary table has correct format and alignment."""
        results = {
            "menopause-planner": BatchResult(
                results=[GenerationResult(success=True)],
                total_duration_ms=1000,
            ),
            "daily-deal-darling": BatchResult(
                results=[
                    GenerationResult(success=True),
                    GenerationResult(success=False, error="Error"),
                ],
                total_duration_ms=2000,
            ),
        }

        print_summary(results, 3.5)
        captured = capsys.readouterr()

        # Check header
        assert "GENERATION SUMMARY" in captured.out
        assert "=" * 80 in captured.out

        # Check column headers
        assert "Brand" in captured.out
        assert "Success" in captured.out
        assert "Failed" in captured.out
        assert "Total" in captured.out

        # Check brands are present
        assert "menopause-planner" in captured.out
        assert "daily-deal-darling" in captured.out

        # Check totals row
        assert "TOTAL" in captured.out

        # Check duration
        assert "Total time: 3.5s" in captured.out

    def test_summary_table_alignment(self, capsys):
        """Summary table columns are properly aligned."""
        results = {
            "brand1": BatchResult(
                results=[GenerationResult(success=True)],
                total_duration_ms=100,
            ),
        }

        print_summary(results, 1.0)
        captured = capsys.readouterr()
        lines = captured.out.split("\n")

        # Find the header line and data line
        header_line = None
        data_line = None
        for line in lines:
            if "Brand" in line and "Success" in line:
                header_line = line
            if "brand1" in line:
                data_line = line

        assert header_line is not None
        assert data_line is not None

        # Verify pipe separators align
        header_pipes = [i for i, c in enumerate(header_line) if c == "|"]
        data_pipes = [i for i, c in enumerate(data_line) if c == "|"]
        assert header_pipes == data_pipes

    def test_summary_totals_calculation(self, capsys):
        """TOTAL row correctly sums all brands."""
        results = {
            "brand1": BatchResult(
                results=[
                    GenerationResult(success=True),
                    GenerationResult(success=True),
                ],
                total_duration_ms=1000,
            ),
            "brand2": BatchResult(
                results=[
                    GenerationResult(success=True),
                    GenerationResult(success=False, error="Error"),
                    GenerationResult(success=False, error="Error"),
                ],
                total_duration_ms=2000,
            ),
        }

        print_summary(results, 5.0)
        captured = capsys.readouterr()

        # Find TOTAL line
        lines = captured.out.split("\n")
        total_line = None
        for line in lines:
            if "TOTAL" in line:
                total_line = line
                break

        assert total_line is not None
        # Should have 3 success (2+1), 2 failed (0+2), 5 total (2+3)
        # The numbers should appear in the TOTAL line
        assert "3" in total_line  # success count
        assert "2" in total_line  # failed count
        assert "5" in total_line  # total count


class TestProgressOutput:
    """Tests for progress output during generation."""

    @patch("cli.resolve_brands")
    @patch("cli.VideoGenerator")
    @patch("cli.BrandLoader")
    def test_progress_shows_brand_header(self, mock_loader_class, mock_generator_class, mock_resolve, capsys):
        """Progress output shows brand header."""
        mock_resolve.return_value = ["menopause-planner"]

        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader

        mock_batch = BatchResult(
            results=[GenerationResult(success=True)],
            total_duration_ms=1000,
        )
        mock_generator = MagicMock()
        mock_generator.generate_batch.return_value = mock_batch
        mock_generator_class.return_value = mock_generator

        main(["--brand", "menopause-planner", "--count", "1", "--no-upload"])
        captured = capsys.readouterr()

        assert "[Brand: menopause-planner]" in captured.out
        assert "Generating 1 video(s)..." in captured.out

    @patch("cli.resolve_brands")
    @patch("cli.VideoGenerator")
    @patch("cli.BrandLoader")
    def test_progress_shows_success(self, mock_loader_class, mock_generator_class, mock_resolve, capsys):
        """Progress output shows SUCCESS for successful videos."""
        mock_resolve.return_value = ["brand1"]

        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader

        mock_batch = BatchResult(
            results=[GenerationResult(success=True)],
            total_duration_ms=1000,
        )
        mock_generator = MagicMock()
        mock_generator.generate_batch.return_value = mock_batch
        mock_generator_class.return_value = mock_generator

        main(["--brand", "brand1", "--count", "1", "--no-upload"])
        captured = capsys.readouterr()

        assert "Video 1/1: SUCCESS" in captured.out

    @patch("cli.resolve_brands")
    @patch("cli.VideoGenerator")
    @patch("cli.BrandLoader")
    def test_progress_shows_failure_with_error(self, mock_loader_class, mock_generator_class, mock_resolve, capsys):
        """Progress output shows FAILED with error message."""
        mock_resolve.return_value = ["brand1"]

        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader

        mock_batch = BatchResult(
            results=[
                GenerationResult(success=False, error="API rate limit exceeded"),
            ],
            total_duration_ms=500,
        )
        mock_generator = MagicMock()
        mock_generator.generate_batch.return_value = mock_batch
        mock_generator_class.return_value = mock_generator

        main(["--brand", "brand1", "--count", "1", "--no-upload"])
        captured = capsys.readouterr()

        assert "Video 1/1: FAILED - API rate limit exceeded" in captured.out


class TestMultiBrandGeneration:
    """Tests for generating videos for multiple brands."""

    @patch("cli.resolve_brands")
    @patch("cli.VideoGenerator")
    @patch("cli.BrandLoader")
    def test_all_brands_processed(self, mock_loader_class, mock_generator_class, mock_resolve, capsys):
        """All brands are processed when using --brand all."""
        mock_resolve.return_value = ["brand1", "brand2", "brand3"]

        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader

        mock_batch = BatchResult(
            results=[GenerationResult(success=True)],
            total_duration_ms=1000,
        )
        mock_generator = MagicMock()
        mock_generator.generate_batch.return_value = mock_batch
        mock_generator_class.return_value = mock_generator

        main(["--brand", "all", "--count", "1", "--no-upload"])
        captured = capsys.readouterr()

        # All brands should appear in output
        assert "[Brand: brand1]" in captured.out
        assert "[Brand: brand2]" in captured.out
        assert "[Brand: brand3]" in captured.out

        # generator.generate_batch should be called 3 times
        assert mock_generator.generate_batch.call_count == 3

    @patch("cli.resolve_brands")
    @patch("cli.VideoGenerator")
    @patch("cli.BrandLoader")
    def test_multiple_videos_per_brand(self, mock_loader_class, mock_generator_class, mock_resolve, capsys):
        """Count parameter generates multiple videos per brand."""
        mock_resolve.return_value = ["brand1"]

        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader

        mock_batch = BatchResult(
            results=[
                GenerationResult(success=True),
                GenerationResult(success=True),
                GenerationResult(success=True),
            ],
            total_duration_ms=3000,
        )
        mock_generator = MagicMock()
        mock_generator.generate_batch.return_value = mock_batch
        mock_generator_class.return_value = mock_generator

        main(["--brand", "brand1", "--count", "3", "--no-upload"])
        captured = capsys.readouterr()

        assert "Video 1/3: SUCCESS" in captured.out
        assert "Video 2/3: SUCCESS" in captured.out
        assert "Video 3/3: SUCCESS" in captured.out
