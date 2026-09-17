from flask import Flask, render_template, request, abort, send_from_directory
import json
import string
import os
import time
import re
from bs4 import BeautifulSoup

# -----------------------------
# CONFIGURATION & DATA LOADING
# -----------------------------

# Detect Vercel environment
IS_VERCEL = os.environ.get("VERCEL") == "1"

if IS_VERCEL:
    # On Vercel, the project root is set by api/index.py
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
else:
    # Local development: app.py is inside search_app/
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INDEXER_DIR = os.path.join(BASE_DIR, "indexer")
PAGES_DIR = os.path.join(BASE_DIR, "pages")

# Configure Flask with explicit template and static paths
TEMPLATE_DIR = os.path.join(BASE_DIR, "search_app", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "search_app", "static")

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR,
    static_url_path="/static"
)

# Stopwords set matching indexer
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", 
    "by", "can", "cannot", "could", "did", "do", "does", "doing", "down", "during", "each", 
    "few", "for", "from", "further", "had", "has", "have", "having", "he", "her", "here", 
    "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", 
    "its", "itself", "just", "me", "more", "most", "my", "myself", "no", "nor", "not", "of", 
    "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", 
    "over", "own", "same", "she", "should", "so", "some", "such", "than", "that", "the", 
    "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this", 
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "we", "were", 
    "what", "when", "where", "which", "while", "who", "whom", "why", "with", "would", 
    "you", "your", "yours", "yourself", "yourselves"
}

