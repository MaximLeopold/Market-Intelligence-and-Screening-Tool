# Database Schema

This document describes the database structure used by the Market Intelligence and Screening Tool.

The project uses a Supabase table called `items` to store collected public-source articles and the structured AI enrichment output.

## Table: `items`

```sql
CREATE TABLE items (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    -- Raw source data
    source_name TEXT,
    title TEXT,
    url TEXT UNIQUE,
    raw_text TEXT,
    language TEXT,
    collected_at TIMESTAMPTZ DEFAULT NOW(),

    -- AI enrichment output
    enriched JSONB,
    event_type TEXT,
    sentiment TEXT,
    summary TEXT,
    relevance_score INTEGER,
    deal_size TEXT,
    investors JSONB,
    target_market TEXT,
    forward_signals TEXT
);
```

## Notes

- `url` should be unique to prevent duplicate articles.
- `enriched` stores the full JSON response from the LLM.
- Individual columns such as `event_type`, `sentiment`, and `relevance_score` make filtering and dashboarding easier.
