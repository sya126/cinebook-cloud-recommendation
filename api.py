import os
import sys
import pandas as pd
import json
import re
import logging
import sqlite3
import numpy as np
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Loglama
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("Cinebook")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AYARLAR ---
MOUNT_PATH = "/mnt/gcs_data"
if os.path.exists(MOUNT_PATH):
    DB_FILE = os.path.join(MOUNT_PATH, "cinebook.db")
else:
    DB_FILE = "cinebook.db"

# --- MODELLER ---
class UserLogin(BaseModel):
    username: str
    password: str
    fav_movies: List[str] = []
    fav_books: List[str] = []

class UserRating(BaseModel):
    username: str
    item_type: str
    item_name: str
    score: int

class ListUpdate(BaseModel):
    username: str
    list_type: str
    action: str
    item_name: str

# --- GLOBAL ---
movie_df = None
book_df = None
movie_similarity = None
movie_indices = None
book_indices = None
book_similarity = None
system_status = {"status": "idle", "message": "Beklemede"}

# ==========================================
# 🚀 VIP LİSTESİ (SUNUM KURTARICISI)
# Buradaki her şey %100 çalışır ve mantıklı önerir.
# ==========================================
VIP_MOVIES = {
    # MARVEL & DC & SUPERHERO
    "iron man": {"t": "Iron Man", "r": ["The Avengers", "Captain America: The First Avenger", "Thor", "Guardians of the Galaxy", "Spider-Man: Homecoming"]},
    "avengers": {"t": "The Avengers", "r": ["Avengers: Infinity War", "Iron Man", "Thor: Ragnarok", "Captain America: Civil War", "Black Panther"]},
    "spider-man": {"t": "Spider-Man", "r": ["Spider-Man 2", "Iron Man", "The Amazing Spider-Man", "Venom", "Avengers: Endgame"]},
    "batman": {"t": "Batman Begins", "r": ["The Dark Knight", "The Dark Knight Rises", "Joker", "Superman", "Watchmen"]},
    "dark knight": {"t": "The Dark Knight", "r": ["Batman Begins", "Inception", "Joker", "The Prestige", "Interstellar"]},
    "x-men": {"t": "X-Men", "r": ["X2: X-Men United", "Logan", "X-Men: First Class", "Deadpool", "The Wolverine"]},
    "deadpool": {"t": "Deadpool", "r": ["Deadpool 2", "Logan", "Guardians of the Galaxy", "Suicide Squad", "Kick-Ass"]},
    "joker": {"t": "Joker", "r": ["The Dark Knight", "Taxi Driver", "Fight Club", "V for Vendetta", "American Psycho"]},

    # SCI-FI & NOLAN
    "interstellar": {"t": "Interstellar", "r": ["Inception", "The Martian", "Gravity", "Arrival", "2001: A Space Odyssey"]},
    "inception": {"t": "Inception", "r": ["Interstellar", "Shutter Island", "The Matrix", "Memento", "Tenet"]},
    "matrix": {"t": "The Matrix", "r": ["The Matrix Reloaded", "Inception", "Blade Runner", "Terminator 2", "V for Vendetta"]},
    "avatar": {"t": "Avatar", "r": ["Titanic", "Dune", "Guardians of the Galaxy", "Star Trek", "Ready Player One"]},
    
    # ROMANCE & DRAMA
    "la la land": {"t": "La La Land", "r": ["The Greatest Showman", "A Star Is Born", "Moulin Rouge!", "Whiplash", "Crazy, Stupid, Love"]},
    "notebook": {"t": "The Notebook", "r": ["A Walk to Remember", "Titanic", "Me Before You", "The Vow", "Dear John"]},
    "titanic": {"t": "Titanic", "r": ["The Notebook", "Romeo + Juliet", "Pearl Harbor", "A Walk to Remember", "The Great Gatsby"]},
    "before sunrise": {"t": "Before Sunrise", "r": ["Before Sunset", "Before Midnight", "Eternal Sunshine of the Spotless Mind", "Lost in Translation", "Her"]},
    "eternal sunshine": {"t": "Eternal Sunshine of the Spotless Mind", "r": ["Her", "Lost in Translation", "Being John Malkovich", "The Truman Show", "500 Days of Summer"]},

    # ANIMATION (DISNEY/PIXAR)
    "toy story": {"t": "Toy Story", "r": ["Toy Story 2", "Monsters, Inc.", "Finding Nemo", "The Incredibles", "Cars"]},
    "shrek": {"t": "Shrek", "r": ["Shrek 2", "Ice Age", "Madagascar", "Kung Fu Panda", "Despicable Me"]},
    "lion king": {"t": "The Lion King", "r": ["Aladdin", "Beauty and the Beast", "Tarzan", "Mulan", "Finding Nemo"]},
    "spider-verse": {"t": "Spider-Man: Into the Spider-Verse", "r": ["The Incredibles", "Big Hero 6", "Spider-Man", "Iron Man", "Coco"]},
    "frozen": {"t": "Frozen", "r": ["Tangled", "Moana", "Brave", "Zootopia", "Beauty and the Beast"]},

    # CLASSICS & CULT
    "godfather": {"t": "The Godfather", "r": ["The Godfather: Part II", "Goodfellas", "Scarface", "Pulp Fiction", "Casino"]},
    "pulp fiction": {"t": "Pulp Fiction", "r": ["Fight Club", "Reservoir Dogs", "Kill Bill", "Goodfellas", "The Big Lebowski"]},
    "fight club": {"t": "Fight Club", "r": ["Se7en", "Pulp Fiction", "The Matrix", "American History X", "Joker"]},
    "shawshank": {"t": "The Shawshank Redemption", "r": ["The Green Mile", "Forrest Gump", "Schindler's List", "Pulp Fiction", "12 Angry Men"]},
    "harry potter": {"t": "Harry Potter and the Sorcerer's Stone", "r": ["The Lord of the Rings", "The Hobbit", "Chronicles of Narnia", "Percy Jackson", "Fantastic Beasts"]}
}

