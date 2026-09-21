# Data sources

| Source | Status | Notes |
|---|---|---|
| YouTube Data API v3 | Collector built | Default quota is 10,000 units per day. `search.list` costs 100, `videos.list` and `commentThreads.list` cost 1. One query is about 105 units, so roughly 90 queries a day. Responses are cached 6 hours. `YOUTUBE_DAILY_QUOTA_BUDGET` stops the collector before the real limit |
| Reddit | Collector built | App-only OAuth. Reddit's Data API terms and approval requirements have changed over time. Read the current terms before commercial use. Send a descriptive `REDDIT_USER_AGENT`. The collector stops on rate-limit headers |
| RSS/Atom | Collector built | Public feeds, keyword filtered |
| Trends | Interface only | `TrendProvider`. Google Trends access is limited, so nothing depends on it |
| AnswerThePublic | Stub | Optional. Implement once you have API access |

Adding a source: subclass `SourceProvider`, emit `RawItem`, add it to the list in the worker. Set `metadata.kind` to `post`, `comment`, `video` or `article`, and `metadata.author_key` so one person repeating themselves is not counted as demand.

Privacy: collect only public content needed for scoring. No private messages, no account credentials.
