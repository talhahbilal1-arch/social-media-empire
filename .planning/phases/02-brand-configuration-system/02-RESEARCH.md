# Phase 2: Brand Configuration System - Research

**Researched:** 2026-01-23
**Domain:** Configuration Management with Python, Pydantic, and YAML
**Confidence:** HIGH

## Summary

This phase requires implementing a brand configuration system that loads distinct brand identities (colors, voice, CTAs) from YAML files. The standard approach in Python is to use **PyYAML with Pydantic 2.x** for type-safe configuration management. Pydantic already exists in the project (v2.10.6) along with pydantic-settings (v2.7.2), providing the foundation needed.

The recommended pattern is to create Pydantic BaseModel classes for brand configuration, load YAML files using `yaml.safe_load()`, and validate with `model_validate()`. For colors, use `pydantic_extra_types.color.Color` which validates hex codes, RGB, named colors, and provides conversion methods. For TTS voices, Edge-TTS uses a locale-based naming convention (e.g., `en-US-AriaNeural`) with 322+ voices across 74 languages, queryable via CLI.

**Primary recommendation:** Use PyYAML (standard library approach) + Pydantic BaseModel for validation, with Color type from pydantic-extra-types for color validation. Store brand configs in `config/brands/{brand-name}.yaml` and create a BrandLoader utility that loads by name.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PyYAML | 6.0.2+ | YAML parsing | Python's de facto YAML library, mature and secure with `safe_load()` |
| Pydantic | 2.10.6 | Data validation | Already in project, industry standard for Python type validation |
| pydantic-settings | 2.7.2 | Settings management | Already in project, official Pydantic extension for config |
| pydantic-extra-types | Latest | Extended types (Color) | Official Pydantic extension for color validation |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pydantic-yaml | 1.6.0 | Pydantic+YAML helpers | Optional: provides `to_yaml_str()` and `parse_yaml_raw_as()` convenience |
| edge-tts | 6.1.18 | TTS voice list | Already in project, provides `--list-voices` for discovery |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| PyYAML + Pydantic | pydantic-yaml | Less explicit control, adds dependency, but more convenient for serialization |
| Manual loading | YamlConfigSettingsSource | More integrated with pydantic-settings, but overkill for simple brand loading |
| Manual color parsing | pydantic-extra-types Color | Reinventing wheel vs using validated type with conversions |

**Installation:**
```bash
# Add to requirements.txt
pyyaml==6.0.2
pydantic-extra-types==2.10.6  # Matches Pydantic version
```

## Architecture Patterns

### Recommended Project Structure
```
config/
├── brands/
│   ├── menopause-planner.yaml    # Sage green/dusty rose, Etsy CTA
│   ├── daily-deal-darling.yaml   # Coral/teal, website CTA
│   └── fitness-made-easy.yaml    # Blue/lime, TBD CTA
src/
├── models/
│   ├── __init__.py
│   └── brand.py                  # BrandConfig BaseModel
└── utils/
    ├── __init__.py
    └── brand_loader.py           # Load brand by name
```

### Pattern 1: Pydantic BaseModel for Brand Configuration
**What:** Define typed configuration model with validation
**When to use:** Always for configuration management in Python
**Example:**
```python
# Source: https://docs.pydantic.dev/latest/concepts/models/
from pydantic import BaseModel, Field
from pydantic_extra_types.color import Color
from typing import Optional

class ColorPalette(BaseModel):
    primary: Color = Field(description="Primary brand color (hex, RGB, or named)")
    secondary: Color = Field(description="Secondary brand color")
    accent: Optional[Color] = Field(None, description="Optional accent color")

class BrandConfig(BaseModel):
    name: str = Field(description="Brand display name")
    slug: str = Field(description="URL-safe brand identifier")
    colors: ColorPalette
    tts_voice: str = Field(description="Edge-TTS voice identifier (e.g., en-US-AriaNeural)")
    cta_text: str = Field(description="Call-to-action text")
    cta_url: str = Field(description="Call-to-action URL")

    class Config:
        # Allow extra fields for future expansion
        extra = "ignore"
```

