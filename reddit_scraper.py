import praw
import json
from datetime import datetime, timedelta
import config

# Initialize Reddit API credentials
reddit = praw.Reddit(
    client_id=config.REDDIT_CLIENT_ID,
    client_secret=config.REDDIT_CLIENT_SECRET,
    user_agent=config.REDDIT_USER_AGENT
)

def scrape_top_posts(subreddit_name, time_filter="week", limit=100):
    """
    Scrapes top posts from a given subreddit for the specified time filter.
    
    Parameters:
        subreddit_name (str): Name of the subreddit.
        time_filter (str): Time filter for top posts ('day', 'week', 'month', etc.).
        limit (int): Maximum number of posts to retrieve.
    
    Returns:
        list: A list of dictionaries containing post data.
    """
    subreddit = reddit.subreddit(subreddit_name)
    posts_data = []
    
    # Using .top() with the time filter "week" will get top posts of the past week
    for submission in subreddit.top(time_filter=time_filter, limit=limit):
        posts_data.append({
            'id': submission.id,
            'title': submission.title,
            'description': submission.selftext,
            'upvotes': submission.score,
            'num_comments': submission.num_comments,
            'created_utc': submission.created_utc,
            'url': submission.url
        })
    return posts_data

def main():
    # Define the subreddits to scrape
    subreddits = ["Entrepreneur", "smallbusiness", "ArtificialIntelligence"]
    all_data = {}
    
    for sub in subreddits:
        print(f"Scraping top posts from r/{sub}...")
        posts = scrape_top_posts(sub, time_filter="week", limit=100)
        all_data[sub] = posts
    
    # Save the scraped data to a JSON file
    output_file = "reddit_top_posts.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4)
    
    print(f"Data successfully saved to {output_file}")

if __name__ == "__main__":
    main()
