import json
import os

class UserManager:
    def __init__(self, filename="users.json"):
        self.filename = filename
        self.users = {}
        self.load_users()

    def load_users(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    self.users = json.load(f)
            except:
                self.users = {}
        else:
            self.users = {}

    def save_users(self):
        with open(self.filename, "w") as f:
            json.dump(self.users, f)

    def create_user(self, username, password, fav_movies=None, fav_books=None):
        self.load_users()
        if username in self.users:
            return False, "Username already exists."
        
        # Listeleri garantiye al (None gelirse boş liste yap)
        f_movies = fav_movies if fav_movies is not None else []
        f_books = fav_books if fav_books is not None else []

        self.users[username] = {
            "password": password,
            "fav_movies": f_movies,
            "fav_books": f_books,
            # Watchlist ve Readlist'i favorilerle başlat
            "watchlist": list(f_movies), 
            "readlist": list(f_books),
            "ratings": []
        }
        
        # 5 Yıldız Puanı Olarak Ekle (Öneri motorunu tetiklemek için)
        for m in f_movies:
            self.users[username]["ratings"].append({"type": "movie", "name": m, "score": 5})
        for b in f_books:
            self.users[username]["ratings"].append({"type": "book", "name": b, "score": 5})

        self.save_users()
        return True, "User created successfully!"

    def authenticate_user(self, username, password):
        self.load_users()
        if username not in self.users: return False, "User not found.", None
        
        if self.users[username]["password"] == password:
            return True, "Login successful.", self.users[username]
        else:
            return False, "Incorrect password.", None

    def add_rating(self, username, item_type, item_name, score):
        self.load_users()
        if username not in self.users: return False, "User not found"

        user_ratings = self.users[username]["ratings"]
        
        # Varsa güncelle
        updated = False
        for r in user_ratings:
            if r["name"] == item_name and r["type"] == item_type:
                r["score"] = score
                updated = True
                break
        
        if not updated:
            user_ratings.append({"type": item_type, "name": item_name, "score": score})

        # OTOMATİK FAVORİ (5 Puan Kuralı)
        if score == 5:
            target_list = "fav_movies" if item_type == "movie" else "fav_books"
            if item_name not in self.users[username][target_list]:
                self.users[username][target_list].append(item_name)
        
        self.save_users()
        return True, "Rated successfully!"

    def manage_list(self, username, list_type, action, item_name):
        self.load_users()
        if username not in self.users: return False, "User not found"
        
        # list_type güvenliği
        if list_type not in self.users[username]:
            self.users[username][list_type] = []

        target = self.users[username][list_type]
        
        if action == "add":
            if item_name not in target: target.append(item_name)
        elif action == "remove":
            if item_name in target: target.remove(item_name)
        
        self.save_users()
        return True, "List updated"
