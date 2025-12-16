import pandas as pd
import os
import sys

class DataManager:
    def load_movies_data(self):
        # Dosyaların olduğu klasörü bul
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Olası dosya isimleri (Büyük/küçük harf duyarlı)
        movie_files = ["movies.csv", "Movies.csv"]
        rating_files = ["ratings.csv", "Ratings.csv"]
        
        m_path = next((f for f in movie_files if os.path.exists(os.path.join(current_dir, f))), None)
        r_path = next((f for f in rating_files if os.path.exists(os.path.join(current_dir, f))), None)

        if m_path and r_path:
            try:
                # Demo için sadece 25.000 satır oku
                movies = pd.read_csv(os.path.join(current_dir, m_path))
                ratings = pd.read_csv(os.path.join(current_dir, r_path), nrows=25000)
                return movies, ratings
            except Exception as e:
                print(f"Movie Read Error: {e}", file=sys.stderr)
                return None, None
        else:
            # Hata ayıklama için klasördeki dosyaları yazdır
            print(f"❌ MOVIES NOT FOUND in {current_dir}. Files here: {os.listdir(current_dir)}", file=sys.stderr)
            return None, None

    def load_books_data(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Kitap dosya isimleri
        b_path = "BX-Books.csv"
        r_path = "BX-Book-Ratings.csv"
        
        if not (os.path.exists(os.path.join(current_dir, b_path)) and os.path.exists(os.path.join(current_dir, r_path))):
            print(f"❌ BOOKS NOT FOUND. Files here: {os.listdir(current_dir)}", file=sys.stderr)
            return None, None, None

        try:
            # Akıllı okuma (Ayraç kontrolü)
            def read_smart(filename, limit=None):
                path = os.path.join(current_dir, filename)
                args = {"encoding": "latin-1", "on_bad_lines": 'skip', "low_memory": False}
                if limit: args["nrows"] = limit
                
                try:
                    return pd.read_csv(path, sep=';', **args)
                except:
                    return pd.read_csv(path, sep=',', **args)

            books = read_smart(b_path)
            ratings = read_smart(r_path, limit=25000)

            # Temizlik
            books.columns = [c.strip().replace('-', '').replace('_', '').lower() for c in books.columns]
            ratings.columns = [c.strip().replace('-', '').replace('_', '').lower() for c in ratings.columns]

            books.rename(columns={'booktitle': 'BookTitle', 'bookauthor': 'BookAuthor', 'isbn': 'ISBN'}, inplace=True)
            ratings.rename(columns={'userid': 'UserID', 'bookrating': 'BookRating', 'isbn': 'ISBN'}, inplace=True)

            # ISBN Eşitle
            books['ISBN'] = books['ISBN'].astype(str).str.strip()
            ratings['ISBN'] = ratings['ISBN'].astype(str).str.strip()
            
            # Sadece puanı olan kitapları tut
            common = books[books['ISBN'].isin(ratings['ISBN'])]
            
            return common, ratings, None
        except Exception as e:
            print(f"Book Read Error: {e}", file=sys.stderr)
            return None, None, None
