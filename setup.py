import os
import urllib.request
import zipfile
import shutil

print("🔧 SİSTEM TAMİR EDİLİYOR...")

# 1. MOVIES (Yoksa İndir)
print("\n🎬 Film Dosyaları Kontrol Ediliyor...")
if not os.path.exists("movies.csv"):
    print("📥 movies.csv eksik! İnternetten indiriliyor...")
    try:
        url = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
        urllib.request.urlretrieve(url, "movies.zip")
        
        with zipfile.ZipFile("movies.zip", 'r') as zip_ref:
            zip_ref.extractall("temp_movies")
        
        # Dosyaları ana dizine taşı
        if os.path.exists("temp_movies/ml-latest-small/movies.csv"):
            shutil.move("temp_movies/ml-latest-small/movies.csv", "movies.csv")
            shutil.move("temp_movies/ml-latest-small/ratings.csv", "ratings.csv")
            print("✅ Film dosyaları başarıyla indirildi ve yerleştirildi!")
        
        # Çöpü temizle
        if os.path.exists("movies.zip"): os.remove("movies.zip")
        if os.path.exists("temp_movies"): shutil.rmtree("temp_movies")
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
else:
    print("✅ Film dosyaları (movies.csv) zaten var.")

# 2. BOOKS (Kontrol Et)
print("\n📚 Kitap Dosyaları Kontrol Ediliyor...")
if not os.path.exists("BX-Books.csv"):
    print("❌ DİKKAT: 'BX-Books.csv' bulunamadı!")
    print("👉 Lütfen kitap dosyalarını (BX-Books.csv ve BX-Book-Ratings.csv) sol taraftaki dosya menüsüne sürükle ve bırak.")
else:
    print("✅ Kitap dosyaları mevcut.")

# 3. ENGEL KALDIRMA (.gcloudignore)
print("\n🛡️ Engel Kaldırılıyor...")
if os.path.exists(".gcloudignore"):
    os.remove(".gcloudignore")
    print("✅ .gcloudignore silindi (Artık dosyalar sunucuya gidecek).")
else:
    print("✅ Engel dosyası zaten yok.")

print("\n" + "="*40)
print("🏁 TAMİR TAMAMLANDI!")
print("Şimdi şu komutu çalıştırarak siteyi güncelle:")
print("gcloud run deploy cinebook-app --source . --memory 8Gi --cpu 2 --timeout 900")
print("="*40)
