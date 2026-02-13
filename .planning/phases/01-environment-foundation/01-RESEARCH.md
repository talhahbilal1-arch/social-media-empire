# Phase 1: Environment & Foundation - Research

**Researched:** 2026-01-23
**Domain:** Python Development Environment Setup for Video Automation
**Confidence:** HIGH

## Summary

Phase 1 establishes the foundational Python 3.11 environment with MoviePy 2.0+, FFmpeg, and proper project structure. The critical insight is that **MoviePy 2.0 eliminated ImageMagick as a dependency** in favor of pure Pillow for text rendering, dramatically simplifying installation. However, the system currently has Python 3.9.6 installed, while the project targets Python 3.11 for full compatibility. FFmpeg is not currently installed and requires Homebrew setup on macOS.

The environment validation phase must verify three critical components work together: (1) Python 3.11 with MoviePy 2.2.1+, (2) FFmpeg with libx264 codec for video encoding, and (3) Pillow for TextClip rendering without ImageMagick errors. The project structure should follow modern Python best practices with requirements.txt for strict dependency pinning (application deployment pattern).

**Primary recommendation:** Install Python 3.11 via pyenv or uv, create virtual environment, install dependencies via requirements.txt, install FFmpeg via Homebrew, then validate the full stack with a test video generation script before proceeding to Phase 2.

## Standard Stack

The established tools for Python video automation environment setup:

### Core Environment

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Python | 3.11.x | Runtime environment | User-specified; excellent balance of stability and modern features. MoviePy 2.2.1 supports 3.9-3.11 (3.12 has known issues). All dependencies compatible with 3.11. |
| pyenv or uv | Latest | Python version manager | pyenv is traditional standard (via Homebrew). uv is emerging 2026 best practice (10-100x faster, includes version management + package manager). Either works for 3.11 installation. |
| venv | Built-in | Virtual environment | Python's built-in module. Standard for isolated dependency management. uv also supports venv creation. |
| pip | Latest (24.x) | Package installer | Standard package manager. Works with requirements.txt. uv can replace pip for faster installs. |
| FFmpeg | Latest stable (7.x) | Video encoding backend | Universal multimedia framework. MoviePy depends on FFmpeg for all video/audio encoding/decoding. Must include libx264 codec. |
| Homebrew | Latest | macOS package manager | Standard for installing FFmpeg on macOS. Simplest installation method. |

### Core Dependencies

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| MoviePy | 2.2.1+ | Video compositing | Industry standard for programmatic video editing. V2.0+ uses pure Pillow (no ImageMagick). Clean API for text overlays, audio compositing, transitions. |
| Pillow | 12.1.0+ | Image/text rendering | Required by MoviePy 2.0+ for TextClip. Handles font rendering, image manipulation. Python 3.10+ required (compatible with 3.11). |
| FFmpeg-python | Optional | Python FFmpeg wrapper | Optional if need low-level FFmpeg control. MoviePy wraps FFmpeg internally for most use cases. |
| imageio | Latest | Media I/O | Automatic MoviePy dependency. Handles file format I/O. |
| imageio-ffmpeg | Latest | FFmpeg binaries | Provides FFmpeg binaries cross-platform. Ensures consistent FFmpeg availability. |
| numpy | <2.0 | Array processing | MoviePy dependency. Note: MoviePy may have issues with NumPy 2.x - pin to numpy<2 if import errors occur. |
| proglog | Latest | Progress logging | MoviePy dependency for rendering progress bars. |
| decorator | Latest | Function decorators | MoviePy internal dependency. |

### Development Dependencies

| Tool | Purpose | When to Use |
|------|---------|-------------|
| pytest | Unit testing | Test video generation functions, API mocks |
| black | Code formatting | Consistent Python style (community standard) |
| ruff | Fast linting | Replaces flake8/pylint for 2026 |
| python-dotenv | Environment variables | Local development with .env for API keys (not committed) |