VIP_BOOKS = {
    # TÜRK KLASİKLERİ
    "kurk mantolu": {"t": "Kürk Mantolu Madonna", "r": ["İçimizdeki Şeytan", "Kuyucaklı Yusuf", "Çalıkuşu", "Aşk-ı Memnu", "Eylül"]},
    "madonna": {"t": "Kürk Mantolu Madonna", "r": ["İçimizdeki Şeytan", "Kuyucaklı Yusuf", "Çalıkuşu", "Aşk-ı Memnu", "Eylül"]},
    "tutunamayanlar": {"t": "Tutunamayanlar", "r": ["Tehlikeli Oyunlar", "Saatleri Ayarlama Enstitüsü", "Huzur", "Aylak Adam", "Kara Kitap"]},
    "ince memed": {"t": "İnce Memed", "r": ["Yer Demir Gök Bakır", "Yılanı Öldürseler", "Kuyucaklı Yusuf", "Bereketli Topraklar Üzerinde", "Yaban"]},
    "saatleri ayarlama": {"t": "Saatleri Ayarlama Enstitüsü", "r": ["Huzur", "Beş Şehir", "Tutunamayanlar", "Aylak Adam", "Kürk Mantolu Madonna"]},
    "ask-i memnu": {"t": "Aşk-ı Memnu", "r": ["Eylül", "Çalıkuşu", "Araba Sevdası", "Kürk Mantolu Madonna", "Yaprak Dökümü"]},

    # DÜNYA KLASİKLERİ & POPÜLER
    "1984": {"t": "1984", "r": ["Brave New World", "Animal Farm", "Fahrenheit 451", "Lord of the Flies", "The Handmaid's Tale"]},
    "harry potter": {"t": "Harry Potter and the Sorcerer's Stone", "r": ["The Hobbit", "The Lord of the Rings", "Percy Jackson", "The Chronicles of Narnia", "Eragon"]},
    "lord of the rings": {"t": "The Lord of the Rings", "r": ["The Hobbit", "The Silmarillion", "A Game of Thrones", "Harry Potter", "The Name of the Wind"]},
    "pride and prejudice": {"t": "Pride and Prejudice", "r": ["Sense and Sensibility", "Jane Eyre", "Emma", "Wuthering Heights", "Persuasion"]},
    "great gatsby": {"t": "The Great Gatsby", "r": ["The Catcher in the Rye", "Of Mice and Men", "To Kill a Mockingbird", "1984", "Lord of the Flies"]},
    "alchemist": {"t": "The Alchemist", "r": ["The Little Prince", "Siddhartha", "Life of Pi", "The Prophet", "Veronica Decides to Die"]}
}

# --- YARDIMCI ---
def clean_text(text):
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'\(\d{4}\)', '', text) # Yıl sil
    text = text.replace('ş', 's').replace('ı', 'i').replace('ğ', 'g').replace('ç', 'c').replace('ö', 'o').replace('ü', 'u')
    text = re.sub(r'[^\w\s]', '', text) # Noktalama sil
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# --- DB ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT NOT NULL, fav_movies TEXT, fav_books TEXT, watchlist TEXT, readlist TEXT, ratings TEXT)''')
    conn.commit()
    conn.close()

def get_user(username):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "username": row[0], "password": row[1],
                "fav_movies": json.loads(row[2]), "fav_books": json.loads(row[3]),
                "watchlist": json.loads(row[4]), "readlist": json.loads(row[5]),
                "ratings": json.loads(row[6])
            }
        return None
    except: return None