### Pattern 2: Safe YAML Loading with Validation
**What:** Load YAML using safe_load, then validate with Pydantic
**When to use:** Always when loading YAML configuration
**Example:**
```python
# Source: https://docs.pydantic.dev/latest/concepts/models/
# Combined with: https://dev.to/fkkarakurt/be-careful-when-using-yaml-in-python-there-may-be-security-vulnerabilities-3cdb
import yaml
from pathlib import Path
from typing import Dict, Any

def load_brand_yaml(brand_file: Path) -> Dict[str, Any]:
    """Load YAML safely - prevents arbitrary code execution."""
    with brand_file.open('r') as f:
        # CRITICAL: Always use safe_load, never load()
        data = yaml.safe_load(f)
    return data

def load_brand_config(brand_name: str) -> BrandConfig:
    """Load and validate brand configuration by name."""
    config_path = Path(f"config/brands/{brand_name}.yaml")
    if not config_path.exists():
        raise FileNotFoundError(f"Brand config not found: {brand_name}")

    data = load_brand_yaml(config_path)
    # Use model_validate for dict input (faster than __init__)
    return BrandConfig.model_validate(data)
```

### Pattern 3: Brand Loader Utility
**What:** Central utility for loading brands by name
**When to use:** When CLI or services need brand configurations
**Example:**
```python
# Source: Pattern from multi-tenant Python systems
from typing import Dict
from functools import lru_cache

class BrandLoader:
    """Load and cache brand configurations."""

    def __init__(self, config_dir: Path = Path("config/brands")):
        self.config_dir = config_dir
        self._cache: Dict[str, BrandConfig] = {}

    @lru_cache(maxsize=10)
    def load(self, brand_name: str) -> BrandConfig:
        """Load brand config with caching."""
        config_path = self.config_dir / f"{brand_name}.yaml"
        data = load_brand_yaml(config_path)
        return BrandConfig.model_validate(data)

    def list_brands(self) -> list[str]:
        """List available brand names."""
        return [
            f.stem for f in self.config_dir.glob("*.yaml")
        ]
```

### Pattern 4: YAML Configuration Format
**What:** Human-readable, consistent YAML structure
**When to use:** All brand configuration files
**Example:**
```yaml
# Source: https://www.cloudbees.com/blog/yaml-tutorial-everything-you-need-get-started
# config/brands/menopause-planner.yaml
name: Menopause Planner
slug: menopause-planner

colors:
  primary: "#9CAF88"      # Sage green
  secondary: "#D4A5A5"    # Dusty rose
  accent: "#F5F5DC"       # Beige

tts_voice: en-US-JennyNeural  # Warm, friendly female voice

cta_text: Shop on Etsy
cta_url: https://etsy.com/shop/menopauseplanner

# Optional metadata (ignored by model with extra="ignore")
description: Empowering women through menopause transition
target_audience: Women 45-60
```

### Anti-Patterns to Avoid
- **Using `yaml.load()` without Loader:** Security vulnerability - can execute arbitrary code. Always use `yaml.safe_load()`.
- **Mixing validation and loading:** Keep YAML loading separate from validation. Load with PyYAML, validate with Pydantic.
- **Hard-coding brand names:** Use `list_brands()` to discover available brands dynamically from filesystem.
- **Manual color parsing:** Don't write regex validators for hex codes. Use `pydantic_extra_types.Color` which handles hex, RGB, HSL, and named colors.
- **String-based color storage:** Store colors as validated Color objects, not strings. Provides type safety and conversion methods.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Color validation | Regex for hex codes | `pydantic_extra_types.Color` | Supports multiple formats (hex, RGB, HSL, named), validates, and provides conversions (`.as_hex()`, `.as_rgb()`) |
| YAML parsing | Custom YAML parser | `yaml.safe_load()` from PyYAML | Industry standard, secure, handles edge cases |
| Configuration validation | Manual type checking | Pydantic `BaseModel` | Automatic validation, helpful errors, type coercion, documentation |
| TTS voice discovery | Hard-coded voice list | `edge-tts --list-voices` | Always current, includes gender/personality metadata |
| Brand name loading | Config registry class | Filesystem glob + stem | Self-documenting, no registration needed |

