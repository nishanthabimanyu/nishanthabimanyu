import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re
import os

# Configuration
RSS_FEED_URL = "https://medium.com/feed/@nishanthabimanyu001"
README_FILE = "README.md"
MAX_LATEST_POSTS = 5

# Hardcoded Termux Series Data
TERMUX_SERIES_POSTS = [
    {
        "title": "How to Set Up a Local SQL Database on Your Phone Using Termux (No Root Required)",
        "link": "https://medium.com/@nishanthabimanyu001/how-to-set-up-a-local-sql-database-on-your-phone-using-termux-no-root-required-69d2644211f3"
    },
    {
        "title": "Master Linux Without a Laptop — Learn Using Just Your Phone",
        "link": "https://medium.com/@nishanthabimanyu001/master-linux-without-a-laptop-learn-using-just-your-phone-64860b2d6a78"
    },
    {
        "title": "Quick Ways to Locate Your Files & Downloads in Termux",
        "link": "https://medium.com/@nishanthabimanyu001/quick-ways-to-locate-your-files-downloads-in-termux-138374a58b29"
    },
    {
        "title": "Hands-On with Termux — Storage Setup, File Downloads, and File System Exploration",
        "link": "https://medium.com/@nishanthabimanyu001/hands-on-with-termux-storage-setup-file-downloads-and-file-system-exploration-21c60be5508c"
    },
    {
        "title": "How to Fix Termux Update Errors by Changing Mirrors…",
        "link": "https://medium.com/@nishanthabimanyu001/how-to-fix-termux-update-errors-by-changing-mirrors-5311f970e70a"
    },
    {
        "title": "Understanding NFC — Insights and Risks from a Hacker’s Viewpoint",
        "link": "https://medium.com/@nishanthabimanyu001/understanding-nfc-insights-and-risks-from-a-hackers-viewpoint-07cc90df8da3"
    }
]

def fetch_rss_feed():
    try:
        response = requests.get(RSS_FEED_URL)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Error fetching RSS feed: {e}")
        return None

def extract_image_and_snippet(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    img_tag = soup.find('img')
    img_url = img_tag['src'] if img_tag else "https://miro.medium.com/v2/resize:fit:1024/1*App_41JJbfT7xR2Vj-rR9A.png"
    text = soup.get_text(separator=' ')
    text = re.sub(r"\s+", " ", text).strip()
    snippet = text[:150] + "..." if len(text) > 150 else text
    return img_url, snippet

def generate_markdown_cards(posts):
    if not posts: return ""
    markdown_output = "<table>\n"
    for post in posts:
        markdown_output += f"""
  <tr>
    <td width="30%">
      <a href="{post['link']}">
        <img src="{post['img_url']}" alt="{post['title']}" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="{post['link']}">{post['title']}</a></h3>
      <p>{post['snippet']}</p>
    </td>
  </tr>
"""
    markdown_output += "</table>\n"
    return markdown_output

def generate_simple_list(posts):
    if not posts: return ""
    markdown_output = ""
    for post in posts:
        markdown_output += f"- [{post['title']}]({post['link']})\n"
    return markdown_output

def update_section(readme_content, marker_name, new_content):
    pattern = rf"(<!-- {marker_name}:START -->)(.*?)(<!-- {marker_name}:END -->)"
    if not re.search(pattern, readme_content, re.DOTALL):
        return readme_content
    replacement = f"<!-- {marker_name}:START -->\n{new_content}\n<!-- {marker_name}:END -->"
    return re.sub(pattern, replacement, readme_content, flags=re.DOTALL)

def main():
    # 1. Fetch Latest Articles from RSS
    rss_content = fetch_rss_feed()
    latest_posts = []
    if rss_content:
        root = ET.fromstring(rss_content)
        ns = {'content': 'http://purl.org/rss/1.0/modules/content/'}
        for item in root.findall(".//item")[:MAX_LATEST_POSTS]:
            title = item.find("title").text
            link = item.find("link").text
            content_encoded = item.find("content:encoded", ns)
            html = content_encoded.text if content_encoded is not None else ""
            img, snip = extract_image_and_snippet(html)
            latest_posts.append({'title': title, 'link': link, 'img_url': img, 'snippet': snip})

    # 2. Update README
    try:
        with open(README_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = update_section(content, "MEDIUM", generate_markdown_cards(latest_posts))
        content = update_section(content, "TERMUX", generate_simple_list(TERMUX_SERIES_POSTS))
        
        with open(README_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        print("README.md updated successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
