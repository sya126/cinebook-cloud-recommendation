import pandas as pd

class DataProcessor:
    def __init__(self):
        print("DataProcessor initialized.")

    def process_books(self, books, ratings, min_user_ratings=20):
        """
        Cleans the book dataset and filters out inactive users.
        Based on Project Methodology Section A.
        """
        print("\n--- 🧹 Processing & Cleaning Book Data ---")
        
        # 1. Convert Ratings to Numbers (Fix potential text errors)
        # 'coerce' means: if you find text like "good", turn it into NaN (empty)
        ratings['BookRating'] = pd.to_numeric(ratings['BookRating'], errors='coerce')
        
        # 2. Drop rows with missing values (NaN)
        original_count = len(ratings)
        ratings.dropna(subset=['BookRating'], inplace=True)
        books.dropna(subset=['BookTitle', 'BookAuthor'], inplace=True)
        
        # 3. Filter Users (Keep only users with >= 20 ratings)
        # Count how many ratings each user has
        user_counts = ratings['UserID'].value_counts()
        
        # Select users who have more than 'min_user_ratings'
        active_users = user_counts[user_counts >= min_user_ratings].index
        
        # Filter the original dataframe to keep only these users
        ratings_filtered = ratings[ratings['UserID'].isin(active_users)]
        
        print(f"   📉 Filtering Inactive Users (< {min_user_ratings} ratings):")
        print(f"      Original Ratings: {original_count}")
        print(f"      Cleaned Ratings:  {len(ratings_filtered)}")
        print(f"      Data Reduced by:  {100 - (len(ratings_filtered)/original_count*100):.1f}%")

        # 4. Merge Books and Ratings (Connect them via ISBN)
        # This creates a master table with User, Book Name, and Rating together
        print("   🔗 Merging Books and Ratings...")
        full_data = pd.merge(ratings_filtered, books, on='ISBN', how='inner')
        
        print(f"   ✅ Final Dataset Size: {len(full_data)} rows")
        return full_data

    def process_movies(self, movies, ratings):
        """
        Simple merge for movie data.
        """
        print("\n--- 🧹 Processing Movie Data ---")
        # Rename columns to match our standard if needed
        # MovieLens usually has 'movieId', 'title', 'genres'
        
        # Merge movies and ratings on 'movieId'
        # Note: In your movie file it might be 'movieId' or 'movie_id', we check first
        if 'movieId' in movies.columns:
            key = 'movieId'
        else:
            key = 'id' # fallback
            
        full_data = pd.merge(ratings, movies, on=key, how='inner')
        print(f"   ✅ Final Movie Dataset Size: {len(full_data)} rows")
        return full_data