**Key insight:** Configuration management has mature solutions. Use Pydantic for validation (already in project), PyYAML for parsing (standard library approach), and filesystem-based discovery. Don't build custom parsers or validators.

## Common Pitfalls

### Pitfall 1: Using unsafe YAML loading
**What goes wrong:** `yaml.load()` without safe loader can execute arbitrary Python code from YAML files.
**Why it happens:** Default `yaml.load()` is as powerful as `pickle.load()` and may call any Python function.
**How to avoid:** Always use `yaml.safe_load()` which restricts to basic types (dicts, lists, strings, numbers).
**Warning signs:** Security scanners flag `yaml.load()` calls. Code review should reject any non-safe YAML loading.
**Source:** [DEV Community: YAML Security in Python](https://dev.to/fkkarakurt/be-careful-when-using-yaml-in-python-there-may-be-security-vulnerabilities-3cdb)

### Pitfall 2: Wrong Pydantic validation method
**What goes wrong:** Using deprecated `parse_obj()` or confusing `model_validate()` with `model_validate_json()`.
**Why it happens:** Migration from Pydantic v1 to v2 changed method names.
**How to avoid:**
- Use `model_validate(dict_data)` for Python dicts
- Use `model_validate_json(json_str)` for JSON strings (faster)
- Never use deprecated `parse_obj()` or `parse_raw()`
**Warning signs:** Deprecation warnings from Pydantic. Tests failing after Pydantic upgrade.
**Source:** [Pydantic Migration Guide](https://docs.pydantic.dev/latest/migration/)

### Pitfall 3: Color format inconsistency
**What goes wrong:** Some colors stored as "#FF0000", others as "FF0000" or "rgb(255,0,0)", causing parsing failures.
**Why it happens:** Manual color input without validation.
**How to avoid:** Use `Color` type in Pydantic model. Accepts all formats, stores internally, provides `.as_hex()` for consistent output.
**Warning signs:** Color parsing errors in logs. Visual inconsistencies in output.
**Source:** [Pydantic Color Types](https://docs.pydantic.dev/latest/api/pydantic_extra_types_color/)

### Pitfall 4: Hardcoded brand references
**What goes wrong:** Code has `if brand == "menopause-planner"` scattered throughout, making new brands hard to add.
**Why it happens:** Not treating brands as data-driven configuration.
**How to avoid:** All brand-specific logic should use properties from `BrandConfig`, never check brand name strings.
**Warning signs:** Adding a new brand requires code changes in multiple files.

### Pitfall 5: Missing Edge-TTS voice validation
**What goes wrong:** Brand config specifies invalid voice name, fails at TTS generation time.
**Why it happens:** No validation that voice exists when config is loaded.
**How to avoid:** Create custom Pydantic validator that checks voice against `edge-tts --list-voices` output, or at minimum validate naming pattern.
**Warning signs:** Runtime errors during TTS generation instead of config load time.

### Pitfall 6: YAML indentation errors
**What goes wrong:** YAML files fail to parse due to tab characters or inconsistent spacing.
**Why it happens:** YAML only allows spaces for indentation, and requires consistency (2 or 4 spaces).
**How to avoid:** Use `.editorconfig` or linter to enforce spaces. Validate YAML files in CI/CD.
**Warning signs:** `yaml.scanner.ScannerError` exceptions during loading.
**Source:** [YAML Tutorial: CloudBees](https://www.cloudbees.com/blog/yaml-tutorial-everything-you-need-get-started)

## Code Examples

Verified patterns from official sources:

### Loading and Using Brand Config
```python
# Source: Combined from https://docs.pydantic.dev/latest/concepts/models/
# and https://dev.to/fkkarakurt/be-careful-when-using-yaml-in-python-there-may-be-security-vulnerabilities-3cdb

from pathlib import Path
import yaml
from pydantic import BaseModel, Field
from pydantic_extra_types.color import Color

class ColorPalette(BaseModel):
    primary: Color
    secondary: Color
    accent: Color | None = None

class BrandConfig(BaseModel):
    name: str
    slug: str
    colors: ColorPalette
    tts_voice: str
    cta_text: str
    cta_url: str

def load_brand(brand_slug: str) -> BrandConfig:
    """Load and validate brand configuration."""
    config_file = Path(f"config/brands/{brand_slug}.yaml")

    with config_file.open('r') as f:
        data = yaml.safe_load(f)  # CRITICAL: Use safe_load

    return BrandConfig.model_validate(data)

# Usage in CLI
if __name__ == "__main__":
    brand = load_brand("menopause-planner")
    print(f"Loaded: {brand.name}")
    print(f"Primary color: {brand.colors.primary.as_hex()}")
    print(f"TTS voice: {brand.tts_voice}")
    print(f"CTA: {brand.cta_text} -> {brand.cta_url}")
```

### Accessing Color Properties
```python
# Source: https://docs.pydantic.dev/latest/api/pydantic_extra_types_color/

from pydantic_extra_types.color import Color

# Color accepts many formats
color = Color("#9CAF88")      # Hex with #
color = Color("9CAF88")       # Hex without #
color = Color("sage")         # Named color
color = Color("rgb(156, 175, 136)")  # RGB string

# Convert to different formats
hex_code = color.as_hex()     # "#9caf88"
rgb_tuple = color.as_rgb_tuple()  # (156, 175, 136)
rgb_str = color.as_rgb()      # "rgb(156, 175, 136)"
hsl_tuple = color.as_hsl_tuple()  # (hue, saturation, lightness)

# Use in video generation (example)
from PIL import ImageColor
pil_color = ImageColor.getrgb(color.as_hex())
```

### Listing Available Brands
```python
# Source: Filesystem-based discovery pattern
from pathlib import Path
from typing import List

def list_available_brands(config_dir: Path = Path("config/brands")) -> List[str]:
    """Discover brands from filesystem."""
    return sorted([
        yaml_file.stem
        for yaml_file in config_dir.glob("*.yaml")
    ])

# Usage
brands = list_available_brands()
print(f"Available brands: {', '.join(brands)}")
```

### Edge-TTS Voice Discovery
```python
# Source: https://github.com/rany2/edge-tts
import subprocess
import json

def list_edge_tts_voices(language: str = None, gender: str = None) -> list:
    """List available Edge-TTS voices with filtering.

    Args:
        language: Filter by language code (e.g., 'en', 'en-US')
        gender: Filter by gender ('Male', 'Female')
    """
    result = subprocess.run(
        ["edge-tts", "--list-voices"],
        capture_output=True,
        text=True
    )

    # Parse output (tab-separated table)
    lines = result.stdout.strip().split('\n')[1:]  # Skip header
    voices = []

    for line in lines:
        parts = line.split('\t')
        voice = {
            'name': parts[0],
            'gender': parts[1],
            'locale': parts[0].split('-')[0] + '-' + parts[0].split('-')[1]
        }

        # Apply filters
        if language and not voice['name'].startswith(language):
            continue
        if gender and voice['gender'] != gender:
            continue

        voices.append(voice)

    return voices

# Usage: Get female English voices
female_voices = list_edge_tts_voices(language='en-US', gender='Female')
for v in female_voices[:3]:
    print(f"{v['name']} ({v['gender']})")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pydantic v1 `parse_obj()` | Pydantic v2 `model_validate()` | Pydantic 2.0 (June 2023) | Better performance, clearer semantics |
| Manual color hex validation | `pydantic_extra_types.Color` | Pydantic 2.x | Supports multiple formats, built-in conversions |
| `yaml.load()` | `yaml.safe_load()` | PyYAML 5.1 (2019) | Security: prevents code execution from YAML |
| ConfigParser (INI files) | YAML + Pydantic | Modern Python | Better nesting, type validation, human-readable |
| JSON config files | YAML config files | Industry shift 2020+ | Comments, multi-line strings, more readable |

**Deprecated/outdated:**
- `parse_obj()`: Deprecated in Pydantic v2, use `model_validate()`
- `parse_raw()`: Deprecated in Pydantic v2, use `model_validate_json()`
- `yaml.load()` without Loader: Security risk, use `yaml.safe_load()`
- Pydantic v1 Color from `pydantic.color`: Moved to `pydantic_extra_types.color` in v2

## Open Questions

Things that couldn't be fully resolved:

1. **Edge-TTS voice validation at config load time**
   - What we know: Edge-TTS provides `--list-voices` to get available voices
   - What's unclear: Best pattern for validating voice names without making subprocess call during config load
   - Recommendation: Start without validation, add custom validator later that caches voice list or validates naming pattern

2. **Color palette accessibility validation**
   - What we know: Colors can be validated for format, converted between formats
   - What's unclear: Whether to validate color contrast ratios for accessibility (e.g., WCAG AA compliance)
   - Recommendation: Defer accessibility validation to future phase, focus on format validation now

3. **Brand configuration versioning**
   - What we know: YAML files will change over time
   - What's unclear: Whether to version brand configs (v1, v2) or handle breaking changes
   - Recommendation: Use Pydantic's `extra="ignore"` to allow forward compatibility, add version field if needed later

4. **Multiple CTA support**
   - What we know: Requirements specify single CTA per brand
   - What's unclear: Whether brands will need multiple CTAs in future
   - Recommendation: Start with single CTA fields, easy to change to list of CTAs later

## Sources

### Primary (HIGH confidence)
- [Pydantic Models Documentation](https://docs.pydantic.dev/latest/concepts/models/) - Official validation patterns
- [Pydantic Color Types API](https://docs.pydantic.dev/latest/api/pydantic_extra_types_color/) - Color validation and conversion
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Settings management patterns
- [PyPI: pydantic-yaml 1.6.0](https://pypi.org/project/pydantic-yaml/) - YAML convenience functions
- [GitHub: rany2/edge-tts](https://github.com/rany2/edge-tts) - Edge-TTS voice API and CLI
- [Edge TTS Voices Gist](https://gist.github.com/BettyJJ/17cbaa1de96235a7f5773b8690a20462) - Complete voice list with metadata

### Secondary (MEDIUM confidence)
- [Medium: Pydantic and YAML Configuration Guide (2025)](https://medium.com/@jonathan_b/a-simple-guide-to-configure-your-python-project-with-pydantic-and-a-yaml-file-bef76888f366) - Implementation patterns
- [DEV: YAML Security in Python](https://dev.to/fkkarakurt/be-careful-when-using-yaml-in-python-there-may-be-security-vulnerabilities-3cdb) - Security best practices
- [CloudBees: YAML Tutorial](https://www.cloudbees.com/blog/yaml-tutorial-everything-you-need-get-started) - YAML formatting best practices
- [Viget: Multi-Tenancy in Django](https://www.viget.com/articles/multi-tenancy-in-django/) - Brand configuration patterns
- [Edge TTS Voices: Free Text-to-Speech API](https://tts.travisvn.com/) - Voice samples and categories

### Tertiary (LOW confidence)
- WebSearch results on brand configuration systems - General patterns, not Python-specific
- WebSearch results on design systems - Conceptual guidance for brand attributes

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - PyYAML and Pydantic are industry standards, versions verified from PyPI
- Architecture: HIGH - Patterns verified from official Pydantic docs and security guides
- Pitfalls: HIGH - Security issues documented in multiple authoritative sources, Pydantic migration guide is official
- Edge-TTS voices: MEDIUM - Voice list verified from gist and GitHub, but voice selection UX is implementation detail
- Color validation: HIGH - Official Pydantic documentation for Color type with API reference

**Research date:** 2026-01-23
**Valid until:** 2026-02-23 (30 days - stable technologies, but Pydantic updates frequently)