def load_json_file(filename, default):
    filepath = os.path.join(INDEXER_DIR, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Could not load {filename}: {e}")
    return default

inverted_index = load_json_file("inverted_index.json", {})
idf = load_json_file("idf.json", {})
metadata = load_json_file("metadata.json", {})


# -----------------------------
# TOKENIZER
# -----------------------------
def tokenize(text, filter_stopwords=True):
    if not text:
        return []
    text = text.lower()
    translator = str.maketrans(string.punctuation, " " * len(string.punctuation))
    text = text.translate(translator)
    tokens = text.split()
    if filter_stopwords:
        filtered = [t for t in tokens if len(t) > 1 and t not in STOPWORDS]
        return filtered if filtered else [t for t in tokens if len(t) > 1]
    return [t for t in tokens if len(t) > 1]


# -----------------------------
# SNIPPET GENERATOR & HIGHLIGHTING
# -----------------------------
def highlight_terms(text, terms):
    """
    Wraps matching terms in <mark> tags safely for rendering in the UI.
    """
    if not text or not terms:
        return text

    # Sort terms by length descending to match longer phrases first
    sorted_terms = sorted(set(t for t in terms if len(t) > 1), key=len, reverse=True)
    if not sorted_terms:
        return text

    pattern = re.compile(r"(\b(?:%s)\b)" % "|".join(map(re.escape, sorted_terms)), re.IGNORECASE)
    return pattern.sub(r"<mark>\1</mark>", text)


def get_snippet_for_doc(doc_id, query_tokens):
    """
    Generates a snippet context around matching query tokens.
    """
    doc_info = metadata.get(doc_id, {})
    base_snippet = doc_info.get("snippet", "")

    # Try to load actual page text if available to get the best matching sentence
    page_path = os.path.join(PAGES_DIR, doc_id)
    if os.path.exists(page_path) and query_tokens:
        try:
            with open(page_path, "r", encoding="utf-8", errors="ignore") as f:
                html = f.read(50000)  # Read first 50KB for speed
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            
            paragraphs = soup.find_all("p")
            best_p = ""
            best_match_count = 0
            for p in paragraphs:
                p_text = p.get_text(strip=True)
                if len(p_text) < 40:
                    continue
                p_lower = p_text.lower()
                matches = sum(1 for token in query_tokens if token in p_lower)
                if matches > best_match_count:
                    best_match_count = matches
                    best_p = p_text
                    if matches == len(query_tokens):
                        break
            if best_p:
                base_snippet = best_p[:260] + ("..." if len(best_p) > 260 else "")
        except Exception:
            pass

    return highlight_terms(base_snippet, query_tokens)


# -----------------------------
# TF-IDF SEARCH LOGIC
# -----------------------------
def search(query, top_k=10):
    if not query or not query.strip():
        return [], 0.0

    start_time = time.perf_counter()
    scores = {}
    query_tokens = tokenize(query, filter_stopwords=True)

    if not query_tokens:
        query_tokens = tokenize(query, filter_stopwords=False)

    for word in query_tokens:
        if word not in inverted_index:
            continue

        word_idf = idf.get(word, 1.0)

        for doc_id, tf in inverted_index[word]:
            # Standard TF-IDF score: tf * idf
            score = tf * word_idf

            # Title matching boost: prioritize documents where query terms appear in the title
            doc_meta = metadata.get(doc_id, {})
            title_lower = doc_meta.get("title", "").lower()
            if word in title_lower:
                score *= 2.5

            scores[doc_id] = scores.get(doc_id, 0.0) + score

    # Sort results descending by score
    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    results = []
    for doc_id, score in sorted_docs:
        meta = metadata.get(doc_id, {
            "title": doc_id,
            "full_title": doc_id,
            "url": "#",
            "snippet": "",
            "doc_id": doc_id
        })

        snippet = get_snippet_for_doc(doc_id, query_tokens)

        results.append({
            "doc_id": doc_id,
            "title": meta.get("title") or doc_id,
            "full_title": meta.get("full_title") or doc_id,
            "url": meta.get("url") or "#",
            "snippet": snippet,
            "score": round(score, 2),
            "word_count": meta.get("word_count", 0)
        })

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    return results, round(elapsed_ms, 2)


# -----------------------------
# ROUTES
# -----------------------------
@app.route("/", methods=["GET", "POST"])
@app.route("/api", methods=["GET", "POST"])
@app.route("/api/", methods=["GET", "POST"])
@app.route("/api/index", methods=["GET", "POST"])
@app.route("/api/index.py", methods=["GET", "POST"])
def home():
    query = ""
    results = []
    elapsed_ms = 0.0

    if request.method == "POST":
        query = request.form.get("query", "").strip()
    elif request.method == "GET" and "q" in request.args:
        query = request.args.get("q", "").strip()

    if query:
        results, elapsed_ms = search(query)

    total_indexed_pages = len(metadata) if metadata else len(os.listdir(PAGES_DIR)) if os.path.exists(PAGES_DIR) else 0

    return render_template(
        "index.html",
        query=query,
        results=results,
        elapsed_ms=elapsed_ms,
        total_indexed=total_indexed_pages
    )


@app.route("/view/<path:doc_id>")
@app.route("/api/view/<path:doc_id>")
@app.route("/api/index.py/view/<path:doc_id>")
def view_cached_page(doc_id):
    """
    Safely serves the crawled snapshot HTML file.
    """
    safe_filename = os.path.basename(doc_id)
    if not os.path.exists(os.path.join(PAGES_DIR, safe_filename)):
        abort(404, description="Cached document not found.")
    return send_from_directory(PAGES_DIR, safe_filename)


@app.route("/api/search")
@app.route("/search")
@app.route("/api/index.py/api/search")
def api_search():
    """
    REST API endpoint for programmatic search queries.
    """
    q = request.args.get("q", "").strip()
    k = request.args.get("k", 10, type=int)
    results, elapsed_ms = search(q, top_k=k)
    return {
        "query": q,
        "results_count": len(results),
        "time_ms": elapsed_ms,
        "results": results
    }


@app.route("/favicon.ico")
def favicon():
    return "", 204


@app.route("/static/<path:filename>")
@app.route("/api/static/<path:filename>")
@app.route("/api/index.py/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(STATIC_DIR, filename)


@app.route("/style.css")
def serve_root_style():
    return send_from_directory(STATIC_DIR, "style.css")




# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
