"""RSS feed signal collector."""

import feedparser
from datetime import datetime, timedelta
from typing import Optional
from signal_collectors.base import Signal, SignalCollector
from config import load_sources


class RSSCollector(SignalCollector):
    """Collects signals from RSS feeds defined in config/sources.yaml."""

    def __init__(self):
        self.sources_config = load_sources()
        self.feeds = self.sources_config.get("rss_feeds", [])

    def source_name(self) -> str:
        return "rss"

    def collect(self, max_age_hours: int = 48, feed_name: Optional[str] = None) -> list[Signal]:
        """Collect recent entries from RSS feeds.

        Args:
            max_age_hours: Only collect entries newer than this
            feed_name: If specified, only collect from this named feed

        Returns:
            List of Signal objects from RSS entries
        """
        signals = []
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)

        for feed_config in self.feeds:
            if feed_name and feed_config["name"] != feed_name:
                continue

            try:
                feed = feedparser.parse(feed_config["url"])
                for entry in feed.entries:
                    # Parse publication date
                    published = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                        published = datetime(*entry.updated_parsed[:6])

                    # Skip old entries
                    if published and published < cutoff:
                        continue

                    signal = Signal(
                        text=entry.get("title", "") + ". " + entry.get("summary", ""),
                        source=f"rss:{feed_config['name']}",
                        category=feed_config.get("category", "market_analysis"),
                        url=entry.get("link"),
                        collected_at=datetime.utcnow(),
                        metadata={
                            "feed_name": feed_config["name"],
                            "published": published.isoformat() if published else None,
                            "frequency": feed_config.get("frequency", "unknown"),
                        },
                    )
                    signals.append(signal)

            except Exception as e:
                print(f"  ⚠ Error collecting from {feed_config['name']}: {e}")
                continue

        return signals
