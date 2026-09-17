import os
import math
import json
import string
import re
from bs4 import BeautifulSoup

# -----------------------------
# CONFIGURATION
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEXER_DIR = os.path.join(BASE_DIR, "indexer")
INDEX_FILE = os.path.join(INDEXER_DIR, "inverted_index.json")
IDF_FILE = os.path.join(INDEXER_DIR, "idf.json")
METADATA_FILE = os.path.join(INDEXER_DIR, "metadata.json")
PAGES_DIR = os.path.join(BASE_DIR, "pages")

# Standard English stopwords
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

# -----------------------------
# STEP 1: PARSE HTML & METADATA
# -----------------------------

def extract_page_data(html, doc_id):
    """
    Extracts plain text, page title, canonical URL, and an initial text snippet from HTML.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Extract title
    title_tag = soup.find("title")
    full_title = title_tag.get_text(strip=True) if title_tag else doc_id
    # Clean wikipedia suffix if present for display title
    clean_title = re.sub(r"\s*-\s*Wikipedia$", "", full_title).strip() or doc_id

    # Extract canonical URL
    canonical_tag = soup.find("link", rel="canonical")
    og_url_tag = soup.find("meta", property="og:url")
    url = ""
    if canonical_tag and canonical_tag.get("href"):
        url = canonical_tag["href"]
    elif og_url_tag and og_url_tag.get("content"):
        url = og_url_tag["content"]
    else:
        # Fallback placeholder using title
        slug = clean_title.replace(" ", "_")
        url = f"https://en.wikipedia.org/wiki/{slug}"

    # Remove non-content tags before text extraction
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    # Extract plain text
    text = soup.get_text(separator=" ")
    text = " ".join(text.split())

    # Build concise snippet from the first readable paragraphs
    snippet = ""
    paragraphs = soup.find_all("p")
    for p in paragraphs:
        p_text = p.get_text(strip=True)
        if len(p_text) > 40:
            snippet = p_text[:240] + ("..." if len(p_text) > 240 else "")
            break
    if not snippet and text:
        snippet = text[:200] + ("..." if len(text) > 200 else "")

    metadata = {
        "title": clean_title,
        "full_title": full_title,
        "url": url,
        "snippet": snippet,
        "doc_id": doc_id
    }

    return text, metadata


# -----------------------------
# STEP 2: CLEAN & TOKENIZE
# -----------------------------

def tokenize(text, remove_stopwords=True):
    text = text.lower()
    translator = str.maketrans(string.punctuation, " " * len(string.punctuation))
    text = text.translate(translator)
    tokens = text.split()

    if remove_stopwords:
        tokens = [t for t in tokens if len(t) > 1 and t not in STOPWORDS and not t.isnumeric()]
    else:
        tokens = [t for t in tokens if len(t) > 1]

    return tokens


# -----------------------------
# STEP 3: LOAD DOCUMENTS
# -----------------------------

def load_documents():
    raw_documents = {}

    for root, _, files in os.walk(PAGES_DIR):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        raw_documents[file] = f.read()
                except Exception as e:
                    print(f"[WARN] Error reading {file}: {e}")

    return raw_documents


# -----------------------------
# STEP 4: TERM FREQUENCY (TF)
# -----------------------------

def compute_tf(tokens):
    tf = {}
    for word in tokens:
        tf[word] = tf.get(word, 0) + 1
    return tf


# -----------------------------
# STEP 5: BUILD INVERTED INDEX & METADATA
# -----------------------------

def build_index_and_metadata(documents):
    inverted_index = {}
    metadata_map = {}

    for doc_id, html in documents.items():
        text, meta = extract_page_data(html, doc_id)
        tokens = tokenize(text, remove_stopwords=True)
        meta["word_count"] = len(tokens)
        metadata_map[doc_id] = meta

        tf = compute_tf(tokens)

        for word, freq in tf.items():
            if word not in inverted_index:
                inverted_index[word] = []
            inverted_index[word].append([doc_id, freq])

    return inverted_index, metadata_map


# -----------------------------
# STEP 6: CALCULATE IDF
# -----------------------------

def compute_idf(inverted_index, total_docs):
    idf = {}

    for word, postings in inverted_index.items():
        doc_count = len(postings)
        # Standard smooth IDF formula
        idf[word] = math.log((total_docs + 1) / (doc_count + 1)) + 1.0

    return idf


# -----------------------------
# STEP 7: SAVE TO DISK
# -----------------------------

def save_to_disk(inverted_index, idf, metadata_map):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(inverted_index, f, indent=2)

    with open(IDF_FILE, "w", encoding="utf-8") as f:
        json.dump(idf, f, indent=2)

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata_map, f, indent=2)


# -----------------------------
# MAIN PIPELINE
# -----------------------------

def main():
    print("[INFO] Loading documents from pages/...")
    documents = load_documents()
    total_docs = len(documents)

    print(f"[INFO] Total documents found: {total_docs}")
    if total_docs == 0:
        print("[WARN] No HTML pages found in pages directory.")
        return

    print("[INFO] Building inverted index and extracting metadata...")
    inverted_index, metadata_map = build_index_and_metadata(documents)
    print(f"[INFO] Unique vocabulary terms indexed: {len(inverted_index)}")

    print("[INFO] Computing TF-IDF (smooth IDF)...")
    idf = compute_idf(inverted_index, total_docs)

    print("[INFO] Saving index, IDF, and metadata to disk...")
    save_to_disk(inverted_index, idf, metadata_map)

    print("[DONE] Indexing completed successfully!")
    print(f"[OUTPUT] {INDEX_FILE}")
    print(f"[OUTPUT] {IDF_FILE}")
    print(f"[OUTPUT] {METADATA_FILE}")


if __name__ == "__main__":
    main()
