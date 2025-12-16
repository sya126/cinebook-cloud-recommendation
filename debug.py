import pandas as pd
import os

# Veri klasörümüz
dataset_folder = 'datasets'

def inspect_file(filename):
    print(f"\n🔎 İNCELENİYOR: {filename}")
    path = os.path.join(dataset_folder, filename)
    
    try:
        # Sadece ilk 5 satırı oku, sütun isimlerini değiştirme
        df = pd.read_csv(
            path, 
            sep=';', 
            encoding="latin-1", 
            on_bad_lines='skip',
            dtype=str
        )
        
        print(f"   👉 Bulunan Sütun Sayısı: {len(df.columns)}")
        print(f"   👉 Sütun İsimleri: {list(df.columns)}")
        print("   👉 İlk Satır Örneği:")
        print(df.head(1))
        
    except Exception as e:
        print(f"   ❌ Dosya okunamadı: {e}")

# Sırayla tüm dosyalara bak
if __name__ == "__main__":
    inspect_file('BX-Books.csv')
    inspect_file('BX-Book-Ratings.csv')
    inspect_file('BX-Book-Users.csv')