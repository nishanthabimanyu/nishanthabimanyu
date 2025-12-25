import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re
import os

# Configuration
RSS_FEED_URL = "https://medium.com/feed/@nishanthabimanyu001"
README_FILE = "README.md"
MAX_POSTS = 5

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
    
    # Find the first image
    img_tag = soup.find('img')
    img_url = img_tag['src'] if img_tag else "https://cdn-images-1.medium.com/max/1024/1*App_41JJbfT7xR2Vj-rR9A.png" # Default fallback image
    
    # Extract text snippet
    text = soup.get_text(separator=' ')
    # Clean up text
    text = re.sub(r'\s+', ' ', text).strip()
    snippet = text[:150] + "..." if len(text) > 150 else text
    
    return img_url, snippet

def generate_markdown_cards(posts):
    markdown_output = "<table>\n"
    
    for post in posts:
        title = post['title']
        link = post['link']
        img_url = post['img_url']
        snippet = post['snippet']
        
        # Create a table row for each post (Image Left, Content Right)
        markdown_output += f"""  <tr>
    <td width="30%">
      <a href="{link}">
        <img src="{img_url}" alt="{title}" width="100%">
      </a>
    </td>
    <td>
      <h3><a href="{link}">{title}</a></h3>
      <p>{snippet}</p>
    </td>
  </tr>
"""
    
    markdown_output += "</table>\n"
    return markdown_output

def update_readme(new_content):
    try:
        with open(README_FILE, 'r', encoding='utf-8') as file:
            readme_content = file.read()
        
        # Regex to find the block between markers
        pattern = r"(<!-- MEDIUM:START -->)(.*?)(<!-- MEDIUM:END -->)"
        
        # Check if markers exist
        if not re.search(pattern, readme_content, re.DOTALL):
            print("Markers not found in README.md. Please add <!-- MEDIUM:START --> and <!-- MEDIUM:END -->")
            return

        # Replace content
        updated_content = re.sub(
            pattern,
            f"\\1\n{new_content}\n\\3",
            readme_content,
            flags=re.DOTALL
        )
        
        with open(README_FILE, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        
        print("README.md updated successfully.")
        
    except Exception as e:
        print(f"Error updating README.md: {e}")

def main():
    rss_content = fetch_rss_feed()
    if not rss_content:
        return

    root = ET.fromstring(rss_content)
    posts = []
    
    # Define namespaces
    namespaces = {
        'content': 'http://purl.org/rss/1.0/modules/content/'
    }

    for item in root.findall(".//item")[:MAX_POSTS]:
        title = item.find("title").text
        link = item.find("link").text
        
        # Get content:encoded
        content_encoded = item.find("content:encoded", namespaces)
        if content_encoded is not None:
            html_content = content_encoded.text
        else:
            html_content = item.find("description").text or ""
            
        img_url, snippet = extract_image_and_snippet(html_content)
        
        posts.append({
            'title': title,
            'link': link,
            'img_url': img_url,
            'snippet': snippet
        })
    
    if posts:
        markdown_html = generate_markdown_cards(posts)
        update_readme(markdown_html)
    else:
        print("No posts found.")

if __name__ == "__main__":
    main()
