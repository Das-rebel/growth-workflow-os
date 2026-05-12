"""Signal collectors — market intelligence sources."""

from signal_collectors.base import Signal, SignalCollector
from signal_collectors.rss_collector import RSSCollector
from signal_collectors.arxiv_collector import ArxivCollector
from signal_collectors.reddit_collector import collect_reddit
from signal_collectors.google_trends_collector import collect_google_trends
from signal_collectors.hackernews_collector import collect_hackernews
from signal_collectors.producthunt_collector import collect_producthunt
from signal_collectors.twitter_collector import collect_twitter
from signal_collectors.linkedin_collector import collect_linkedin
from signal_collectors.manual import submit as manual_signal
from signal_collectors.competitor_collector import collect_competitor

__all__ = [
    "Signal",
    "SignalCollector",
    "RSSCollector",
    "ArxivCollector",
    "collect_reddit",
    "collect_google_trends",
    "collect_hackernews",
    "collect_producthunt",
    "collect_twitter",
    "collect_linkedin",
    "collect_competitor",
    "manual_signal",
]