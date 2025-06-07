import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def crawl_website(start_url, max_pages=15):
    visited = set()
    to_visit = [start_url]
    all_data = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue

        try:
            print(f"🔍 Crawling: {url}")
            response = requests.get(url, timeout=10)
            visited.add(url)

            if "text/html" not in response.headers.get("Content-Type", ""):
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            all_data.append({"url": url, "text": text})

            # Extract all links from the page
            for link_tag in soup.find_all("a", href=True):
                href = link_tag['href']
                full_url = urljoin(url, href)

                # Filter internal links only (same domain)
                if urlparse(full_url).netloc == urlparse(start_url).netloc:
                    if full_url not in visited and full_url not in to_visit:
                        to_visit.append(full_url)

        except Exception as e:
            print(f"❌ Failed to crawl {url}: {e}")
            continue

    return all_data


start_url = "https://docs.chaicode.com/youtube/chai-aur-git/branches/"  # Replace with your target site
crawled_data = crawl_website(start_url)

# for page in data:
#     print("\n📄 Page:", page["url"])
#     print("📜 Text preview:", page["text"][:500], "...\n")


print("data collected successfully!")
print("Saving data to PDF...")
from fpdf import FPDF

def clean_text(text):
    # Remove or replace unsupported characters
    return text.encode("latin-1", "replace").decode("latin-1")

def save_to_pdf(crawled_data, output_path="website_data.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for page in crawled_data:
        url = clean_text(f"URL: {page['url']}\n")
        content = clean_text(page['text'])

        pdf.set_font("Arial", style="B", size=12)
        pdf.multi_cell(0, 10, url, align='L')
        pdf.set_font("Arial", style="", size=11)
        pdf.multi_cell(0, 10, content + "\n\n", align='L')

    pdf.output(output_path)
    print(f"✅ PDF saved to: {output_path}")
save_to_pdf(crawled_data, "website_data.pdf")
print("PDF saved successfully!")