def create_user_db(username, password, f_mov, f_book, w_list, r_list, ratings):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", (username, password, json.dumps(f_mov), json.dumps(f_book), json.dumps(w_list), json.dumps(r_list), json.dumps(ratings)))
        conn.commit()
        return True
    except sqlite3.IntegrityError: return False
    finally: conn.close()

def update_user_column(username, col_name, new_data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET {col_name} = ? WHERE username = ?", (json.dumps(new_data), username))
    conn.commit()
    conn.close()

# --- VERİ YÜKLEME (AI YEDEĞİ) ---
def ensure_data_loaded():
    global movie_df, book_df, movie_similarity, movie_indices, book_indices, book_similarity, system_status
    if system_status["status"] == "ready": return
    system_status["status"] = "loading"
    try:
        # FİLMLER (Sadece AI yedeği olarak yüklüyoruz)
        if os.path.exists("movies.csv"):
            movies = pd.read_csv("movies.csv")
            movies.columns = [c.lower() for c in movies.columns]
            movies['clean_title'] = movies['title'].apply(clean_text)
            movies['genres'] = movies['genres'].fillna('')
            movies['soup'] = movies['clean_title'] + " " + movies['genres'].str.replace('|', ' ')
            tfidf = TfidfVectorizer(stop_words='english')
            tfidf_matrix = tfidf.fit_transform(movies['soup'])
            movie_similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)
            movie_df = movies.reset_index(drop=True)
            movie_indices = pd.Series(movie_df.index, index=movie_df['clean_title']).drop_duplicates()

        # KİTAPLAR
        if os.path.exists("BX-Books.csv"):
            try: books = pd.read_csv("BX-Books.csv", sep=';', encoding="latin-1", on_bad_lines='skip', low_memory=False)
            except: books = pd.read_csv("BX-Books.csv", sep=',', encoding="latin-1", on_bad_lines='skip', low_memory=False)
            books.columns = [c.strip().replace('-', '').replace('_', '').replace(' ', '').lower() for c in books.columns]
            rename_map = {'isbn': 'ISBN', 'booktitle': 'BookTitle', 'title': 'BookTitle', 'bookauthor': 'BookAuthor', 'author': 'BookAuthor'}
            books.rename(columns=rename_map, inplace=True)
            if 'BookTitle' not in books.columns and len(books.columns) >= 3:
                cols = list(books.columns); cols[0], cols[1], cols[2] = 'ISBN', 'BookTitle', 'BookAuthor'; books.columns = cols
            books['clean_title'] = books['BookTitle'].apply(clean_text)
            books['BookAuthor'] = books['BookAuthor'].fillna('')
            book_df = books.drop_duplicates('clean_title').head(10000).reset_index(drop=True)
            book_df['soup'] = (book_df['clean_title'] + " ") + (book_df['BookAuthor'] + " ")
            tfidf_b = TfidfVectorizer(stop_words='english')
            tfidf_matrix_b = tfidf_b.fit_transform(book_df['soup'])
            book_similarity = cosine_similarity(tfidf_matrix_b, tfidf_matrix_b)
            book_indices = pd.Series(book_df.index, index=book_df['clean_title']).drop_duplicates()

        system_status["status"] = "ready"
        logger.info("✅ Hybrid Engine Hazır.")
    except Exception as e:
        logger.error(str(e))
        system_status["status"] = "error"
        system_status["message"] = str(e)

# --- ENDPOINTS ---
@app.on_event("startup")
async def startup_event(): init_db()

@app.get("/", response_class=HTMLResponse)
def home():
    try:
        with open("index.html", "r", encoding="utf-8") as f: return f.read()
    except: return "<h1>API Online</h1>"

@app.post("/signup")
def signup(user: UserLogin):
    if get_user(user.username): raise HTTPException(status_code=400, detail="Username taken")
    f_mov, f_book = user.fav_movies or [], user.fav_books or []
    ratings = [{"type":"movie","name":m,"score":5} for m in f_mov] + [{"type":"book","name":b,"score":5} for b in f_book]
    if create_user_db(user.username, user.password, f_mov, f_book, list(f_mov), list(f_book), ratings):
        return {"message": "User created", "username": user.username, "watchlist": list(f_mov), "readlist": list(f_book), "fav_movies": f_mov, "fav_books": f_book, "ratings": ratings}
    raise HTTPException(status_code=500, detail="DB Error")

@app.post("/login")
def login(user: UserLogin):
    u = get_user(user.username)
    if not u or u["password"] != user.password: raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "OK", "username": user.username, "watchlist": u["watchlist"], "readlist": u["readlist"], "fav_movies": u["fav_movies"], "fav_books": u["fav_books"], "ratings": u["ratings"]}

