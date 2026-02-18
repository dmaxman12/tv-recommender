# TV Show Recommender — Product Requirements Document

## Overview
A personal TV show recommendation tool that lets users enter favorite shows and discovers similar ones. Uses the free TVmaze API for show data and content-based filtering to compute similarity. Served as a local Flask web app.

## Problem
Finding new TV shows to watch is time-consuming. Streaming platform recommendations are siloed to their own catalog and driven by engagement metrics rather than genuine taste matching. Users want a single tool that works across all networks and services to surface shows similar to ones they already love.

## Target User
Individual users looking for TV show recommendations based on personal taste, not platform availability.

## User Flow
1. User starts the app (`python app.py`) and opens `http://localhost:5050`
2. User searches for a TV show using the search bar (live results with 300ms debounce)
3. User clicks a result to add it to their favorites list
4. User repeats to build a collection of 2+ favorites
5. User clicks "Get Recommendations"
6. System searches for candidate shows based on favorite genres, scores them, and returns the top 20
7. Recommendations display as cards with match percentage, shared genres, ratings, and summaries

## Features

### Search
- Type-ahead search bar querying TVmaze API
- Results show thumbnail, name, genres, rating, and network
- 300ms debounce to avoid excessive API calls
- Top 10 results displayed in a dropdown

### Favorites Management
- Add shows from search results with one click
- Visual cards with show image, name, genres, and rating
- Remove button on each card
- Duplicate prevention (same show can't be added twice)
- Badge showing favorite count

### Recommendation Engine
Content-based filtering combining four similarity signals:

| Signal | Weight | Method |
|--------|--------|--------|
| Genre similarity | 40% | Jaccard similarity of genre sets |
| Text similarity | 30% | TF-IDF cosine similarity of show summaries |
| Network match | 15% | Binary — 1.0 if same network, 0.0 otherwise |
| Rating proximity | 15% | Normalized distance: `1 - |a - b| / 10` |

- Candidate pool built by searching TVmaze for each genre keyword from favorites plus show name terms
- Favorites are excluded from results
- Top 20 results returned, sorted by composite score

### Recommendation Display
- Cards with show image, match percentage badge, name, genres, rating, network
- Shared genres highlighted as explanation for why the show was recommended
- Truncated summary text

## Technical Architecture

```
tv-recommender/
  app.py              # Flask app — routes and entry point
  tvmaze.py           # TVmaze API client
  recommender.py      # Similarity engine
  templates/
    index.html         # Single-page UI (vanilla HTML/CSS/JS)
  static/
    style.css          # Dark theme styling
  requirements.txt     # Flask, requests, scikit-learn
```

### API Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Serve the single-page UI |
| `/api/search?q=<query>` | GET | Proxy TVmaze search, return JSON |
| `/api/recommend` | POST | Accept `{show_ids: [int]}`, return ranked recommendations |

### External Dependencies
- **TVmaze API** (https://api.tvmaze.com) — free, no auth required, rate-limited
- **Flask** — web framework
- **requests** — HTTP client for TVmaze
- **scikit-learn** — TF-IDF vectorization and cosine similarity

## Design
- Dark theme (`#0f0f0f` background)
- Card-based layout with responsive grid
- Indigo accent color (`#6366f1`) for interactive elements
- Loading spinner during recommendation computation

## Constraints
- No user accounts or persistence — favorites exist only in the browser session
- TVmaze API rate limits apply (no API key needed)
- Recommendation quality depends on candidate pool size (limited by search-based discovery)
- Runs locally only — not designed for deployment

## Future Considerations
- Persist favorites in localStorage
- Add "type" filtering (scripted, reality, animation, etc.)
- Expand candidate pool using TVmaze page-based bulk fetch
- Add year/decade filtering
- Show where to watch (streaming availability)
