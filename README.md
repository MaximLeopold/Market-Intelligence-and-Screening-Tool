# Market-Intelligence-and-Screening-Tool
AI-powered market intelligence platform that collects, enriches, and structures information from public sources to identify business events, market developments, competitive activity, and strategic signals. The tool is intended to be taylored to specific topics or themes of interest for monitoring. 


## Overview

Market Intelligence Tool as AI-powered platform that continuously collects information from public sources and transforms unstructured content into structured business intelligence.

The system automates the process of monitoring public sources such as news feeds, industry publications, company announcements, and other available sources to identify relevant information covering topics including but not limited to market developments, competitive activity, funding events, partnerships, acquisitions, executive changes, regulatory updates, and emerging trends.

Using Large Language Models, raw articles are enriched with structured metadata, allowing users to build searchable intelligence repositories, monitor industries, and detect strategic signals at scale.



# Architecture Overview

```text
Public sources / RSS feeds
        ↓
src/collect.py
        ↓
Supabase `items` table
        ↓
src/enrich.py
        ↓
Claude / LLM enrichment
        ↓
Structured market intelligence database
```

## Workflow

1. Configure public sources in `sources.yaml`.
2. Run `src/collect.py` to collect recent public-source articles.
3. New articles are stored in Supabase.
4. Run `src/enrich.py` to classify and enrich articles using an LLM.
5. Structured fields can be used for screening, filtering, dashboards, alerts, or reporting.
