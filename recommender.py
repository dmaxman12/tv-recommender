from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from tvmaze import search_shows

# Weights for each similarity signal
GENRE_WEIGHT = 0.40
TEXT_WEIGHT = 0.30
NETWORK_WEIGHT = 0.15
RATING_WEIGHT = 0.15


def _genre_similarity(genres_a, genres_b):
    """Jaccard similarity between two genre lists."""
    set_a = set(genres_a)
    set_b = set(genres_b)
    if not set_a and not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def _text_similarity(summaries_a, summary_b):
    """TF-IDF cosine similarity between favorite summaries and a candidate."""
    combined_favorites = " ".join(s for s in summaries_a if s)
    if not combined_favorites or not summary_b:
        return 0.0
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf = vectorizer.fit_transform([combined_favorites, summary_b])
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])
        return float(sim[0][0])
    except ValueError:
        return 0.0


def _network_similarity(networks_a, network_b):
    """Binary match: 1.0 if candidate network matches any favorite's network."""
    if not network_b:
        return 0.0
    return 1.0 if network_b in networks_a else 0.0


def _rating_similarity(ratings_a, rating_b):
    """Normalized distance between average of favorite ratings and candidate."""
    valid_ratings = [r for r in ratings_a if r is not None]
    if not valid_ratings or rating_b is None:
        return 0.5  # neutral when data missing
    avg_rating = sum(valid_ratings) / len(valid_ratings)
    return 1.0 - abs(avg_rating - rating_b) / 10.0


def compute_similarity(favorite_shows, candidate_show):
    """Compute weighted similarity score between favorites and a candidate show."""
    fav_genres = [g for show in favorite_shows for g in show.get("genres", [])]
    fav_summaries = [show.get("summary", "") for show in favorite_shows]
    fav_networks = {show.get("network") for show in favorite_shows if show.get("network")}
    fav_ratings = [show.get("rating") for show in favorite_shows]

    genre_score = _genre_similarity(fav_genres, candidate_show.get("genres", []))
    text_score = _text_similarity(fav_summaries, candidate_show.get("summary", ""))
    network_score = _network_similarity(fav_networks, candidate_show.get("network"))
    rating_score = _rating_similarity(fav_ratings, candidate_show.get("rating"))

    total = (
        GENRE_WEIGHT * genre_score
        + TEXT_WEIGHT * text_score
        + NETWORK_WEIGHT * network_score
        + RATING_WEIGHT * rating_score
    )
    return round(total, 4)


def _shared_genres(favorite_shows, candidate_show):
    """Find genres shared between favorites and a candidate."""
    fav_genres = set()
    for show in favorite_shows:
        fav_genres.update(show.get("genres", []))
    return sorted(fav_genres & set(candidate_show.get("genres", [])))


def get_recommendations(favorite_shows, num_results=20):
    """Get show recommendations based on favorite shows.

    Strategy: search TVmaze for each genre keyword from favorites,
    build a candidate pool, score all candidates, return top N.
    """
    favorite_ids = {show["id"] for show in favorite_shows}

    # Collect unique genre keywords from favorites
    genre_keywords = set()
    for show in favorite_shows:
        genre_keywords.update(show.get("genres", []))

    # Also search by favorite show names to find similar shows
    search_terms = list(genre_keywords)
    for show in favorite_shows:
        # Use first word of show name as additional search term
        name_parts = show.get("name", "").split()
        if name_parts:
            search_terms.append(name_parts[0])

    # Build candidate pool
    candidates = {}
    for term in search_terms:
        try:
            results = search_shows(term)
            for show in results:
                if show["id"] not in favorite_ids and show["id"] not in candidates:
                    candidates[show["id"]] = show
        except Exception:
            continue

    # Score all candidates
    scored = []
    for candidate in candidates.values():
        score = compute_similarity(favorite_shows, candidate)
        shared = _shared_genres(favorite_shows, candidate)
        scored.append({
            **candidate,
            "score": score,
            "shared_genres": shared,
        })

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:num_results]
