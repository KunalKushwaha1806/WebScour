'''
Pseudo code 
START

1. Initialize:
      queue = [seed_url]
      visited = empty_set
      page_id = 1

2. WHILE queue is not empty AND pages_crawled < MAX_PAGES:

      a. Take the next URL from queue (FIFO)
      
      b. IF URL is already in visited:
             skip this URL and continue
      
      c. Fetch the HTML for the URL
             IF fetching failed:
                 skip and continue
      
      d. Save the HTML content to a file:
             filename = "page_<page_id>.html"
      
      e. Extract all links from the HTML content
      
      f. FOR each extracted link:
             IF link NOT in visited AND NOT already in queue:
                   add link to queue
      
      g. Mark current URL as visited
      
      h. Increment page_id by 1
      
      i. Sleep for 0.5 seconds (to avoid server overload)

3. END WHILE

4. Print the total number of pages crawled

END

'''


'''
Explaination:

1. Start with one URL
Put the seed URL into a queue.
Create an empty visited set.
Set page_id = 1.

2. Loop while you still have pages to crawl
Take the first URL from the queue.
If you already visited it → skip.

3. Fetch the page
Download the HTML.
If download fails → skip.

4. Save the HTML
Store the HTML into a file like:
page_1.html, page_2.html, etc.

5. Extract links
Get all <a href="..."> links from the HTML.

6. Add new links to the queue
Only add links that:
are not visited
not already in the queue

7. Mark visited
Add the current URL to visited.

8. Increase counters
page_id = page_id + 1
Sleep 0.5 seconds so you don't overload websites.

9. After loop ends
Print how many pages you crawled.

'''
import requests 
from bs4 import BeautifulSoup
import time
import os 
from urllib.parse import urljoin, urlparse, urldefrag


def fetch_page(url, max_retries=3): # takes url and max retries as input(this is additional parameter to control retries)
    """
    Tries to download the webpage at the given URL.
    Retries a few times if there is a temporary error (network, timeout, etc.).
    Returns the HTML text if successful, otherwise returns None.
    """
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[INFO] Fetching (attempt {attempt}/{max_retries}):{url}") # logging the attempt number
            response = requests.get(
                url,
                timeout=5,
                headers={"User-Agent": "WebScourCrawler/1.0"}
            )

            if response.status_code == 200:
                return response.text
            else:
                # For non-200 codes we don't retry (here we just report)
                print(f"[ERROR] Status {response.status_code} for {url}") # As these are client/server errors, no point in retrying  
                return None

        except Exception as error:
            print(f"[ERROR] Problem while fetching {url}: {error}") # passing the error message before retrying , if possible 

            # If this was the last attempt, give up
            if attempt == max_retries:
                print(f"[ERROR] Giving up on {url} after {max_retries} attempts.")
                return None

            # Small delay before next retry
            time.sleep(1)

    

def extract_links(html, base_url):
    """
    Extract only useful HTTP/HTTPS links from the page.
    Skips: mailto:, javascript:, tel:, #section, etc.
    """
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()

        # 1. Skip obviously useless hrefs
        if not href:
            continue
        if href.startswith("#"):
            continue
        if href.startswith("mailto:"):
            continue
        if href.startswith("javascript:"):
            continue
        if href.startswith("tel:"):
            continue

        # 2. Make absolute URL
        absolute = urljoin(base_url, href)   

        # 3. Remove fragment (#section)
        absolute, _ = urldefrag(absolute)  

        # 4. Keep only http/https   ---> url have scheme , domain, path 
        parsed = urlparse(absolute)
        if parsed.scheme not in ("http", "https"): # skips ftp://, file://, data:// etc.
            continue

        links.add(absolute)

    return links


def main():
    seed_url = "https://en.wikipedia.org/wiki/Infosys"
    MAX_PAGES = 50


    # This basically gets the domain from the seed URL for reference 
    # e.g., for "https://en.wikipedia.org/xyz", it gets "en.wikipedia.org"
    # We can use this to restrict crawling to the same domain if needed.
    seed_domain = urlparse(seed_url).netloc
    print(f"[INFO] Seed domain: {seed_domain}")

    folder_name = "pages"
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    queue = [seed_url]
    visited = set()
    page_id = 1
    pages_crawled = 0

    duplicate_count = 0   # SIMPLE duplicate counter
    start_time = time.time()

    while queue and pages_crawled < MAX_PAGES:

        url = queue.pop(0)

        # b. Check for duplicates
        if url in visited:
            duplicate_count += 1   #COUNT DUPLICATE HERE
            continue

        # c. Fetch page
        html = fetch_page(url)
        if html is None:
            continue

        # d. Save HTML
        filename = os.path.join(folder_name, f"page_{page_id}.html")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[SAVED] {url} --> {filename}")

        # e. Extract links
        links = extract_links(html, url)

        # f. Add new links to queue
        for link in links:
            link_domain = urlparse(link).netloc # This gets the domain of the link
            if link_domain != seed_domain: # Restrict to same domain
                continue
            if link not in visited and link not in queue:
                queue.append(link)

        # g. Mark visited
        visited.add(url)

        # h. Update counters
        page_id += 1
        pages_crawled += 1

        time.sleep(0.5)

    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / pages_crawled if pages_crawled > 0 else 0

    print("\n--- SUMMARY ---")
    print("Total pages crawled:", pages_crawled)
    print("Duplicate links encountered:", duplicate_count)
    print(f"Total time: {total_time:.2f} sec")
    print(f"Average time per page: {avg_time:.2f} sec")
    
    # Save visited URLs to a file
    visited_file = "visited.txt"
    with open(visited_file, "w", encoding="utf-8") as f:
        for v in sorted(visited):
            f.write(v + "\n")
    print(f"[INFO] Saved visited URLs to {visited_file}")


if __name__ == "__main__":
    main()
    

