"""arXiv RSS signal collector.

Fetches papers from arXiv CS/Finance collections filtered for
fintech, lending, credit, LLM, retention, and India signals.
"""

import feedparser
from datetime import datetime, timedelta, timezone
from signal_collectors.base import Signal, SignalCollector


ARXIV_RSS_URL = "https://export.arxiv.org/rss/cs.IR&q-fin.GN"

# Keywords that indicate relevance to this system's domain
FILTER_KEYWORDS = [
    # Core fintech / credit
    "credit", "lending", "fintech", "credit scoring", "loan default",
    "borrowing", "debt", "credit risk", "financial inclusion",
    "microfinance", "peer-to-peer", "bnpl", "buy now pay later",
    "embedded finance", " Lending", "credit evaluation",
    # India-specific
    "india", "indian", "aadhaar", "upi", "ruperee", "rupee",
    "non-metro", "tier-2", "tier-3",
    # LLM / AI in finance
    "large language model", "llm", "bert", "gpt", "transformer",
    "natural language processing", "nlp", "nlu",
    "text classification", "sentiment", "financial sentiment",
    # Retention / growth
    "customer retention", "churn", "engagement", "conversion",
    "customer lifetime value", "clv", "activation",
    "acquisition", "funnel", "drop-off", "retention",
    # Alternative data / credit
    "alternative data", "digital footprint", "transaction data",
    "mobile money", "digital credit", "thin file", "credit thin",
]


def _is_relevant(entry_title: str, entry_summary: str) -> bool:
    """Return True if the paper is relevant to our domain."""
    text = (entry_title + " " + entry_summary).lower()
    # Require at least 2 keyword matches to filter out noise
    matches = sum(1 for kw in FILTER_KEYWORDS if kw.lower() in text)
    return matches >= 2


class ArxivCollector(SignalCollector):
    """Collect signals from arXiv CS/Finance RSS feed."""

    def source_name(self) -> str:
        return "arxiv"

    def collect(self, max_age_days: int = 30) -> list[Signal]:
        """Fetch recent arXiv papers and filter for relevant ones.

        Args:
            max_age_days: Only collect papers from the last N days

        Returns:
            List of Signal objects
        """
        signals = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)

        try:
            feed = feedparser.parse(ARXIV_RSS_URL)
        except Exception as e:
            print(f"  ⚠ Failed to fetch arXiv RSS: {e}")
            return []

        for entry in feed.entries:
            # Parse publication date
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                except Exception:
                    published = None

            # Skip old entries
            if published and published < cutoff:
                continue

            title = getattr(entry, "title", "") or ""
            summary = getattr(entry, "summary", "") or ""
            link = getattr(entry, "link", "") or ""

            if not title:
                continue

            if not _is_relevant(title, summary):
                continue

            signal = Signal(
                text=f"[arXiv] {title}. {summary[:500]}",
                source="arxiv",
                category="research_paper",
                url=link,
                collected_at=datetime.now(timezone.utc),
                metadata={
                    "feed_name": "arxiv_cs_ir_qfin",
                    "published": published.isoformat() if published else None,
                    "paper_title": title.strip(),
                    "relevance_keywords": [kw for kw in FILTER_KEYWORDS if kw.lower() in (title + summary).lower()],
                },
            )
            signals.append(signal)

        return signals
