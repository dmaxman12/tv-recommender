import sys
import os

# Ensure the tv_recommender package directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify

from tvmaze import search_shows, get_show
from recommender import get_recommendations

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])
    try:
        results = search_shows(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    data = request.get_json()
    show_ids = data.get("show_ids", [])
    if not show_ids:
        return jsonify({"error": "No shows provided"}), 400

    # Fetch full details for each favorite
    favorite_shows = []
    for sid in show_ids:
        try:
            show = get_show(sid)
            favorite_shows.append(show)
        except Exception:
            continue

    if not favorite_shows:
        return jsonify({"error": "Could not fetch show details"}), 500

    try:
        recommendations = get_recommendations(favorite_shows)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5050)
