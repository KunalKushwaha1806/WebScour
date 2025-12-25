# 🕷️ WebScour – Web Crawler Using Python

WebScour is a **Python-based web crawler** developed as part of my **Infosys Virtual Internship Program**.  
The project focuses on **automated information discovery**, **web page collection**, and building a strong foundation for a **search engine pipeline**.

---

## 📌 Project Overview

The internet contains a massive amount of information, making manual data collection inefficient and impractical.  
WebScour solves this problem by **automatically discovering, crawling, and storing web pages** starting from a given seed URL.

The crawler follows a **FIFO (queue-based) approach**, avoids duplicate visits, filters invalid links, restricts crawling to the same domain, and stores downloaded pages locally for further processing and searching.

---

## ❓ What Problem Does WebScour Solve?

### Challenges on the Web
- Huge amount of information available online
- Manual discovery and collection of pages is time-consuming
- Difficulty in organizing and searching collected data

### WebScour Solution
WebScour automates this process by:
- Crawling selected websites
- Collecting and storing page content
- Preparing data for indexing and searching

---

## 🔍 Web Crawling Pipeline

WebScour is designed based on the standard **search engine workflow**:

**Crawling → Collecting → Indexing → Searching**

### 1️⃣ Crawling
- Starts from a **seed URL**
- Downloads the web page
- Extracts hyperlinks
- Discovers new pages recursively
- Avoids duplicate URLs
- Restricts crawling to the same domain

### 2️⃣ Collecting
- Stores downloaded HTML pages locally
- Creates a structured dataset for future processing

### 3️⃣ Indexing *(Future Scope)*
- Organizes collected content
- Builds keyword-based indexes for fast searching

### 4️⃣ Searching *(Future Scope)*
- Allows users to search indexed content
- Forms the final layer of a search engine

**Current Implementation Status:**
- ✔ Crawling
- ✔ Collecting
- ❌ Indexing (future enhancement)
- ❌ Searching (future enhancement)

---

## 🎯 Main Focus of the Web Crawler

The WebScour crawler primarily focuses on:

### 🔹 Information Discovery
Automatically finding new web pages through hyperlinks.

### 🔹 Automation
Removing manual effort by automatically fetching, filtering, and storing pages.

### 🔹 Search Enablement
Preparing clean and structured data that can later be indexed and searched.

---

## 🏗️ System Architecture

The architecture of WebScour follows real-world search engine design:

**Seed URL --> Web Crawler --> Page Storage --> Indexer -->Search Engine**

### Component Description

**Seed URL**  
The starting point of the crawl that defines the scope.

**Web Crawler**  
- Fetches web pages
- Handles retries on failure
- Extracts and filters links
- Avoids duplicate crawling
- Enforces same-domain restriction

**Page Storage**  
- Saves HTML pages locally
- Maintains crawled data for analysis

**Indexer (Future Scope)**  
- Converts pages into searchable data

**Search Engine (Future Scope)**  
- Provides keyword-based search functionality

---

## 🧰 Tech Stack – Python Focused

### Programming Language
- Python 3

### Core Python Concepts Used
- Functions and modules
- Data structures:
  - `list` (queue)
  - `set` (visited URLs)
- File handling
- Exception handling
- Retry logic

### Libraries and Tools
- **Requests** – HTTP requests
- **BeautifulSoup** – HTML parsing
- **OS module** – file and directory handling
- **Time module** – delays and performance tracking
- **urllib.parse** – URL normalization and domain extraction

---

## ⚙️ How the Crawler Works

1. Initialize a queue with a seed URL  
2. Fetch the webpage content  
3. Save the HTML page locally  
4. Extract valid HTTP/HTTPS links  
5. Filter invalid links (`mailto`, `javascript`, `tel`, `#`)  
6. Restrict crawling to the same domain  
7. Avoid duplicate URLs using a visited set  
8. Retry failed requests (limited attempts)  
9. Repeat until the maximum page limit is reached  

---

## ✨ Features Implemented

- FIFO queue-based crawling
- Same-domain crawling only
- Duplicate URL prevention
- Invalid link filtering
- Retry logic for failed URLs
- Politeness delay (0.5 seconds)
- Local storage of HTML pages
- Performance measurement (time & average speed)
- Logging of visited URLs

---

### Component Description

- **Seed URL** – Starting point of the crawl  
- **Web Crawler** – Fetches pages, extracts links, filters URLs, avoids duplicates  
- **Page Storage** – Stores HTML pages locally  
- **Indexer** *(Future)* – Builds searchable indexes  
- **Search Engine** *(Future)* – Provides query-based search  

