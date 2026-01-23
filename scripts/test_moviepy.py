#!/usr/bin/env python3
"""
MoviePy Test Script for Social Media Empire

Generates a test video to verify the MoviePy 2.0 stack works correctly.
Creates a 5-second vertical video (1080x1920) with text overlay using MoviePy 2.0 syntax.

Output: output/test.mp4 (libx264 codec)
"""

import sys
from pathlib import Path
from moviepy import TextClip, CompositeVideoClip, ColorClip


def main():
    """Generate test video with MoviePy"""

    print("=" * 60)
    print("MoviePy Test Video Generator")
    print("=" * 60)

    # Configuration
    width = 1080
    height = 1920
    duration = 5
    fps = 30
    output_path = Path("output/test.mp4")

    print(f"\nConfiguration:")
    print(f"  Resolution: {width}x{height} (vertical)")
    print(f"  Duration: {duration} seconds")
    print(f"  FPS: {fps}")
    print(f"  Output: {output_path}")

    try:
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print("\n[1/4] Creating background...")
        # Create black background
        background = ColorClip(
            size=(width, height),
            color=(0, 0, 0),
            duration=duration
        )

        print("[2/4] Creating text overlay...")
        # Create text clip with MoviePy 2.0 syntax
        text = TextClip(
            text="MoviePy 2.0\nTest Video",
            font_size=80,
            color='white',
            duration=duration,
            method='caption',
            size=(width - 100, None)
        )

        # Center the text
        text = text.with_position('center')

        print("[3/4] Compositing video...")
        # Composite background and text
        video = CompositeVideoClip([background, text])
        video = video.with_duration(duration)
        video = video.with_fps(fps)

        print("[4/4] Writing video file...")
        # Write video file with libx264 codec
        video.write_videofile(
            str(output_path),
            codec='libx264',
            audio=False,
            fps=fps,
            preset='medium',
            logger=None  # Suppress MoviePy's progress bar for cleaner output
        )

        # Clean up
        background.close()
        text.close()
        video.close()

        # Get file size
        file_size = output_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)

        print("\n" + "=" * 60)
        print("✓ SUCCESS")
        print("=" * 60)
        print(f"Video created: {output_path}")
        print(f"File size: {file_size:,} bytes ({file_size_mb:.2f} MB)")
        print(f"Resolution: {width}x{height}")
        print(f"Duration: {duration} seconds")
        print("=" * 60)

        return 0

    except ImportError as e:
        print(f"\n✗ ERROR: Missing dependency - {e}")
        print("Please install required dependencies: pip install -r requirements.txt")
        return 1
    except FileNotFoundError as e:
        print(f"\n✗ ERROR: FFmpeg not found - {e}")
        print("Please install FFmpeg with libx264 codec")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
