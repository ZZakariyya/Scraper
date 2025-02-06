import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import random

class IndieHackersScraper:
    def __init__(self):
        self.base_url = "https://www.indiehackers.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.categories = ["milestones", "ideas", "revenue"]
        
    def get_page(self, url):
        """Fetch page with exponential backoff"""
        max_retries = 3
        for i in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                time.sleep(random.uniform(2, 4))  # Respectful rate limiting
                return response.text
            except requests.RequestException as e:
                if i == max_retries - 1:
                    print(f"Failed to fetch {url}: {e}")
                    return None
                time.sleep(2 ** i)  # Exponential backoff
    
    def parse_post(self, post_url):
        """Extract data from a single post"""
        html = self.get_page(self.base_url + post_url)
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract post content
        post_data = {
            'url': post_url,
            'title': '',
            'content': '',
            'author': '',
            'date': '',
            'engagement': {
                'upvotes': 0,
                'comments': 0
            },
            'comments': []
        }
        
        # Get post title
        title_elem = soup.find('h1', class_='post-title')
        if title_elem:
            post_data['title'] = title_elem.get_text().strip()
            
        # Get post content
        content_elem = soup.find('div', class_='post-content')
        if content_elem:
            post_data['content'] = content_elem.get_text().strip()
            
        # Get comments
        comments = soup.find_all('div', class_='comment')
        for comment in comments:
            comment_data = {
                'text': comment.get_text().strip(),
                'author': '',
                'upvotes': 0
            }
            author_elem = comment.find('a', class_='comment-author')
            if author_elem:
                comment_data['author'] = author_elem.get_text().strip()
            
            post_data['comments'].append(comment_data)
            
        return post_data
    
    def scrape_category(self, category, num_pages=5):
        """Scrape posts from a specific category"""
        posts = []
        
        for page in range(1, num_pages + 1):
            url = f"{self.base_url}/categories/{category}?page={page}"
            html = self.get_page(url)
            if not html:
                continue
                
            soup = BeautifulSoup(html, 'html.parser')
            post_links = soup.find_all('a', class_='post-link')
            
            for link in post_links:
                post_url = link.get('href')
                if post_url:
                    post_data = self.parse_post(post_url)
                    if post_data:
                        posts.append(post_data)
                        
        return posts
    
    def analyze_themes(self, posts):
        """Basic theme analysis from posts"""
        themes = {
            'common_words': {},
            'frustrations': [],
            'successes': []
        }
        
        # Simple keyword-based analysis
        frustration_keywords = ['challenge', 'problem', 'struggle', 'difficult']
        success_keywords = ['achieved', 'launched', 'milestone', 'revenue']
        
        for post in posts:
            content = (post['title'] + ' ' + post['content']).lower()
            
            # Analyze for frustrations
            for keyword in frustration_keywords:
                if keyword in content:
                    themes['frustrations'].append({
                        'post_title': post['title'],
                        'keyword': keyword
                    })
                    
            # Analyze for successes
            for keyword in success_keywords:
                if keyword in content:
                    themes['successes'].append({
                        'post_title': post['title'],
                        'keyword': keyword
                    })
                    
        return themes
    
    def run(self):
        """Main execution method"""
        all_data = {}
        
        for category in self.categories:
            print(f"Scraping {category}...")
            posts = self.scrape_category(category)
            themes = self.analyze_themes(posts)
            
            all_data[category] = {
                'posts': posts,
                'themes': themes
            }
            
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'indiehackers_data_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2)
            
        print(f"Data saved to {filename}")

if __name__ == "__main__":
    scraper = IndieHackersScraper()
    scraper.run()