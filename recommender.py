import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class RecommenderEngine:
    def __init__(self):
        self.matrix = None
        self.similarity = None
        self.indices = None
        self.df = None
        self.ready = False

    def prepare_matrix(self, df, title_col, rating_col, feature_col=None):
        if df is None or df.empty:
            print("⚠️ Uyarı: Veri seti boş geldi!")
            return None

        # 1. Veri kopyası
        data = df.copy()
        
        # 2. String'e çevir (Hata önleyici)
        data[title_col] = data[title_col].astype(str).fillna('')
        
        # 3. TEKİLLEŞTİRME
        if rating_col in data.columns:
            data = data.sort_values(by=rating_col, ascending=False)
        data = data.drop_duplicates(subset=[title_col], keep='first')
        
        # 4. İndeksleri Sıfırla
        data = data.reset_index(drop=True)
        self.df = data
        
        # 5. 'Soup' Oluşturma
        if feature_col and feature_col in data.columns:
            self.df['soup'] = self.df[title_col] + " " + self.df[feature_col].astype(str).fillna('')
        else:
            self.df['soup'] = self.df[title_col]

        return self.df

    def train(self):
        if self.df is None or self.df.empty:
            print("⚠️ Eğitim verisi yok, motor başlatılamadı.")
            self.ready = False
            return

        print(f"⚙️ Model eğitiliyor... ({len(self.df)} satır)")
        tfidf = TfidfVectorizer(stop_words='english', min_df=2) # En az 2 kez geçen kelimeleri al
        
        try:
            # Bellek dostu olması için ilk 10.000 satırı alalım
            limit = 10000
            tfidf_matrix = tfidf.fit_transform(self.df['soup'].head(limit))
            
            self.similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)

            # Başlık -> Index Haritası
            # Sadece ilk 'limit' kadar başlığı alıyoruz
            limited_df = self.df.iloc[:limit]
            self.indices = pd.Series(limited_df.index, index=limited_df.iloc[:, 0].str.lower()).drop_duplicates()
            
            self.ready = True
            print(f"✅ Model Başarıyla Eğitildi! (İlk {limit} öğe üzerinden)")
        except Exception as e:
            print(f"❌ Model eğitimi hatası: {e}")
            self.ready = False

    def recommend(self, title, n_recommendations=5):
        if not self.ready or self.similarity is None:
            print("⚠️ Motor henüz hazır değil.")
            return None, [] # Her zaman tuple döndür

        title = str(title).lower().strip()
        
        idx = None
        if title in self.indices:
            idx = self.indices[title]
        else:
            # Fuzzy search (İçerenleri bul)
            matches = self.indices.index[self.indices.index.str.contains(title, regex=False)]
            if not matches.empty:
                matched_title = matches[0]
                idx = self.indices[matched_title]
        
        if idx is None:
            # print(f"'{title}' başlığı index'te bulunamadı.") # Debug için
            return None, [] # Bulunamadıysa boş liste ile tuple döndür

        # Eğer birden fazla index dönerse ilkini al
        if isinstance(idx, pd.Series):
            idx = idx.iloc[0]

        # ÖNEMLİ: Index'in benzerlik matrisi sınırları içinde olduğundan emin ol
        if idx >= len(self.similarity):
            # Bu durum, aranan öğenin ilk 10.000'de olmadığı anlamına gelir.
            # print(f"'{title}' (index: {idx}) modelin sınırları dışında.") # Debug için
            return None, []

        # Benzerlikleri hesapla
        sim_scores = list(enumerate(self.similarity[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:n_recommendations+1]

        movie_indices = [i[0] for i in sim_scores]
        
        # Sonuç
        found_title = self.df.iloc[idx, 0] if idx < len(self.df) else title
        return found_title, self.df.iloc[movie_indices, 0].tolist()