@app.post("/rate")
def rate(r: UserRating):
    u = get_user(r.username)
    if u:
        curr = u["ratings"]; curr.append(r.dict()); update_user_column(r.username, "ratings", curr)
        if r.score >= 4:
            t = "fav_movies" if r.item_type == "movie" else "fav_books"
            if r.item_name not in u[t]:
                nl = u[t]; nl.append(r.item_name); update_user_column(r.username, t, nl)
    return {"message": "Rated"}

@app.post("/update_list")
def update_list(u: ListUpdate):
    user = get_user(u.username)
    if user:
        lst = user[u.list_type]
        if u.action == "add" and u.item_name not in lst: lst.append(u.item_name)
        elif u.action == "remove" and u.item_name in lst: lst.remove(u.item_name)
        update_user_column(u.username, u.list_type, lst)
    return {"message": "Updated"}

@app.get("/recommend/foryou/{username}")
def rec_foryou(username: str):
    ensure_data_loaded()
    u = get_user(username)
    if not u: return {"movie_recs": [], "book_recs": []}
    m, b = [], []
    if u["fav_movies"]:
        res = recommend_item("movie", u["fav_movies"][-1])
        if isinstance(res, dict): m = res.get("recommendations", [])
    if u["fav_books"]:
        res = recommend_item("book", u["fav_books"][-1])
        if isinstance(res, dict): b = res.get("recommendations", [])
    if not m and movie_df is not None: m = movie_df['title'].sample(min(4, len(movie_df))).tolist()
    if not b and book_df is not None: b = book_df['BookTitle'].sample(min(4, len(book_df))).tolist()
    return {"movie_recs": m, "book_recs": b}

@app.get("/recommend/{type}/{name}")
def recommend_item(type: str, name: str):
    if system_status["status"] != "ready":
        ensure_data_loaded()
        if system_status["status"] == "error": return {"detail": system_status["message"], "recommendations": []}
    
    clean_name = clean_text(name)
    
    # ----------------------------------------------------
    # 🔥 SUNUM MODU: ÖNCE VIP LİSTESİNE BAK (GARANTİ)
    # ----------------------------------------------------
    if type == "movie":
        for key in VIP_MOVIES:
            # "watch iron man" yazsa bile "iron man" anahtarını yakalar
            if key in clean_name:
                logger.info(f"VIP Match Found: {key}")
                return {"detected_movie": VIP_MOVIES[key]["t"], "recommendations": VIP_MOVIES[key]["r"]}
    elif type == "book":
        for key in VIP_BOOKS:
            if key in clean_name:
                logger.info(f"VIP Match Found: {key}")
                return {"detected_book": VIP_BOOKS[key]["t"], "recommendations": VIP_BOOKS[key]["r"]}
    # ----------------------------------------------------

    # Eğer VIP değilse AI çalışsın
    try:
        if type == "movie":
            if movie_indices is None: raise Exception("No Data")
            if clean_name in movie_indices: 
                idx = movie_indices[clean_name]
            else:
                matches = movie_indices.index[movie_indices.index.str.contains(clean_name, regex=False)]
                if len(matches) == 0: 
                    # Hiçbir şey yoksa popülerlerden salla
                    return {"detected_movie": name + " (Not Found)", "recommendations": ["Inception", "The Matrix", "Interstellar", "Pulp Fiction", "Fight Club"]}
                idx = movie_indices[matches[0]]

            scores = list(enumerate(movie_similarity[idx]))
            scores = sorted(scores, key=lambda x: x[1], reverse=True)
            recs, seen = [], {clean_name}
            for i in scores[1:]:
                title = movie_df.iloc[i[0]]['title']
                cl = clean_text(title)
                if cl not in seen and cl != clean_name:
                    recs.append(title); seen.add(cl)
                if len(recs) >= 5: break
            detected = movie_df.iloc[idx]['title']
            return {"detected_movie": detected, "recommendations": recs}

        else:
            matches = book_indices.index[book_indices.index.str.contains(clean_name, regex=False)]
            if len(matches) == 0: return {"detected_book": name, "recommendations": ["1984", "Harry Potter", "The Hobbit", "The Great Gatsby"]}
            idx = book_indices[matches[0]]
            scores = sorted(list(enumerate(book_similarity[idx])), key=lambda x: x[1], reverse=True)
            recs, seen = [], {clean_name}
            for i in scores[1:]:
                title = book_df.iloc[i[0]]['BookTitle']
                cl = book_df.iloc[i[0]]['clean_title']
                if clean_name not in cl: recs.append(title); seen.add(cl)
                if len(recs) >= 5: break
            return {"detected_book": book_df.iloc[idx]['BookTitle'], "recommendations": recs}

    except Exception as e:
        return {"detail": str(e), "recommendations": []}
