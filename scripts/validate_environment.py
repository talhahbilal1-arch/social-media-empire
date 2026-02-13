#!/usr/bin/env python3
"""
Environment Validation Script for Social Media Empire

Validates that the development environment is properly configured:
- Python 3.11.x
- Required dependencies (moviepy, PIL, numpy, imageio)
- FFmpeg with libx264 codec
- MoviePy TextClip functionality with Pillow

Exit codes:
    0: All checks passed
    1: One or more checks failed
"""

import sys
import subprocess
import importlib.util
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(message):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def print_check(name, passed, details=""):
    """Print a check result with color coding"""
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"{status} - {name}")
    if details:
        print(f"       {details}")


def check_python_version():
    """Verify Python 3.11.x is installed"""
    version = sys.version_info
    is_valid = version.major == 3 and version.minor == 11
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print_check(
        "Python Version Check",
        is_valid,
        f"Found: Python {version_str} (Required: 3.11.x)"
    )

    return is_valid


def check_dependency(module_name, import_name=None):
    """Check if a Python module can be imported"""
    if import_name is None:
        import_name = module_name

    try:
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            print_check(f"Dependency: {module_name}", False, f"Module '{import_name}' not found")
            return False

        # Try actual import to catch import-time errors
        __import__(import_name)
        print_check(f"Dependency: {module_name}", True, f"Module '{import_name}' imported successfully")
        return True
    except ImportError as e:
        print_check(f"Dependency: {module_name}", False, f"Import error: {e}")
        return False
    except Exception as e:
        print_check(f"Dependency: {module_name}", False, f"Unexpected error: {e}")
        return False


def check_ffmpeg():
    """Verify FFmpeg is installed and has libx264 codec"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            print_check("FFmpeg Availability", False, "FFmpeg command failed")
            return False

        output = result.stdout

        # Check for libx264 in configuration
        has_libx264 = 'libx264' in output

        # Extract version
        version_line = output.split('\n')[0] if output else "Unknown"

        print_check(
            "FFmpeg Availability",
            True,
            f"{version_line}"
        )
        print_check(
            "FFmpeg libx264 Codec",
            has_libx264,
            "libx264 codec is available" if has_libx264 else "libx264 codec NOT found"
        )

        return has_libx264

    except FileNotFoundError:
        print_check("FFmpeg Availability", False, "FFmpeg not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print_check("FFmpeg Availability", False, "FFmpeg command timed out")
        return False
    except Exception as e:
        print_check("FFmpeg Availability", False, f"Error: {e}")
        return False


def check_moviepy_textclip():
    """Verify MoviePy TextClip works with Pillow"""
    try:
        # Import using MoviePy 2.0 syntax
        from moviepy import TextClip

        # Try to create a simple TextClip
        clip = TextClip(
            text="Test",
            font_size=50,
            color='white',
            duration=1
        )

        # Verify clip has required attributes
        has_duration = hasattr(clip, 'duration') and clip.duration == 1
        has_size = hasattr(clip, 'size') and clip.size is not None

        success = has_duration and has_size

        print_check(
            "MoviePy TextClip Test",
            success,
            f"TextClip created successfully (size: {clip.size})" if success else "TextClip missing required attributes"
        )

        # Clean up
        clip.close()

        return success

    except ImportError as e:
        print_check("MoviePy TextClip Test", False, f"Import error: {e}")
        return False
    except Exception as e:
        print_check("MoviePy TextClip Test", False, f"Error creating TextClip: {e}")
        return False


def main():
    """Run all validation checks"""
    print_header("Environment Validation for Social Media Empire")

    results = []

    # Check Python version
    results.append(check_python_version())

    # Check dependencies
    print(f"\n{Colors.BOLD}Checking Python Dependencies:{Colors.RESET}")
    results.append(check_dependency("moviepy"))
    results.append(check_dependency("PIL", "PIL"))
    results.append(check_dependency("numpy"))
    results.append(check_dependency("imageio"))

    # Check FFmpeg
    print(f"\n{Colors.BOLD}Checking FFmpeg:{Colors.RESET}")
    results.append(check_ffmpeg())

    # Check MoviePy TextClip
    print(f"\n{Colors.BOLD}Checking MoviePy Functionality:{Colors.RESET}")
    results.append(check_moviepy_textclip())

    # Summary
    passed = sum(results)
    total = len(results)
    all_passed = all(results)

    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED ({passed}/{total}){Colors.RESET}")
        print(f"{Colors.GREEN}Environment is ready for development!{Colors.RESET}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME CHECKS FAILED ({passed}/{total} passed){Colors.RESET}")
        print(f"{Colors.RED}Please fix the issues above before proceeding.{Colors.RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
