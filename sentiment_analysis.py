import streamlit as st
import openai
from db_config import get_db_connection
import os
from dotenv import load_dotenv
import pandas as pd
import re
import html
import emoji
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure OpenAI
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize session state
if 'current_username' not in st.session_state:
    st.session_state.current_username = None

def preprocess_tweet(tweet_text):
    """Clean and structure the tweet text for better analysis"""
    if not tweet_text:
        return ""
    
    # Decode HTML entities
    tweet_text = html.unescape(tweet_text)
    
    # Remove URLs
    tweet_text = re.sub(r'http\S+|www\S+|https\S+', '', tweet_text, flags=re.MULTILINE)
    
    # Remove mentions (@username)
    tweet_text = re.sub(r'@\w+', '', tweet_text)
    
    # Remove hashtags
    tweet_text = re.sub(r'#\w+', '', tweet_text)
    
    # Remove extra whitespace
    tweet_text = re.sub(r'\s+', ' ', tweet_text).strip()
    
    return tweet_text

def extract_emojis(tweet_text):
    """Extract emojis from the tweet text"""
    return ''.join(char for char in tweet_text if emoji.is_emoji(char))

def get_user_tweets(username):
    """Fetch tweets for a specific user from the database"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        # Convert username to lowercase for case-insensitive comparison
        username = username.lower()
        cursor.execute("""
            SELECT id, tweet_text, sentiment, tweet_date, query 
            FROM tweets 
            WHERE LOWER(username) = %s
            ORDER BY tweet_date DESC
        """, (username,))
        
        tweets = cursor.fetchall()
        return tweets
    except Exception as e:
        st.error(f"Error fetching tweets: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def analyze_sentiment(tweet):
    """Analyze sentiment of a single tweet using OpenAI"""
    if not tweet:
        return "No tweet selected for analysis."
    
    # Preprocess tweet for better analysis
    original_text = tweet[1]
    processed_text = preprocess_tweet(original_text)
    
    # Extract emojis
    emojis = extract_emojis(original_text)
    
    prompt = f"""Analyze the sentiment of the following tweet and provide a detailed analysis:
    
    Original Tweet: {original_text}
    Processed Tweet: {processed_text}
    Emojis: {emojis if emojis else "None"}
    
    Please provide a comprehensive analysis that includes:
    1. Overall sentiment (Positive/Negative)
    2. Detailed explanation of the sentiment
    3. Analysis of any emojis used and their impact on sentiment
    4. Identification of slang language or informal expressions
    5. Key themes and patterns in the tweet
    6. Cultural or contextual factors that might affect interpretation
    
    Be thorough in your analysis, considering both the explicit text and the implicit meaning conveyed through emojis and slang.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in sentiment analysis with deep knowledge of social media language, emojis, and slang. You excel at interpreting both explicit and implicit meaning in tweets."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error in sentiment analysis: {str(e)}"

def convert_negative_to_positive(tweet):
    """Convert a negative tweet to positive using OpenAI"""
    if not tweet:
        return "No tweet selected for conversion."
    
    connection = get_db_connection()
    if not connection:
        return "Database connection failed"
    
    try:
        cursor = connection.cursor()
        
        # Preprocess the tweet
        original_text = tweet[1]
        processed_text = preprocess_tweet(original_text)
        
        # Extract emojis
        emojis = extract_emojis(original_text)
        
        prompt = f"""Convert this negative tweet into a positive one while maintaining its core message:
        
        Original tweet: {original_text}
        Processed tweet: {processed_text}
        Emojis: {emojis if emojis else "None"}
        
        Please provide a positive version of this tweet that:
        1. Maintains the same core message or topic
        2. Uses positive language and framing
        3. Preserves any relevant emojis or adapts them to match the positive sentiment
        4. Keeps a similar tone and style (formal/informal)
        5. Addresses the same audience
        
        Provide only the converted positive tweet text.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert at converting negative sentiment to positive while preserving the core message and maintaining authenticity. You understand social media language, emojis, and slang."},
                {"role": "user", "content": prompt}
            ]
        )
        
        positive_tweet = response.choices[0].message.content
        
        # Update the database
        cursor.execute("""
            UPDATE tweets 
            SET tweet_text = %s, sentiment = 1 
            WHERE id = %s
        """, (positive_tweet, tweet[0]))
        
        connection.commit()
        return "Successfully converted tweet to positive!"
    except Exception as e:
        connection.rollback()
        return f"Error in conversion: {str(e)}"
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Streamlit UI
st.title("Tweet Sentiment Analysis")

# Clear any cached data
st.cache_data.clear()

# User input - simple text input without dropdown
username = st.text_input("Enter Twitter Username (without @):", key="username_input")

if username:
    # Remove @ if user included it and convert to lowercase
    username = username.strip('@').lower()
    
    # Update session state
    st.session_state.current_username = username
    
    # Fetch tweets
    tweets = get_user_tweets(username)
    
    if tweets:
        # Display all tweets
        st.subheader(f"Tweets for @{username}")
        
        for tweet in tweets:
            # Create a container for each tweet
            tweet_container = st.container()
            with tweet_container:
                st.markdown("---")  # Add a separator between tweets
                st.text(f"Tweet ID: {tweet[0]}")
                st.text(f"Original Text: {tweet[1]}")
                st.text(f"Processed Text: {preprocess_tweet(tweet[1])}")
                st.text(f"Emojis: {extract_emojis(tweet[1]) if extract_emojis(tweet[1]) else 'None'}")
                st.text(f"Sentiment: {'Positive' if tweet[2] == 1 else 'Negative'}")
                st.text(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Create columns for buttons
                col1, col2 = st.columns(2)
                
                # Analyze sentiment button
                with col1:
                    if st.button("Analyze Sentiment", key=f"analyze_{tweet[0]}"):
                        analysis = analyze_sentiment(tweet)
                        st.markdown("### Sentiment Analysis")
                        st.write(analysis)
                
                # Convert negative to positive button
                with col2:
                    if st.button("Convert Negative to Positive", key=f"convert_{tweet[0]}"):
                        result = convert_negative_to_positive(tweet)
                        st.write(result)
                        
                        # Refresh tweets after conversion
                        tweets = get_user_tweets(username)
                        st.markdown("### Updated Tweet")
                        updated_tweet = next((t for t in tweets if t[0] == tweet[0]), None)
                        if updated_tweet:
                            st.text(f"Tweet ID: {updated_tweet[0]}")
                            st.text(f"Original Text: {updated_tweet[1]}")
                            st.text(f"Processed Text: {preprocess_tweet(updated_tweet[1])}")
                            st.text(f"Emojis: {extract_emojis(updated_tweet[1]) if extract_emojis(updated_tweet[1]) else 'None'}")
                            st.text(f"Sentiment: {'Positive' if updated_tweet[2] == 1 else 'Negative'}")
                            st.text(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.error(f"No tweets found for username: {username}") 