---

## 🧰 Tech Stack

- **Language**: Python 3  
- **Libraries**:
  - Requests (HTTP requests)
  - BeautifulSoup (HTML parsing)
  - OS (file handling)
  - Time (delay and performance)
  - urllib.parse (URL handling)

---

## ⚙️ How the Crawler Works

1. Initialize queue with seed URL  
2. Fetch webpage content  
3. Save HTML locally  
4. Extract valid HTTP/HTTPS links  
5. Filter invalid links (`mailto`, `javascript`, `tel`, `#`)  
6. Restrict crawling to same domain  
7. Avoid duplicate URLs  
8. Retry failed requests  
9. Stop when page limit is reached  

---

## ✨ Features Implemented

- FIFO queue-based crawling  
- Same-domain crawling only  
- Duplicate URL prevention  
- Invalid link filtering  
- Retry logic for failed URLs  
- Politeness delay (0.5 seconds)  
- Local storage of pages  
- Performance measurement  
- Visited URL logging  

---

## 📁 Project Structure

The WebScour project follows a simple and well-organized directory structure.

```bash
webscour/
├── crawler.py          # Main Python script that implements the web crawler
├── pages/              # Directory containing downloaded HTML pages
│   ├── page_1.html     # Crawled webpage (example)
│   ├── page_2.html
│   └── ...
├── visited.txt         # Text file storing all visited URLs
└── README.md           # Project documentation
```

### Description

- **crawler.py** – Contains the complete crawler logic  
- **pages/** – Stores downloaded web pages  
- **visited.txt** – Maintains record of visited URLs  
- **README.md** – Explains the project  

---

## ▶️ How to Run the Project

### Step 1: Install Dependencies
```bash
pip install requests beautifulsoup4
```
Step 2: Run the Crawler
```bash
python crawler.py
```
# WebScour – Web Crawler Using Python

A simple yet efficient web crawler built with Python that downloads web pages, extracts links, and stores them systematically.

## ⚙️ Configuration

The behavior of the WebScour crawler can be customized by modifying the following variables in the `crawler.py` file.

### 🔗 Seed URL
Defines the starting point of the crawl.

```python
seed_url = "https://en.wikipedia.org/wiki/Infosys"
```

### 📄 Maximum Pages
Controls how many pages the crawler is allowed to download.

```python
MAX_PAGES = 5
```

This limit helps prevent excessive crawling and avoids overloading target websites.

### ⏳ Politeness Delay
A delay of 0.5 seconds is applied between successive HTTP requests to reduce server load and promote ethical crawling. This value can be adjusted if required.

## 📊 Output

After execution, the crawler generates the following outputs:

### 🗂 Downloaded Pages
- All successfully crawled HTML pages are stored in the `pages/` directory
- Each page is saved with a unique filename (e.g., `page_1.html`, `page_2.html`)

### 🧾 Visited URLs File
- All unique URLs visited during the crawl are stored in `visited.txt`
- This file helps verify duplicate prevention and crawl coverage

### 💻 Console Output
The terminal displays important crawling statistics, including:
- Total number of pages crawled
- Number of duplicate links encountered
- Total crawling time
- Average time taken per page

## ⚠️ Limitations

Although WebScour works efficiently for small to medium-sized websites, it has the following limitations:
- Crawls only static HTML pages
- Does not execute JavaScript
- Uses a single-threaded crawling approach
- Does not currently respect `robots.txt`
- Not suitable for very large-scale web crawling

## 🚀 Future Enhancements

The project can be extended with the following features:
- Implement multi-threaded crawling for better performance
- Add `robots.txt` compliance for ethical crawling
- Introduce depth-based crawling control
- Store crawled data in a database
- Implement indexing of collected pages
- Build a keyword-based search engine
- Create a web interface using Flask or similar frameworks

## 🎓 Learning Outcomes

Through this project, the following concepts were learned and applied:
- Web crawler architecture and workflow
- Search engine pipeline (crawling → collecting → indexing → searching)
- Use of Python data structures such as queues and sets
- Handling HTTP requests and responses
- Parsing HTML using BeautifulSoup
- Error handling and retry mechanisms
- File and directory management
- Writing clean, maintainable, and well-documented code

## 🧾 Internship Information

- **Program:** Infosys Virtual Internship
- **Project Title:** WebScour – Web Crawler Using Python
- **Domain:** Python / Web Technologies
- **Author:** Kunal Kushwaha

## 📚 References

- [Python Official Documentation](https://docs.python.org/)
- [Requests Library Documentation](https://requests.readthedocs.io/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- Wikipedia (used for testing purposes)




