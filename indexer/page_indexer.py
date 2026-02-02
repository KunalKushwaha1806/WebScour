import os
import math
import json
import string
from bs4 import BeautifulSoup

# -----------------------------
# CONFIGURATION
# -----------------------------
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEXER_DIR = os.path.join(BASE_DIR, "indexer")
INDEX_FILE = os.path.join(INDEXER_DIR, "inverted_index.json")
IDF_FILE = os.path.join(INDEXER_DIR, "idf.json")
PAGES_DIR = os.path.join(BASE_DIR, "pages")


# -----------------------------
# STEP 1: PARSE HTML → TEXT
# -----------------------------

def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text(separator=" ")



# -----------------------------
# STEP 2: CLEAN & TOKENIZE
# -----------------------------

def tokenize(text):
    text = text.lower()
    translator = str.maketrans("", "", string.punctuation)
    text = text.translate(translator)
    return [t for t in text.split() if t.strip()]



# -----------------------------
# STEP 3: LOAD DOCUMENTS
# -----------------------------

def load_documents():
    documents = {}

    for root, _, files in os.walk(PAGES_DIR):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    documents[file] = f.read()

    return documents


# -----------------------------
# STEP 4: TERM FREQUENCY (TF)
# -----------------------------

def compute_tf(tokens):
    tf = {}
    for word in tokens:
        tf[word] = tf.get(word, 0) + 1
    return tf


# -----------------------------
# STEP 5: BUILD INVERTED INDEX
# -----------------------------

def build_inverted_index(documents):
    inverted_index = {}

    for doc_id, html in documents.items():
        text = extract_text_from_html(html)
        tokens = tokenize(text)
        tf = compute_tf(tokens)

        for word, freq in tf.items():
            if word not in inverted_index:
                inverted_index[word] = []
            inverted_index[word].append([doc_id, freq])

    return inverted_index


# -----------------------------
# STEP 6: CALCULATE IDF
# -----------------------------

def compute_idf(inverted_index, total_docs):
    idf = {}

    for word, postings in inverted_index.items():
        doc_count = len(postings)
        idf[word] = math.log(total_docs / doc_count)

    return idf


# -----------------------------
# STEP 7: SAVE TO DISK
# -----------------------------

def save_to_disk(inverted_index, idf):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(inverted_index, f, indent=2)

    with open(IDF_FILE, "w", encoding="utf-8") as f:
        json.dump(idf, f, indent=2)


# -----------------------------
# MAIN FUNCTION
# -----------------------------

def main():
    print("[INFO] Loading documents...")
    documents = load_documents()
    total_docs = len(documents)

    print(f"[INFO] Total documents: {total_docs}")

    print("[INFO] Building inverted index...")
    inverted_index = build_inverted_index(documents)

    print("[INFO] Computing IDF...")
    idf = compute_idf(inverted_index, total_docs)

    print("[INFO] Saving index to disk...")
    save_to_disk(inverted_index, idf)

    print("[DONE] Milestone 3 completed successfully!")
    print(f"[OUTPUT] {INDEX_FILE}, {IDF_FILE}")


if __name__ == "__main__":
    main()
