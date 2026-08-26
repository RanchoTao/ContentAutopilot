from __future__ import annotations

import tweepy

from .config import Settings


class XPublisher:
    def __init__(self, settings: Settings):
        required = {
            "X consumer key": settings.x_consumer_key,
            "X consumer secret": settings.x_consumer_secret,
            "X access token": settings.x_access_token,
            "X access token secret": settings.x_access_token_secret,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError("Missing credentials: " + ", ".join(missing))
        self.client = tweepy.Client(
            consumer_key=settings.x_consumer_key,
            consumer_secret=settings.x_consumer_secret,
            access_token=settings.x_access_token,
            access_token_secret=settings.x_access_token_secret,
            wait_on_rate_limit=True,
        )

    def publish(self, text: str) -> str:
        response = self.client.create_tweet(text=text, user_auth=True)
        data = response.data or {}
        post_id = data.get("id")
        if not post_id:
            raise RuntimeError(f"X API returned no post id: {response}")
        return str(post_id)
