"""Late API client for Pinterest video posting.

Late API handles the complex Pinterest video upload workflow:
- Multi-step media upload
- Video transcoding
- Pin creation with proper video format

This replaces the broken Make.com webhook approach that was using
image URL for videos (Pinterest error 235 "Sorry, this image is broken").
"""
import os
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

from src.clients.base import BaseClient


@dataclass
class LatePostResult:
      """Result of posting via Late API."""
      success: bool
      post_id: Optional[str] = None
      platform_post_url: Optional[str] = None
      error: Optional[str] = None
      raw_response: Dict[str, Any] = field(default_factory=dict)


class LateAPIClient(BaseClient):
      """Client for Late API - handles Pinterest video posting.

          Late API abstracts Pinterest's complex video upload workflow into
              a single API call that handles:
                  - Media upload to Pinterest servers
                      - Video transcoding/processing
                          - Pin creation with proper video format

                              Docs: https://docs.getlate.dev/
                                  """

    LATE_API_BASE_URL = "https://getlate.dev/api/v1"

    def __init__(
              self,
              api_key: Optional[str] = None,
              timeout: float = 120.0  # Longer timeout for video uploads
    ):
              """Initialize Late API client.

                      Args:
                                  api_key: Late API key (defaults to LATE_API_KEY env var)
                                              timeout: Request timeout in seconds (default 120s for video)
                                                      """
              self.api_key = api_key or os.getenv('LATE_API_KEY')
              if not self.api_key:
                            raise ValueError("LATE_API_KEY is required")

              super().__init__(
                  base_url=self.LATE_API_BASE_URL,
                  api_key=self.api_key,
                  timeout=timeout,
                  logger_name="LateAPIClient"
              )

        self._pinterest_account_id: Optional[str] = None

    def get_pinterest_account_id(self) -> Optional[str]:
              """Get the connected Pinterest account ID.

                      Returns:
                                  Pinterest account ID if connected, None otherwise
                                          """
              if self._pinterest_account_id:
                            return self._pinterest_account_id

              try:
                            response = self._request("GET", "/accounts")
                            accounts = response.json()

                  # Find Pinterest account
                            for account in accounts.get('accounts', []):
                                              if account.get('platform') == 'pinterest':
                                                                    self._pinterest_account_id = account.get('_id')
                                                                    self.logger.info(f"Found Pinterest account: {account.get('username')}")
                                                                    return self._pinterest_account_id

                                          self.logger.warning("No Pinterest account connected to Late API")
                            return None

              except Exception as e:
                            self.logger.error(f"Failed to get accounts: {e}")
                            return None

          def create_pinterest_video_pin(
                    self,
                    video_url: str,
                    title: str,
                    description: str,
                    link: Optional[str] = None,
                    board_id: Optional[str] = None,
                    publish_now: bool = True
          ) -> LatePostResult:
                    """Create a Pinterest video pin via Late API.

                            Args:
                                        video_url: Public URL of the video file (must be accessible)
                                                    title: Pin title
                                                                description: Pin description (can include hashtags)
                                                                            link: Destination URL when pin is clicked
                                                                                        board_id: Pinterest board ID (uses default if not specified)
                                                                                                    publish_now: If True, publish immediately; if False, create as draft
                                                                                                    
                                                                                                            Returns:
                                                                                                                        LatePostResult with success status and pin URL
                                                                                                                                """
                    account_id = self.get_pinterest_account_id()
                    if not account_id:
                                  return LatePostResult(
                                                    success=False,
                                                    error="No Pinterest account connected to Late API"
                                  )

                    # Build the request payload
                    payload: Dict[str, Any] = {
                                  "content": title,  # Late uses 'content' for the text
                                  "platforms": [
                                                    {
                                                                          "platform": "pinterest",
                                                                          "accountId": account_id
                                                    }
                                  ],
                                  "mediaUrls": [video_url],  # Late handles video upload from URL
                    }

        # Add optional fields
        if description:
                      # Pinterest uses description for the pin text
                      # Late API combines content + description
                      payload["content"] = f"{title}\n\n{description}"

        if link:
                      payload["platformSettings"] = {
                                        "pinterest": {
                                                              "link": link
                                        }
                      }
                      if board_id:
                                        payload["platformSettings"]["pinterest"]["boardId"] = board_id
        elif board_id:
                      payload["platformSettings"] = {
                                        "pinterest": {
                                                              "boardId": board_id
                                        }
                      }

        # Set status based on publish_now
        if not publish_now:
                      payload["status"] = "draft"

        try:
                      self.logger.info(f"Creating Pinterest video pin: {title[:50]}...")

            response = self._request("POST", "/posts", json=payload)
            result = response.json()

            # Extract the post info
            post = result.get('post', result)
            post_id = post.get('_id')

            # Get Pinterest-specific result
            platforms = post.get('platforms', [])
            pinterest_result = None
            for p in platforms:
                              if p.get('platform') == 'pinterest':
                                                    pinterest_result = p
                                                    break

                          # Check if successful
                          status = post.get('status', '')
            if status in ['published', 'queued', 'processing']:
                              platform_url = None
                              if pinterest_result:
                                                    platform_url = pinterest_result.get('platformPostUrl')

                              self.logger.info(f"Pinterest video pin created successfully: {post_id}")
                              return LatePostResult(
                                  success=True,
                                  post_id=post_id,
                                  platform_post_url=platform_url,
                                  raw_response=result
                              )
else:
                  error_msg = post.get('error') or f"Unexpected status: {status}"
                  self.logger.error(f"Pinterest video pin failed: {error_msg}")
                  return LatePostResult(
                      success=False,
                      error=error_msg,
                      raw_response=result
                  )

except Exception as e:
            self.logger.error(f"Failed to create Pinterest video pin: {e}")
            return LatePostResult(
                              success=False,
                              error=str(e)
            )

    def get_post_status(self, post_id: str) -> Dict[str, Any]:
              """Get the status of a post.

                      Args:
                                  post_id: The Late API post ID

                                          Returns:
                                                      Post status information
                                                              """
              try:
                            response = self._request("GET", f"/posts/{post_id}")
                            return response.json()
except Exception as e:
            self.logger.error(f"Failed to get post status: {e}")
            return {"error": str(e)}

    def list_pinterest_boards(self) -> List[Dict[str, Any]]:
              """List available Pinterest boards.

                      Returns:
                                  List of board objects with id, name, etc.
                                          """
              account_id = self.get_pinterest_account_id()
              if not account_id:
                            return []

              try:
                            response = self._request(
                                              "GET",
                                              f"/accounts/{account_id}/boards"
                            )
                            result = response.json()
                            return result.get('boards', [])
except Exception as e:
            self.logger.error(f"Failed to list boards: {e}")
            return []


def create_late_client() -> Optional[LateAPIClient]:
      """Factory function to create Late API client.

          Returns:
                  LateAPIClient if LATE_API_KEY is configured, None otherwise
                      """
      api_key = os.getenv('LATE_API_KEY')
      if not api_key:
                logging.getLogger("LateAPIClient").warning(
                              "LATE_API_KEY not set - Pinterest posting disabled"
                )
                return None

      try:
                return LateAPIClient(api_key=api_key)
except Exception as e:
        logging.getLogger("LateAPIClient").error(f"Failed to create Late client: {e}")
        return None