**Installation:**
```bash
# Option 1: Traditional approach (pyenv + pip)
brew install pyenv
pyenv install 3.11
pyenv local 3.11
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Option 2: Modern approach (uv - faster)
brew install uv
uv venv --python 3.11
source .venv/bin/activate
uv pip install -r requirements.txt

# FFmpeg (required for either approach)
brew install ffmpeg
```

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pyenv | uv | uv is 10-100x faster and integrates version management + package installation. However, pyenv is more established with broader documentation. For 2026, uv is emerging best practice. |
| pyenv | System Python + venv | System Python (Xcode 3.9.6) is outdated. Project requires 3.11 for full dependency compatibility. Installing 3.11 system-wide risks conflicts. Use version manager. |
| venv | virtualenv | virtualenv was standard pre-Python 3.3. venv is now built-in and recommended. No need for external tool. |
| requirements.txt | pyproject.toml only | pyproject.toml is modern standard for libraries. For applications requiring strict version pinning and reproducible deployments, requirements.txt remains best practice. Use both: pyproject.toml for metadata, requirements.txt for locked versions. |
| Homebrew FFmpeg | Compile from source | Homebrew includes libx264 by default in 2026. Manual compilation is unnecessary complexity. Only compile if need exotic codecs. |

## Architecture Patterns

### Recommended Project Structure

```
social-media-empire/
├── .venv/                      # Virtual environment (gitignored)
├── .python-version             # pyenv version pin (3.11)
├── requirements.txt            # Locked dependencies with exact versions
├── pyproject.toml              # Project metadata (optional for Phase 1)
├── .gitignore                  # Ignore .venv, __pycache__, output/
├── .env.example                # Template for API keys (committed)
├── .env                        # Actual API keys (gitignored)
├── src/
│   ├── __init__.py
│   ├── orchestration/
│   ├── services/
│   ├── clients/
│   ├── models/
│   └── utils/
├── config/
│   ├── brands/
│   └── settings.py
├── assets/
│   ├── fonts/
│   └── watermarks/
├── output/                     # Generated videos (gitignored)
│   └── temp/                   # Temp files during processing
├── cache/                      # API response cache (gitignored)
│   ├── videos/
│   ├── audio/
│   └── scripts/
├── tests/
│   ├── unit/
│   └── integration/
└── scripts/
    └── validate_environment.py # Phase 1 validation script
```

### Pattern 1: Virtual Environment Isolation

**What:** All project dependencies installed in isolated .venv directory, never in global Python.

**When to use:** Always for Python projects. Prevents dependency conflicts between projects.

**Example:**
```bash
# Create venv (Python 3.11)
python3.11 -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Verify correct Python
which python  # Should show .venv/bin/python
python --version  # Should show 3.11.x

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

**Why it matters:** GitHub Actions will use its own isolated environment. Local virtual env ensures parity between dev and CI/CD.

### Pattern 2: Locked Dependency Versions

**What:** requirements.txt specifies exact versions (==) not ranges (>=). Ensures reproducible builds.

**When to use:** Applications deployed to production or CI/CD. Not for libraries (libraries use loose versions).

**Example:**
```
# requirements.txt - Locked versions
moviepy==2.2.1
pillow==12.1.0
numpy==1.26.4
imageio==2.36.0
imageio-ffmpeg==0.5.1
proglog==0.1.10
decorator==5.1.1

# Development dependencies
pytest==8.3.4
black==24.10.0
ruff==0.8.4
```

**Why it matters:** Prevents "works on my machine" issues. Same versions in dev, CI/CD, and production.

### Pattern 3: Environment Validation Script

**What:** Script that validates all dependencies and system requirements before development begins.

**When to use:** First step after environment setup. Run before any development work. Include in CI/CD setup.

**Example:**
```python
# scripts/validate_environment.py
import sys
import subprocess
import importlib

def check_python_version():
    """Verify Python 3.11.x"""
    version = sys.version_info
    if version.major != 3 or version.minor != 11:
        return False, f"Python 3.11 required, found {version.major}.{version.minor}"
    return True, f"Python {version.major}.{version.minor}.{version.micro}"

def check_ffmpeg():
    """Verify FFmpeg with libx264 codec"""
    try:
        result = subprocess.run(['ffmpeg', '-version'],
                               capture_output=True, text=True)
        if result.returncode != 0:
            return False, "FFmpeg not found"

        # Check for libx264
        codec_result = subprocess.run(['ffmpeg', '-codecs'],
                                     capture_output=True, text=True)
        if 'libx264' not in codec_result.stdout:
            return False, "FFmpeg missing libx264 codec"

        return True, "FFmpeg installed with libx264"
    except FileNotFoundError:
        return False, "FFmpeg not found in PATH"

