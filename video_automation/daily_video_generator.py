"""Main orchestrator for daily video generation."""

import logging
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field

from utils.config import get_config
from database.supabase_client import get_supabase_client
from .video_content_generator import VideoContentGenerator, VideoContent
from .video_templates import VideoTemplateManager
from .cross_platform_poster import CrossPlatformPoster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DailyVideoGenerator:
    """Orchestrates the daily video generation pipeline."""

    content_generator: VideoContentGenerator = field(default=None)
    template_manager: VideoTemplateManager = field(default=None)
    platform_poster: CrossPlatformPoster = field(default=None)

    def __post_init__(self):
        if self.content_generator is None:
            self.content_generator = VideoContentGenerator()
        if self.template_manager is None:
            self.template_manager = VideoTemplateManager()
        if self.platform_poster is None:
            self.platform_poster = CrossPlatformPoster()

    def generate_and_post(
        self,
        brand: str,
        topic: Optional[str] = None,
        platforms: Optional[list[str]] = None,
        dry_run: bool = False
    ) -> dict:
        """Generate and post a single video for a brand.

        Args:
            brand: Brand identifier
            topic: Optional specific topic (auto-generated if not provided)
            platforms: Target platforms (defaults to all)
            dry_run: If True, generate but don't post

        Returns:
            dict with video details and posting results
        """
        config = get_config()
        db = get_supabase_client()

        if platforms is None:
            platforms = config.platforms

        logger.info(f"Starting video generation for {brand}")

        try:
            # Step 1: Generate content
            logger.info(f"Generating content for topic: {topic or 'auto-generated'}")
            content = self.content_generator.generate_content(brand, topic)

            # Step 2: Get background media
            logger.info(f"Fetching background media for: {content.background_query}")
            backgrounds = self.content_generator.get_background_media(
                content.background_query,
                media_type="video",
                count=1
            )
            background_url = backgrounds[0]["url"] if backgrounds else None

            # Step 3: Render video
            logger.info("Rendering video with Creatomate")
            render_result = self._render_video(brand, content, background_url)

            video_url = render_result.get("url", "")

            # Step 4: Log to database
            video_record = db.log_video_creation(
                brand=brand,
                platform="all",
                video_url=video_url,
                title=content.hook,
                description=self._format_description(content),
                status="rendered"
            )

            # Step 5: Post to platforms
            posting_results = {}
            if not dry_run and video_url:
                logger.info(f"Posting to platforms: {platforms}")
                posting_results = self.platform_poster.post_to_all(
                    video_url=video_url,
                    title=content.hook,
                    description=self._format_description(content),
                    hashtags=content.hashtags,
                    brand=brand,
                    platforms=platforms
                )

                # Update database with posting status
                for platform, result in posting_results.items():
                    if result.get("success"):
                        db.update_video_status(
                            video_id=video_record.get("id"),
                            status="posted",
                            platform_id=result.get("platform_id")
                        )
                    else:
                        db.log_error(
                            error_type="posting_failure",
                            error_message=result.get("error", "Unknown error"),
                            context={"brand": brand, "platform": platform}
                        )

            # Log analytics
            db.log_analytics_event(
                event_type="video_created",
                brand=brand,
                platform="all",
                data={
                    "topic": content.topic,
                    "hook": content.hook,
                    "platforms_posted": list(posting_results.keys())
                }
            )

            return {
                "success": True,
                "brand": brand,
                "content": {
                    "topic": content.topic,
                    "hook": content.hook,
                    "hashtags": content.hashtags
                },
                "video_url": video_url,
                "posting_results": posting_results,
                "video_id": video_record.get("id")
            }

        except Exception as e:
            logger.error(f"Error generating video for {brand}: {e}")
            db.log_error(
                error_type="generation_failure",
                error_message=str(e),
                context={"brand": brand, "topic": topic}
            )
            return {
                "success": False,
                "brand": brand,
                "error": str(e)
            }

    def _render_video(
        self,
        brand: str,
        content: VideoContent,
        background_url: Optional[str]
    ) -> dict:
        """Render video using template manager."""
        try:
            content_dict = {
                "hook": content.hook,
                "body_points": content.body_points,
                "cta": content.cta,
                "hashtags": content.hashtags
            }

            result = self.template_manager.render_video_and_wait(
                brand=brand,
                content=content_dict,
                background_url=background_url
            )
            return result
        except Exception as e:
            logger.warning(f"Creatomate render failed: {e}, using placeholder")
            # Return placeholder for development/testing
            return {
                "url": f"https://placeholder.video/{brand}/{content.topic.replace(' ', '-')}.mp4",
                "status": "placeholder"
            }

    def _format_description(self, content: VideoContent) -> str:
        """Format video description with hashtags."""
        points = "\n".join([f"\u2022 {p}" for p in content.body_points])
        hashtags = " ".join(content.hashtags)
        return f"{content.hook}\n\n{points}\n\n{content.cta}\n\n{hashtags}"

    def run_scheduled_generation(
        self,
        time_slot: str = "morning",
        dry_run: bool = False
    ) -> list[dict]:
        """Run scheduled video generation for all brands.

        Args:
            time_slot: One of 'morning', 'noon', 'evening'
            dry_run: If True, generate but don't post

        Returns:
            List of results for each brand
        """
        config = get_config()
        results = []

        logger.info(f"Running scheduled generation for {time_slot} slot")

        for brand in config.brands:
            result = self.generate_and_post(
                brand=brand,
                platforms=config.platforms,
                dry_run=dry_run
            )
            results.append(result)

            # Log result
            status = "success" if result.get("success") else "failed"
            logger.info(f"{brand}: {status}")

        # Summary
        successful = sum(1 for r in results if r.get("success"))
        logger.info(f"Completed: {successful}/{len(results)} videos generated")

        return results

    def generate_batch(
        self,
        brands: list[str],
        videos_per_brand: int = 1,
        dry_run: bool = False
    ) -> list[dict]:
        """Generate multiple videos for multiple brands.

        Args:
            brands: List of brand identifiers
            videos_per_brand: Number of videos per brand
            dry_run: If True, generate but don't post

        Returns:
            List of all results
        """
        results = []

        for brand in brands:
            for i in range(videos_per_brand):
                logger.info(f"Generating video {i+1}/{videos_per_brand} for {brand}")
                result = self.generate_and_post(brand=brand, dry_run=dry_run)
                results.append(result)

        return results


def main():
    """CLI entry point for video generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate and post videos")
    parser.add_argument("--brand", help="Specific brand to generate for")
    parser.add_argument("--topic", help="Specific topic for the video")
    parser.add_argument("--slot", choices=["morning", "noon", "evening"],
                       help="Time slot for scheduled generation")
    parser.add_argument("--dry-run", action="store_true",
                       help="Generate but don't post")

    args = parser.parse_args()

    generator = DailyVideoGenerator()

    if args.slot:
        # Run scheduled generation
        results = generator.run_scheduled_generation(
            time_slot=args.slot,
            dry_run=args.dry_run
        )
    elif args.brand:
        # Single brand generation
        result = generator.generate_and_post(
            brand=args.brand,
            topic=args.topic,
            dry_run=args.dry_run
        )
        results = [result]
    else:
        # Default: all brands
        config = get_config()
        results = generator.run_scheduled_generation(dry_run=args.dry_run)

    # Print summary
    for result in results:
        brand = result.get("brand", "unknown")
        if result.get("success"):
            print(f"\u2713 {brand}: {result.get('content', {}).get('topic', 'N/A')}")
        else:
            print(f"\u2717 {brand}: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
