import requests
import pika
from bs4 import BeautifulSoup
import time
import os
import multiprocessing
from multiprocessing import Lock
from urllib.parse import urljoin, urlparse, urldefrag
import signal
import sys
import uuid   # ✅ ADDED for unique filenames

# -------------------------------
# GLOBAL CONFIG
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE_NAME = "url_queue"
PAGES_DIR = os.path.join(BASE_DIR, "pages")
VISITED_FILE = os.path.join(BASE_DIR, "visited.txt")
FOLDER_NAME = PAGES_DIR

file_lock = Lock()
print_lock = Lock()

# -------------------------------
# SETUP STORAGE
# -------------------------------
if not os.path.exists(FOLDER_NAME):
    os.mkdir(FOLDER_NAME)

if not os.path.exists(VISITED_FILE):
    open(VISITED_FILE, "w").close()

# -------------------------------
# VISITED FILE HELPERS
# -------------------------------
def is_visited(url):
    with file_lock:
        with open(VISITED_FILE, "r", encoding="utf-8") as f:
            return url in f.read().splitlines()

def mark_visited(url):
    with file_lock:
        with open(VISITED_FILE, "a", encoding="utf-8") as f:
            f.write(url + "\n")

# -------------------------------
# FETCH PAGE
# -------------------------------
def fetch_page(url, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url,
                timeout=5,
                headers={"User-Agent": "WebScourCrawler/1.0"}
            )
            if response.status_code == 200:
                response.encoding = response.apparent_encoding
                return response.text

        except Exception:
            if attempt == max_retries:
                return None
            time.sleep(1)
    return None

# -------------------------------
# EXTRACT LINKS
# -------------------------------
def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()

        if not href:
            continue
        if href.startswith(("#", "mailto:", "javascript:", "tel:")):
            continue

        absolute = urljoin(base_url, href)
        absolute, _ = urldefrag(absolute)

        parsed = urlparse(absolute)
        if parsed.scheme not in ("http", "https"):
            continue

        links.add(absolute)

    return links

# -------------------------------
# WORKER PROCESS
# -------------------------------
def worker_process(worker_id):
    pages_crawled = 0
    start_time = time.time()
    connection = None
    channel = None

    def print_summary():
        with print_lock:
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / pages_crawled if pages_crawled else 0

            print(f"\n--- WORKER-{worker_id} SUMMARY ---")
            print(f"Pages crawled: {pages_crawled}")
            print(f"Total time: {total_time:.2f} sec")
            print(f"Average time per page: {avg_time:.2f} sec")

    def handle_interrupt(sig, frame):
        print(f"\n[WORKER-{worker_id}] Stopping gracefully...")
        print_summary()

        if channel and channel.is_open:
            channel.stop_consuming()
        if connection and connection.is_open:
            connection.close()

        sys.exit(0)

    signal.signal(signal.SIGINT, handle_interrupt)

    def callback(ch, method, properties, body):
        nonlocal pages_crawled

        url = body.decode()
        print(f"[WORKER-{worker_id}] Crawling: {url}")

        if is_visited(url):
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        html = fetch_page(url)
        if html is None:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return

        pages_crawled += 1
        filename = f"{uuid.uuid4().hex}.html"
        filepath = os.path.join(FOLDER_NAME, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"[WORKER-{worker_id}] Saved → {filename}")

        links = extract_links(html, url)
        domain = urlparse(url).netloc

        for link in links:
            if urlparse(link).netloc == domain and not is_visited(link):
                ch.basic_publish(
                    exchange="",
                    routing_key=QUEUE_NAME,
                    body=link.encode()
                )

        mark_visited(url)
        time.sleep(0.5)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # -------------------------------
    # RABBITMQ CONNECTION
    # -------------------------------
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print(f"[*] Worker-{worker_id} started")
    channel.start_consuming()

# -------------------------------
# START MULTIPLE WORKERS
# -------------------------------
def start_workers(num_workers=3):
    processes = []

    print("\n--- TASK 10: PERFORMANCE CONFIG ---")
    print(f"Number of workers: {num_workers}\n")

    for i in range(num_workers):
        p = multiprocessing.Process(
            target=worker_process,
            args=(i + 1,)
        )
        p.start()
        processes.append(p)

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\n[MAIN] Stopping all workers gracefully...")
        for p in processes:
            if p.is_alive():
                p.terminate()
        for p in processes:
            p.join()
        print("[MAIN] All workers stopped cleanly.")

# -------------------------------
# ENTRY POINT
# -------------------------------
if __name__ == "__main__":
    start_workers(3)
