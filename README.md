# TV Show Recommender

A personal TV show recommendation tool that discovers shows similar to your favorites. Uses the [TVmaze API](https://www.tvmaze.com/api) for show data and content-based filtering to compute similarity.

## How It Works

1. Search for TV shows and add your favorites
2. Click "Get Recommendations"
3. The engine finds similar shows using:
   - **Genre similarity** (40%) — Jaccard similarity of genre sets
   - **Text similarity** (30%) — TF-IDF cosine similarity of show summaries
   - **Network match** (15%) — same network/streaming service
   - **Rating proximity** (15%) — normalized rating distance

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5050** in your browser.

## Dependencies

- Flask — web framework
- requests — TVmaze API calls
- scikit-learn — TF-IDF vectorization and cosine similarity

## Screenshot

Search for shows, add favorites, get personalized recommendations with match scores and shared-genre explanations.
