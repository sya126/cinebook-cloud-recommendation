from data_manager import DataManager
from data_processor import DataProcessor
from recommender import RecommenderEngine # Yeni ekledik

def main():
    print("🚀 Sistem Başlatılıyor...\n")
    
    dm = DataManager()
    dp = DataProcessor()
    rec_engine = RecommenderEngine() # Motoru çalıştır
    
    # --- BÖLÜM 1: FİLMLER (Test etmesi daha kolay) ---
    movies, movie_ratings = dm.load_movies_data()
    
    if movies is not None:
        clean_movie_data = dp.process_movies(movies, movie_ratings)
        
        print("\n--- 🎬 FİLM TAVSİYE SİSTEMİ ---")
        # 1. Matrisi Hazırla
        # title = Film İsmi, userId = Kullanıcı, rating = Puan
        movie_matrix = rec_engine.prepare_matrix(clean_movie_data, 'title', 'userId', 'rating')
        
        # 2. Modeli Eğit
        rec_engine.train(movie_matrix)
        
        # 3. ÖRNEK TAVSİYE İSTEYELİM
        test_movie = "Toy Story (1995)"
        print(f"\n   🤔 '{test_movie}' izleyenler şunları da sevdi:")
        
        recommendations = rec_engine.recommend(test_movie)
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")

    # --- BÖLÜM 2: KİTAPLAR ---
    books, book_ratings, book_users = dm.load_books_data()
    
    if books is not None:
        clean_book_data = dp.process_books(books, book_ratings)
        
        print("\n--- 📘 KİTAP TAVSİYE SİSTEMİ ---")
        # BookTitle = Kitap, UserID = Kullanıcı, BookRating = Puan
        book_matrix = rec_engine.prepare_matrix(clean_book_data, 'BookTitle', 'UserID', 'BookRating')
        
        rec_engine.train(book_matrix)
        
        # Harry Potter testi yapalım (Veride kesin vardır)
        # Not: Kitap isminin tam eşleşmesi lazım, veri setinde genelde 'Harry Potter...' diye geçer.
        # Şansımızı deneyelim, hata verirse listeden başka isim seçeriz.
        test_book = "The Lovely Bones: A Novel" 
        print(f"\n   🤔 '{test_book}' okuyanlar şunları da sevdi:")
        
        recommendations = rec_engine.recommend(test_book)
        if isinstance(recommendations, list):
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        else:
            print(recommendations)

if __name__ == "__main__":
    main()