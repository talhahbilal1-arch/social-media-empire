"""
Extract Amazon ASINs from HTML files.

Scans index.html and article files for Amazon affiliate links
and extracts unique ASINs for verification.
"""

import re
import json
import argparse
from pathlib import Path
from typing import Set
from dataclasses import dataclass, asdict


@dataclass
class ExtractedLink:
    """Represents an extracted affiliate link."""
    asin: str
    url: str
    source_file: str
    line_number: int
    context: str  # Surrounding text for identification


def extract_asins_from_file(file_path: Path) -> list[ExtractedLink]:
    """
    Extract all Amazon ASINs from an HTML file.

    Args:
        file_path: Path to HTML file

    Returns:
        List of ExtractedLink objects
    """
    extracted = []

    # ASIN patterns in Amazon URLs
    # /dp/ASIN, /gp/product/ASIN, /product/ASIN
    asin_pattern = r'(?:amazon\.com/(?:dp|gp/product|product)/([A-Z0-9]{10}))'

    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Find all ASIN matches in this line
            for match in re.finditer(asin_pattern, line, re.IGNORECASE):
                asin = match.group(1).upper()

                # Extract URL context
                url_match = re.search(
                    rf'https?://[^\s"\'<>]*{asin}[^\s"\'<>]*',
                    line,
                    re.IGNORECASE
                )
                url = url_match.group(0) if url_match else f"amazon.com/dp/{asin}"

                # Get surrounding context (product name if available)
                context = ""
                # Look for alt text or title nearby
                alt_match = re.search(r'alt="([^"]*)"', line)
                if alt_match:
                    context = alt_match.group(1)
                else:
                    title_match = re.search(r'title="([^"]*)"', line)
                    if title_match:
                        context = title_match.group(1)

                extracted.append(ExtractedLink(
                    asin=asin,
                    url=url,
                    source_file=str(file_path),
                    line_number=line_num,
                    context=context[:100] if context else "",
                ))

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return extracted


def extract_all_asins(source_paths: list[str]) -> dict:
    """
    Extract ASINs from multiple files/directories.

    Args:
        source_paths: List of file paths or directories

    Returns:
        Dict with unique ASINs and their locations
    """
    all_links: list[ExtractedLink] = []
    seen_asins: Set[str] = set()

    for source in source_paths:
        path = Path(source)

        if path.is_file() and path.suffix == '.html':
            all_links.extend(extract_asins_from_file(path))

        elif path.is_dir():
            for html_file in path.rglob('*.html'):
                all_links.extend(extract_asins_from_file(html_file))

    # Deduplicate and organize
    unique_asins = {}
    for link in all_links:
        if link.asin not in unique_asins:
            unique_asins[link.asin] = {
                'asin': link.asin,
                'locations': [],
                'first_context': link.context,
            }
        unique_asins[link.asin]['locations'].append({
            'file': link.source_file,
            'line': link.line_number,
            'url': link.url,
        })

    return {
        'total_links_found': len(all_links),
        'unique_asins': len(unique_asins),
        'asins': list(unique_asins.values()),
    }


def main():
    parser = argparse.ArgumentParser(
        description='Extract Amazon ASINs from HTML files'
    )
    parser.add_argument(
        '--source',
        nargs='+',
        default=['index.html', 'articles/'],
        help='Files or directories to scan'
    )
    parser.add_argument(
        '--output',
        default='asins.json',
        help='Output JSON file path'
    )

    args = parser.parse_args()

    print(f"Scanning: {args.source}")
    result = extract_all_asins(args.source)

    print(f"Found {result['total_links_found']} total links")
    print(f"Found {result['unique_asins']} unique ASINs")

    # Write output
    output_path = Path(args.output)
    output_path.write_text(json.dumps(result, indent=2))
    print(f"Written to {args.output}")

    # Print summary
    print("\nASINs found:")
    for item in result['asins']:
        context = f" - {item['first_context']}" if item['first_context'] else ""
        print(f"  {item['asin']}{context} ({len(item['locations'])} locations)")


if __name__ == "__main__":
    main()
