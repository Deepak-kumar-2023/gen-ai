import snscrape.modules.twitter as sntwitter
import pandas as pd

# Define the search query and parameters
search_query = "#python -filter:retweets"  # Fetches tweets with #python, excluding retweets
max_tweets = 1  # Number of tweets to fetch

# Create a list to store tweet data
tweet_data = []

# Fetch tweets using TwitterSearchScraper
try:
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(search_query).get_items()):
        if i >= max_tweets:
            break
        tweet_data.append([
            tweet.date,
            tweet.user.username,
            tweet.rawContent,  # Use rawContent for full text
            tweet.user.location or ""
        ])
    print(f"Successfully fetched {len(tweet_data)} tweets.")

except Exception as e:
    print(f"Error fetching tweets: {e}")

# Create a DataFrame with the collected data
columns = ['Created_At', 'User', 'Text', 'Location']
df = pd.DataFrame(tweet_data, columns=columns)

# Save to CSV file
output_file = "tweets_snscrape.csv"
try:
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Tweets saved to {output_file}")
except Exception as e:
    print(f"Error saving to CSV: {e}")