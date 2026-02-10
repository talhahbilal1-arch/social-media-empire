"""
Vercel deployment service for Anti-Gravity.

Replaces WordPress — writes article JSON to the Next.js content directory
and triggers a Vercel redeployment via CLI.
"""

import json
import logging
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

SITE_DIR = Path(__file__).parent.parent / "site"
CONTENT_DIR = SITE_DIR / "content" / "articles"


@dataclass
class DeployResult:
    success: bool
    slug: str
    post_url: Optional[str] = None
    deploy_url: Optional[str] = None
    error: Optional[str] = None


class VercelDeployer:
    """Handles writing articles and deploying to Vercel."""

    def __init__(self, site_dir: Optional[Path] = None):
        self.site_dir = site_dir or SITE_DIR
        self.content_dir = self.site_dir / "content" / "articles"
        self.content_dir.mkdir(parents=True, exist_ok=True)

        # Get the production URL from .vercel/project.json if available
        self.production_url = self._get_production_url()

    def _get_production_url(self) -> Optional[str]:
        """Read the Vercel project URL from the .vercel directory."""
        vercel_dir = self.site_dir / ".vercel" / "project.json"
        if vercel_dir.exists():
            try:
                data = json.loads(vercel_dir.read_text())
                project_id = data.get("projectId", "")
                org_id = data.get("orgId", "")
                if project_id:
                    logger.info(f"Vercel project: {project_id}")
            except Exception:
                pass
        return None

    def save_article(
        self,
        title: str,
        slug: str,
        html: str,
        meta_description: str,
        word_count: int,
        keyword: str,
        image_prompt: str = "",
    ) -> Path:
        """Save an article as a JSON file in the content directory."""
        article_data = {
            "title": title,
            "slug": slug,
            "html": html,
            "meta_description": meta_description,
            "word_count": word_count,
            "keyword": keyword,
            "image_prompt": image_prompt,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        filepath = self.content_dir / f"{slug}.json"
        filepath.write_text(json.dumps(article_data, indent=2, ensure_ascii=False))
        logger.info(f"Article saved: {filepath}")
        return filepath

    def deploy(self, prod: bool = True) -> DeployResult:
        """Deploy the site to Vercel using the CLI."""
        cmd = ["vercel", "--yes"]
        if prod:
            cmd.append("--prod")

        logger.info(f"Deploying to Vercel: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.site_dir),
                capture_output=True,
                text=True,
                timeout=300,
            )

            output = result.stdout + result.stderr
            logger.info(f"Vercel output: {output[:500]}")

            if result.returncode != 0:
                return DeployResult(
                    success=False,
                    slug="",
                    error=f"Deploy failed (exit {result.returncode}): {output[:300]}",
                )

            # Extract the production URL from output
            # Vercel CLI uses ANSI escape codes that can concatenate text with URLs
            import re
            deploy_url = None
            urls = re.findall(r'https://[a-zA-Z0-9\-]+\.vercel\.app', output)
            if urls:
                deploy_url = urls[-1]  # Last URL is typically the production one

            return DeployResult(
                success=True,
                slug="",
                deploy_url=deploy_url,
            )

        except subprocess.TimeoutExpired:
            return DeployResult(
                success=False,
                slug="",
                error="Deploy timed out after 300 seconds",
            )
        except FileNotFoundError:
            return DeployResult(
                success=False,
                slug="",
                error="Vercel CLI not found. Install with: npm i -g vercel",
            )

    def publish_article(
        self,
        title: str,
        slug: str,
        html: str,
        meta_description: str,
        word_count: int,
        keyword: str,
        image_prompt: str = "",
    ) -> DeployResult:
        """Save article and deploy in one step."""
        # Save the article
        self.save_article(
            title=title,
            slug=slug,
            html=html,
            meta_description=meta_description,
            word_count=word_count,
            keyword=keyword,
            image_prompt=image_prompt,
        )

        # Deploy
        deploy_result = self.deploy(prod=True)

        if deploy_result.success and deploy_result.deploy_url:
            # Construct the article URL
            base_url = deploy_result.deploy_url.rstrip("/")
            post_url = f"{base_url}/articles/{slug}"
            deploy_result.slug = slug
            deploy_result.post_url = post_url
            logger.info(f"Article live at: {post_url}")

        return deploy_result

    def verify_article_live(self, url: str, max_retries: int = 5) -> bool:
        """Verify the article is accessible via HTTP."""
        import requests

        for attempt in range(max_retries):
            try:
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    logger.info(f"Article verified live: {url}")
                    return True
                logger.warning(f"Attempt {attempt + 1}: HTTP {resp.status_code}")
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1}: {e}")

            if attempt < max_retries - 1:
                time.sleep(5)

        return False
