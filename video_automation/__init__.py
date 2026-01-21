"""Video automation module for Social Media Empire."""

from .video_content_generator import VideoContentGenerator
from .video_templates import VideoTemplateManager, BRAND_TEMPLATES
from .daily_video_generator import DailyVideoGenerator
from .cross_platform_poster import CrossPlatformPoster
from .pinterest_idea_pins import PinterestIdeaPinCreator
from .youtube_shorts import YouTubeShortsUploader

__all__ = [
    "VideoContentGenerator",
    "VideoTemplateManager",
    "BRAND_TEMPLATES",
    "DailyVideoGenerator",
    "CrossPlatformPoster",
    "PinterestIdeaPinCreator",
    "YouTubeShortsUploader",
]
