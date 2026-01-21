"""API client wrappers for external services."""

import json
import requests
from typing import Optional, Any
from dataclasses import dataclass
import google.generativeai as genai


@dataclass
class GeminiClient:
    """Client for Google Gemini AI content generation."""

    api_key: str
    model_name: str = "gemini-1.5-flash"

    def __post_init__(self):
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def generate_content(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate content using Gemini."""
        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.7,
            )
        )
        return response.text

    def generate_video_script(
        self,
        brand: str,
        topic: str,
        style: str = "engaging",
        duration_seconds: int = 30
    ) -> dict:
        """Generate a video script with hooks, body, and CTA."""
        prompt = f"""Create a {duration_seconds}-second video script for {brand}.
Topic: {topic}
Style: {style}

Return JSON with:
- hook: Attention-grabbing opening (3-5 seconds)
- body: Main content points (array of 2-3 points)
- cta: Call to action
- hashtags: Array of 5 relevant hashtags
- music_mood: Suggested music mood (upbeat, calm, motivational, etc.)
"""
        response = self.generate_content(prompt)
        # Parse JSON from response
        try:
            # Handle markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            return json.loads(response.strip())
        except json.JSONDecodeError:
            return {
                "hook": topic,
                "body": [topic],
                "cta": "Follow for more!",
                "hashtags": ["#tips", "#lifestyle"],
                "music_mood": "upbeat"
            }


@dataclass
class PexelsClient:
    """Client for Pexels stock images and videos."""

    api_key: str
    base_url: str = "https://api.pexels.com/v1"
    video_url: str = "https://api.pexels.com/videos"

    @property
    def headers(self) -> dict:
        return {"Authorization": self.api_key}

    def search_photos(
        self,
        query: str,
        per_page: int = 5,
        orientation: str = "portrait"
    ) -> list[dict]:
        """Search for stock photos."""
        response = requests.get(
            f"{self.base_url}/search",
            headers=self.headers,
            params={
                "query": query,
                "per_page": per_page,
                "orientation": orientation
            }
        )
        response.raise_for_status()
        return response.json().get("photos", [])

    def search_videos(
        self,
        query: str,
        per_page: int = 5,
        orientation: str = "portrait"
    ) -> list[dict]:
        """Search for stock videos."""
        response = requests.get(
            f"{self.video_url}/search",
            headers=self.headers,
            params={
                "query": query,
                "per_page": per_page,
                "orientation": orientation
            }
        )
        response.raise_for_status()
        return response.json().get("videos", [])

    def get_photo_url(self, photo: dict, size: str = "large") -> str:
        """Extract photo URL from Pexels photo object."""
        return photo.get("src", {}).get(size, photo.get("src", {}).get("original", ""))

    def get_video_url(self, video: dict, quality: str = "hd") -> str:
        """Extract video URL from Pexels video object."""
        files = video.get("video_files", [])
        for f in files:
            if f.get("quality") == quality:
                return f.get("link", "")
        return files[0].get("link", "") if files else ""


@dataclass
class CreatomateClient:
    """Client for Creatomate video rendering."""

    api_key: str
    base_url: str = "https://api.creatomate.com/v1"

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_render(
        self,
        template_id: str,
        modifications: dict,
        output_format: str = "mp4"
    ) -> dict:
        """Create a video render from template."""
        payload = {
            "template_id": template_id,
            "modifications": modifications,
            "output_format": output_format
        }
        response = requests.post(
            f"{self.base_url}/renders",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_render_status(self, render_id: str) -> dict:
        """Check render status."""
        response = requests.get(
            f"{self.base_url}/renders/{render_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def wait_for_render(
        self,
        render_id: str,
        timeout_seconds: int = 300,
        poll_interval: int = 5
    ) -> dict:
        """Wait for render to complete."""
        import time
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            status = self.get_render_status(render_id)
            if status.get("status") == "succeeded":
                return status
            if status.get("status") == "failed":
                raise Exception(f"Render failed: {status.get('error')}")
            time.sleep(poll_interval)
        raise TimeoutError(f"Render {render_id} timed out after {timeout_seconds}s")


@dataclass
class YouTubeClient:
    """Client for YouTube API (uploads via OAuth)."""

    client_id: str
    client_secret: str
    refresh_token: str
    access_token: Optional[str] = None

    def _refresh_access_token(self) -> str:
        """Refresh OAuth access token."""
        response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token"
            }
        )
        response.raise_for_status()
        self.access_token = response.json()["access_token"]
        return self.access_token

    @property
    def headers(self) -> dict:
        if not self.access_token:
            self._refresh_access_token()
        return {"Authorization": f"Bearer {self.access_token}"}

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list[str],
        category_id: str = "22",  # People & Blogs
        privacy_status: str = "public"
    ) -> dict:
        """Upload a video to YouTube."""
        # Step 1: Initialize upload
        metadata = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False
            }
        }

        init_response = requests.post(
            "https://www.googleapis.com/upload/youtube/v3/videos",
            headers={
                **self.headers,
                "Content-Type": "application/json",
                "X-Upload-Content-Type": "video/mp4"
            },
            params={"uploadType": "resumable", "part": "snippet,status"},
            json=metadata
        )
        init_response.raise_for_status()
        upload_url = init_response.headers["Location"]

        # Step 2: Upload video file
        with open(video_path, "rb") as video_file:
            upload_response = requests.put(
                upload_url,
                headers={"Content-Type": "video/mp4"},
                data=video_file
            )
            upload_response.raise_for_status()
            return upload_response.json()


@dataclass
class PinterestClient:
    """Client for Pinterest via Make.com webhook."""

    webhook_url: str

    def create_pin(
        self,
        board_id: str,
        title: str,
        description: str,
        media_url: str,
        link: Optional[str] = None
    ) -> dict:
        """Create a Pinterest pin via Make.com webhook."""
        payload = {
            "board_id": board_id,
            "title": title,
            "description": description,
            "media_url": media_url,
            "link": link
        }
        response = requests.post(self.webhook_url, json=payload)
        response.raise_for_status()
        return response.json() if response.text else {"status": "success"}

    def create_idea_pin(
        self,
        board_id: str,
        title: str,
        pages: list[dict],
        link: Optional[str] = None
    ) -> dict:
        """Create a Pinterest Idea Pin via Make.com webhook."""
        payload = {
            "type": "idea_pin",
            "board_id": board_id,
            "title": title,
            "pages": pages,  # List of {media_url, description} dicts
            "link": link
        }
        response = requests.post(self.webhook_url, json=payload)
        response.raise_for_status()
        return response.json() if response.text else {"status": "success"}