def check_moviepy():
    """Verify MoviePy imports and TextClip works"""
    try:
        from moviepy import VideoClip, TextClip
        # Test TextClip with Pillow (no ImageMagick)
        clip = TextClip("Test", font='Arial', font_size=70, color='white')
        clip.close()
        return True, "MoviePy TextClip works with Pillow"
    except ImportError as e:
        return False, f"MoviePy import failed: {e}"
    except Exception as e:
        return False, f"TextClip failed: {e}"

def check_dependencies():
    """Verify all required packages"""
    required = ['moviepy', 'PIL', 'numpy', 'imageio']
    missing = []
    for package in required:
        try:
            importlib.import_module(package)
        except ImportError:
            missing.append(package)

    if missing:
        return False, f"Missing packages: {', '.join(missing)}"
    return True, "All dependencies installed"

def main():
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("FFmpeg", check_ffmpeg),
        ("MoviePy TextClip", check_moviepy),
    ]

    print("Environment Validation")
    print("=" * 60)

    all_passed = True
    for name, check_fn in checks:
        passed, message = check_fn()
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} | {name}: {message}")
        if not passed:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("✓ Environment ready for development")
        sys.exit(0)
    else:
        print("✗ Environment validation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Why it matters:** Catches environment issues before starting development. Saves hours of debugging "why doesn't X work?"

### Anti-Patterns to Avoid

- **Installing packages globally:** Never use `pip install` without activated venv. Pollutes system Python, causes conflicts.
- **Using system Python (3.9.6):** MoviePy dependencies require 3.10+. System Python outdated. Use version manager.
- **Skipping FFmpeg validation:** MoviePy will fail silently if FFmpeg missing libx264. Validate codec support explicitly.
- **Mixing pip and Homebrew Python packages:** Pick one: pyenv/uv OR Homebrew. Don't install Python packages via both.
- **Ignoring MoviePy 2.0 breaking changes:** v1.x syntax fails in v2.0. Pin version >=2.0,<3.0 and use v2 API from start.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Python version management | Shell scripts to switch versions, manually installing multiple Pythons | pyenv or uv | Handles installation, switching, .python-version files, and shell integration. Solves PATH conflicts. |
| Virtual environment | Manual PYTHONPATH manipulation, Docker containers for isolation | venv (built-in) | Built into Python 3.3+. Lightweight, standard, works everywhere. Docker overkill for dependency isolation. |
| Dependency locking | Manually noting versions, copying pip freeze | pip freeze > requirements.txt or uv pip compile | Captures exact versions including transitive dependencies. pip freeze is standard. |
| FFmpeg installation on macOS | Building from source, downloading binaries | Homebrew (brew install ffmpeg) | Homebrew includes libx264 by default. Handles dependencies, updates, uninstalls. |
| Font rendering for text overlays | ImageMagick, custom PIL rendering | MoviePy 2.0 TextClip with Pillow | MoviePy 2.0 uses Pillow internally. No need for ImageMagick. TextClip API handles font rendering. |

**Key insight:** Environment setup has well-established tooling. Use standard tools (pyenv/uv, venv, pip, Homebrew) rather than custom scripts. The ecosystem has solved these problems.

## Common Pitfalls

### Pitfall 1: Python Version Mismatch (System 3.9.6 vs Required 3.11)

**What goes wrong:** System has Python 3.9.6, but MoviePy dependencies (Pillow 12.1.0, google-genai SDK) require Python 3.10+. Installing packages fails with cryptic errors about unsupported Python version.

**Why it happens:** macOS includes Python 3.9.6 from Xcode Command Line Tools. This is the "system Python" and shouldn't be modified. Modern packages increasingly require Python 3.10+ (released 2021).

**How to avoid:**
- Install Python 3.11 via pyenv: `brew install pyenv && pyenv install 3.11`
- OR install via uv: `brew install uv && uv venv --python 3.11`
- Create project-specific .python-version file: `echo "3.11" > .python-version`
- Always activate virtual environment before pip install
- Verify Python version in venv: `python --version` should show 3.11.x
- Add to validation script: check sys.version_info.minor == 11

**Warning signs:**
- pip install fails with "Requires Python >=3.10"
- `which python` shows /usr/bin/python (system Python, not venv)
- Different Python version inside vs outside venv
- Import errors mentioning Python version compatibility

**Phase to address:** Phase 1 (this phase) - install Python 3.11 and create venv before any package installation.

---

### Pitfall 2: FFmpeg Not Installed or Missing libx264 Codec

**What goes wrong:** MoviePy's write_videofile() crashes with "FFmpeg not found" or "Unknown encoder 'libx264'" errors. Videos fail to render despite MoviePy importing successfully.

**Why it happens:** FFmpeg is external dependency not installed by pip. MoviePy wraps FFmpeg but doesn't include it. Some FFmpeg builds exclude libx264 (licensing). System has no FFmpeg by default.

**How to avoid:**
- Install FFmpeg via Homebrew: `brew install ffmpeg` (includes libx264 by default in 2026)
- Verify installation: `ffmpeg -version` (should show version)
- Verify libx264 codec: `ffmpeg -h encoder=libx264` (should show libx264 help)
- Test encoding: `ffmpeg -f lavfi -i testsrc2=duration=5:size=640x480:rate=30 -c:v libx264 test.mp4`
- Add to validation script: subprocess check for ffmpeg and libx264 codec
- For GitHub Actions: Use setup-ffmpeg action (FFmpeg not pre-installed)

**Warning signs:**
- "FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'"
- "Unknown encoder 'libx264'" when calling write_videofile()
- MoviePy imports successfully but rendering fails
- `which ffmpeg` returns nothing

**Phase to address:** Phase 1 (this phase) - install and validate FFmpeg before video composition work in Phase 2.

---

### Pitfall 3: MoviePy 2.0 Breaking Changes from 1.x

**What goes wrong:** Code written for MoviePy 1.x (or tutorials using v1 syntax) fails with ImportError or AttributeError in MoviePy 2.0. The moviepy.editor namespace no longer exists. Methods like set_duration() don't exist.

**Why it happens:** MoviePy 2.0 restructured API for consistency and immutability. Breaking changes necessary for better architecture. Many online tutorials still reference v1.x syntax (pre-2025).

**How to avoid:**
- Pin MoviePy version: `moviepy>=2.0,<3.0` in requirements.txt
- Use v2.0 syntax from start:
  - `from moviepy import VideoFileClip, TextClip` (not `from moviepy.editor import`)
  - `clip.with_duration(5)` (not `clip.set_duration(5)`)
  - `clip.with_fps(30)` (not `clip.set_fps(30)`)
- All methods return new clips (immutable), don't modify in-place
- Chain operations: `clip.with_duration(5).with_fps(30)`
- Read migration guide: https://zulko.github.io/moviepy/getting_started/updating_to_v2.html
- Ignore Stack Overflow answers from before 2025 (likely v1.x syntax)

**Warning signs:**
- `ImportError: cannot import name 'VideoFileClip' from 'moviepy.editor'`
- `AttributeError: 'VideoFileClip' object has no attribute 'set_duration'`
- Code works locally but fails in CI/CD (version mismatch)
- Unexpected behavior where clip modifications don't persist

**Phase to address:** Phase 1 (this phase) - pin correct version and validate v2.0 API before Phase 2 video composition.

---

### Pitfall 4: ImageMagick Dependency Confusion (v2.0 doesn't need it)

**What goes wrong:** Developers install ImageMagick thinking MoviePy TextClip requires it, then encounter font detection errors or version conflicts between ImageMagick 6 vs 7.

**Why it happens:** MoviePy 1.x required ImageMagick for TextClip. Many old tutorials (pre-2025) show ImageMagick installation steps. MoviePy 2.0 switched to pure Pillow but this isn't widely known yet.

**How to avoid:**
- **Don't install ImageMagick** - MoviePy 2.0 doesn't need it for TextClip
- MoviePy 2.0 uses Pillow for all image manipulation (confirmed by migration guide)
- Install only: moviepy and pillow (ImageMagick removed from dependencies)
- If TextClip fails, it's a Pillow issue (font not found), not ImageMagick
- Use system fonts or package .ttf fonts in assets/ directory
- Specify font explicitly in TextClip: `TextClip("text", font="Arial", ...)`

**Warning signs:**
- Installing ImageMagick 6 or 7 "for MoviePy"
- Searching for solutions to "ImageMagick not detected by MoviePy"
- Setting IMAGEMAGICK_BINARY environment variable
- Following pre-2025 tutorials that mention ImageMagick

**Phase to address:** Phase 1 (this phase) - document that ImageMagick NOT required. Validate TextClip works with Pillow only.

---

### Pitfall 5: requirements.txt Not Locked (Using >= Instead of ==)

**What goes wrong:** requirements.txt uses flexible versions (`moviepy>=2.0`) which allows automatic upgrades. Six months later, moviepy 2.5 breaks API compatibility and CI/CD starts failing despite code unchanged.

**Why it happens:** Developers think >= is safer ("get latest security fixes"). But Python packages don't follow semantic versioning strictly. Minor version bumps can break compatibility.

**How to avoid:**
- Use exact versions: `moviepy==2.2.1` not `moviepy>=2.2.1`
- Lock all dependencies including transitive ones: `pip freeze > requirements.txt`
- Regenerate requirements.txt when intentionally upgrading:
  - `pip install --upgrade moviepy`
  - `pip freeze > requirements.txt`
  - Test thoroughly, commit new requirements.txt
- For development dependencies, can use ranges in separate requirements-dev.txt
- Use pip-tools or uv pip compile for more sophisticated locking

**Warning signs:**
- CI/CD suddenly fails despite no code changes
- "Works on my machine" but fails for teammates
- Different package versions in different environments
- Using >= or ~= in requirements.txt

**Phase to address:** Phase 1 (this phase) - create requirements.txt with locked versions from pip freeze.

---

### Pitfall 6: Not Validating Environment Before Development

**What goes wrong:** Developer installs dependencies, assumes everything works, starts writing video composition code. Hours later discovers FFmpeg missing libx264, or TextClip fails with font errors.

**Why it happens:** pip install succeeds even if system dependencies missing. MoviePy imports successfully even if FFmpeg missing. Errors only appear at runtime when trying to encode video.

**How to avoid:**
- Create validation script (scripts/validate_environment.py) as shown in Architecture Patterns
- Run validation after environment setup: `python scripts/validate_environment.py`
- Check: Python version, all dependencies importable, FFmpeg installed, libx264 codec available, TextClip renders test text
- Make validation script part of CI/CD setup steps
- Document validation as required step in README

**Warning signs:**
- Starting Phase 2 development without validating stack
- "It worked on my laptop" but fails in GitHub Actions
- Discovering missing dependencies late in development

**Phase to address:** Phase 1 (this phase) - create and run validation script before marking Phase 1 complete.

## Code Examples

Verified patterns from official sources and best practices:

### Environment Setup Script

```bash
#!/bin/bash
# setup_environment.sh - Phase 1 environment setup

set -e  # Exit on error

echo "=== Social Media Empire - Environment Setup ==="

# Check macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script is for macOS. Adjust for your OS."
    exit 1
fi

# Install Homebrew if missing
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install pyenv (or uv - choose one)
echo "Installing pyenv for Python version management..."
brew install pyenv

# Configure shell (zsh on macOS)
if ! grep -q 'pyenv init' ~/.zshrc; then
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
    echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
    echo 'eval "$(pyenv init -)"' >> ~/.zshrc
    echo "Added pyenv to ~/.zshrc - restart shell or source ~/.zshrc"
fi

# Install Python 3.11
echo "Installing Python 3.11..."
pyenv install 3.11 --skip-existing
pyenv local 3.11

# Create virtual environment
echo "Creating virtual environment..."
python -m venv .venv
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install FFmpeg
echo "Installing FFmpeg..."
brew install ffmpeg

# Validate environment
echo "Validating environment..."
python scripts/validate_environment.py

echo "=== Setup Complete ==="
echo "To activate environment: source .venv/bin/activate"
```

### requirements.txt (Locked Versions)

```
# Core video processing
moviepy==2.2.1
pillow==12.1.0

# MoviePy dependencies (explicit for reproducibility)
numpy==1.26.4
imageio==2.36.0
imageio-ffmpeg==0.5.1
proglog==0.1.10
decorator==5.1.1

# Future dependencies (commented until needed in later phases)
# edge-tts==7.2.7
# google-genai==1.60.0
# requests==2.32.5
# supabase==2.27.2

# Development dependencies
pytest==8.3.4
black==24.10.0
ruff==0.8.4
```

### .gitignore (Project-Specific)

```
# Virtual environment
.venv/
venv/
env/

# Python cache
__pycache__/
*.py[cod]
*$py.class
*.so

# Environment variables (secrets)
.env

# Generated videos and temp files
output/
cache/

# macOS
.DS_Store

# IDE
.vscode/
.idea/
*.swp
*.swo

# Test artifacts
.pytest_cache/
.coverage
htmlcov/

# Build artifacts
dist/
build/
*.egg-info/
```

### .env.example (Template for API Keys)

```
# Copy to .env and fill in your API keys
# .env is gitignored - never commit secrets

# Gemini API key (for script generation - Phase 5)
GEMINI_API_KEY=your_key_here

# Pexels API key (for stock video - Phase 4)
PEXELS_API_KEY=your_key_here

# Supabase credentials (for video storage - Phase 4)
SUPABASE_URL=your_project_url
SUPABASE_ANON_KEY=your_anon_key
```

### Basic MoviePy Test (v2.0 Syntax)

```python
# test_moviepy.py - Verify MoviePy 2.0 works
from moviepy import ColorClip, TextClip, CompositeVideoClip

def test_basic_video():
    """Test MoviePy 2.0 can create video with text overlay."""

    # Create 5-second blue background (v2.0 syntax)
    background = ColorClip(
        size=(1080, 1920),  # Vertical video
        color=(0, 100, 200),  # RGB blue
        duration=5
    )

    # Create text overlay with Pillow (no ImageMagick)
    text = TextClip(
        text="MoviePy 2.0 Test",
        font="Arial",  # System font
        font_size=70,
        color="white"
    ).with_duration(5).with_position("center")

    # Composite (v2.0 immutable pattern)
    final = CompositeVideoClip([background, text])

    # Render with explicit codec
    final.write_videofile(
        "output/test.mp4",
        fps=30,
        codec="libx264",
        preset="ultrafast",
        audio=False
    )

    # Cleanup
    final.close()
    background.close()
    text.close()

    print("✓ MoviePy test successful: output/test.mp4")

if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)
    test_basic_video()
```

## State of the Art

| Old Approach | Current Approach (2026) | When Changed | Impact |
|--------------|-------------------------|--------------|--------|
| MoviePy 1.x with ImageMagick | MoviePy 2.0+ with Pillow only | May 2025 (v2.0 release) | Simpler installation, fewer dependencies, better Pillow integration. TextClip "just works" without ImageMagick setup. |
| pip + virtualenv | uv (unified tool) | 2024-2026 emerging | 10-100x faster installs, integrated Python version management, better lockfiles. Still optional - pip works fine. |
| requirements.txt only | pyproject.toml + requirements.txt | 2021+ (PEP 621) | pyproject.toml for metadata, requirements.txt for locked versions. Best of both worlds for applications. |
| Manual FFmpeg compilation | Homebrew with default libx264 | 2023+ (Homebrew changes) | Homebrew FFmpeg includes libx264 by default. No need for --with-libx264 flags or manual compilation. |
| Python 3.9 or earlier | Python 3.10+ required | 2024+ (modern packages) | Pillow 12.1.0, google-genai SDK require 3.10+. Python 3.11 is sweet spot (stable, well-tested, compatible). |

**Deprecated/outdated:**
- **MoviePy 1.x:** No longer maintained as of 2025. Use MoviePy 2.0+. Breaking API changes require migration.
- **ImageMagick for TextClip:** MoviePy 2.0 uses Pillow instead. Don't install ImageMagick.
- **google-generativeai SDK:** Deprecated November 2025. Use google-genai (unified SDK) instead.
- **FFmpeg --with-* Homebrew flags:** Removed from Homebrew core. Modern installs include standard codecs by default.
- **Python 3.9 or earlier:** Modern packages dropping support. Use 3.10+ (project targets 3.11).

## Open Questions

Things that couldn't be fully resolved:

1. **pyenv vs uv for version management**
   - What we know: Both install Python 3.11. pyenv is established (2013+), uv is emerging (2024+) and 10-100x faster.
   - What's unclear: Will uv become standard or remain niche? Long-term support?
   - Recommendation: Document both approaches. Default to pyenv (more documentation, proven). Advanced users can choose uv for speed.

2. **NumPy 2.x compatibility with MoviePy**
   - What we know: MoviePy may have issues with NumPy 2.x (reported in GitHub issues). NumPy 2.0 released 2024.
   - What's unclear: Has MoviePy 2.2.1 fixed NumPy 2.x compatibility?
   - Recommendation: Pin `numpy<2.0` in requirements.txt until verified. Test without pin - if works, remove constraint.

3. **Optimal FFmpeg preset for GitHub Actions**
   - What we know: preset='ultrafast' renders fastest but larger files. preset='medium' better quality but 3-5x slower.
   - What's unclear: GitHub Actions runner performance (CPU cores, time limits) for typical 60-second video.
   - Recommendation: Start with 'ultrafast' for Phase 1 validation. Benchmark in Phase 2 with realistic videos. Optimize later if needed.

## Sources

### Primary (HIGH confidence)

- [MoviePy Updating from v1.X to v2.X](https://zulko.github.io/moviepy/getting_started/updating_to_v2.html) - Official v2.0 migration guide, confirms ImageMagick removed
- [MoviePy PyPI](https://pypi.org/project/moviepy/) - Version and dependency information
- [MoviePy Releases](https://github.com/Zulko/moviepy/releases) - v2.0 release notes and breaking changes
- [Pillow PyPI](https://pypi.org/project/pillow/) - Python 3.10+ requirement for v12.1.0
- [FFmpeg Homebrew Formula](https://formulae.brew.sh/formula/ffmpeg) - Default codec inclusions
- [Python Packaging Guide - pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) - Official guidance on modern Python packaging
- [Install Python with Pyenv - Mac Install Guide 2026](https://mac.install.guide/python/install-pyenv) - Current macOS installation best practices
- [uv Documentation - Environments](https://docs.astral.sh/uv/pip/environments/) - Official uv usage guide

### Secondary (MEDIUM confidence)

- [How to Update Python - Mac Install Guide 2026](https://mac.install.guide/python/update) - macOS Python management patterns
- [Understanding Python Virtual Environments: venv vs uv](https://medium.com/@betecieai/understanding-python-virtual-environments-venv-vs-uv-9d9811f2c073) - Comparison of environment tools
- [Why Choose pyproject.toml over requirements.txt](https://pydevtools.com/handbook/explanation/pyproject-vs-requirements/) - Modern dependency management trade-offs
- [MoviePy Issue #2246 - Python 3.12/3.13 support](https://github.com/Zulko/moviepy/issues/2246) - Python version compatibility discussions
- [MoviePy Issue #2473 - Python 3.12 ModuleNotFoundError](https://github.com/zulko/moviepy/issues/2473) - Known Python 3.12 issues
- [How to install FFmpeg on Mac OSX](https://json2video.com/how-to/ffmpeg-course/install-ffmpeg-mac.html) - FFmpeg installation guide
- [FFmpeg Codecs Documentation](https://ffmpeg.org/ffmpeg-codecs.html) - Official codec reference

### Tertiary (LOW confidence - needs validation)

- Medium articles on Python environment setup - Useful patterns but not authoritative
- GitHub Gists on FFmpeg installation - May be outdated (pre-2023 Homebrew changes)
- Stack Overflow answers on MoviePy - Often reference v1.x, not v2.0

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All versions verified from PyPI, Homebrew formulae, and official docs
- Architecture patterns: HIGH - Based on established Python best practices (venv, requirements.txt, validation scripts)
- Pitfalls: HIGH - Drawn from PITFALLS.md research, GitHub issues, and migration guides

**Research date:** 2026-01-23
**Valid until:** 2026-03-23 (60 days - environment tooling is relatively stable)

**Key findings:**
1. MoviePy 2.0 eliminated ImageMagick dependency - major simplification
2. System Python 3.9.6 is incompatible - must install 3.11 via pyenv/uv
3. FFmpeg not installed - requires Homebrew installation
4. requirements.txt with locked versions remains best practice for applications
5. Environment validation script catches setup issues before development

**Next steps for planning:**
- Create setup_environment.sh script
- Create requirements.txt with locked versions
- Create scripts/validate_environment.py
- Update .gitignore for Python project
- Document environment setup in README
- Test full stack with basic MoviePy video generation
