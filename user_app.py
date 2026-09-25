# -*- coding: utf-8 -*-

import sys
import traceback
import tkinter as tk
from tkinter import messagebox
import subprocess

try:
    import customtkinter as ctk
    import requests
    import json
    import os
    from PIL import Image, ImageTk, ImageDraw
    import io
    import threading
    import concurrent.futures
    from datetime import datetime
    import cv2
except Exception as e:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Missing Library", f"មិនអាចដំណើរការបានទេ ដោយសារខ្វះ Library:\n\n{e}\n\nសូមសាកល្បង Run: pip install customtkinter requests pillow opencv-python")
    sys.exit()

# 🔑 បញ្ចូលព័ត៌មានរបស់អ្នកទីនេះ
SUPABASE_URL = "https://arrupyibnwvghwhgjfqg.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFycnVweWlibnd2Z2h3aGdqZnFnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk3OTY2NjUsImV4cCI6MjEwNTM3MjY2NX0.T8HQhUNNhB-lo948870hfqmoabbjo4yr-TTvoPPLb1E"
TELEGRAM_BOT_TOKEN = "8940465802:AAFdV3ZimYVkKC2iLq83LbxhaX_0Z0QtzxY"
TELEGRAM_ADMIN_CHAT_ID = "-1003964392370"

# 🔑 បន្ថែមព័ត៌មាន JSONBin ទីនេះ
JSONBIN_API_KEY = "$2a$10$zLpShJzAqZEDcD2JFAVA6uECAzPLVVZc/r009uIxoGJooGVxkFTsm"
JSONBIN_BIN_ID = "6ab0c526ffd5d160531e3259"
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
JSONBIN_HEADERS = {
    "X-Master-Key": JSONBIN_API_KEY,
    "Content-Type": "application/json"
}

# ⚠️ ដូរលេខ Version នេះពេលអ្នក Build កម្មវិធីជំនាន់ថ្មីដើម្បីកុំឲ្យវាលោត Update រហូត
CURRENT_APP_VERSION = "1.0"

HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json"
}

USER_HOME = os.path.expanduser("~")
LOCAL_DATA_FILE = os.path.join(USER_HOME, "tny_shop_data.json")

try:
    RESAMPLE_METHOD = Image.Resampling.BILINEAR
except AttributeError:
    RESAMPLE_METHOD = Image.BILINEAR

LANG = {
    "km": {
        "app_title": "TNY Shop - ទិញទំនិញអនឡាញ",
        "search": "ស្វែងរកទំនិញ...",
        "recent": "🕒 ធ្លាប់មើល",
        "fav": "❤️ ចំណូលចិត្ត",
        "cart": "🛒 កន្ត្រក",
        "account": "👤 គណនី",
        "login": "ចូលគណនី (Login)",
        "register": "បង្កើតគណនី (Register)",
        "email": "អ៊ីមែល (Username)",
        "password": "ពាក្យសម្ងាត់ (Password)",
        "confirm_password": "បញ្ជាក់ពាក្យសម្ងាត់",
        "back": "⬅ ត្រឡប់ក្រោយ",
        "category": "ប្រភេទចំណាត់ថ្នាក់",
        "all": "ទាំងអស់ (All)",
        "detail": "មើលលម្អិត",
        "remove": "❌ យកចេញ",
        "remove_fav": "❌ លុបពីចំណូលចិត្ត",
        "add_cart": "ដាក់ចូលកន្ត្រក",
        "stock": "មានស្តុក៖",
        "out_stock": "អស់ពីស្តុក (Out of stock)",
        "desc": "ការពិពណ៌នា៖",
        "specs": "លក្ខណៈបច្ចេកទេស៖",
        "similar": "ផលិតផលស្រដៀងគ្នា",
        "qty": "ចំនួន:",
        "total": "សរុប:",
        "checkout": "បញ្ជាក់ការទិញ",
        "history": "📦 ប្រវត្តិការទិញ",
        "logout": "ចាកចេញ",
        "no_data": "មិនមានទិន្នន័យទេ",
        "checkout_info": "ព័ត៌មានដឹកជញ្ជូន",
        "saved_fav": "បានរក្សាទុកក្នុងចំណូលចិត្ត",
        "removed_fav": "បានដកចេញពីចំណូលចិត្ត"
    },
    "en": {
        "app_title": "TNY Shop - Online Store",
        "search": "Search products...",
        "recent": "🕒 Recent",
        "fav": "❤️ Favorites",
        "cart": "🛒 Cart",
        "account": "👤 Account",
        "login": "Login",
        "register": "Register",
        "email": "Email (Username)",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "back": "⬅ Back",
        "category": "Categories",
        "all": "All",
        "detail": "View Detail",
        "remove": "❌ Remove",
        "remove_fav": "❌ Unfavorite",
        "add_cart": "Add to Cart",
        "stock": "In Stock:",
        "out_stock": "Out of Stock",
        "desc": "Description:",
        "specs": "Specifications:",
        "similar": "Similar Products",
        "qty": "Qty:",
        "total": "Total:",
        "checkout": "Place Order",
        "history": "📦 Order History",
        "logout": "Logout",
        "no_data": "No data available",
        "checkout_info": "Delivery Information",
        "saved_fav": "Saved to Favorites",
        "removed_fav": "Removed from Favorites"
    }
}

class UserStoreApp:
    def get_font(self, size=14, style="normal"):
        # ប្តូរពី "Khmer OS Battambang" ទៅជាឈ្មោះហ្វុងថ្មីរបស់អ្នក
        font_family = "Suwannaphum" if self.lang == "km" else "Arial"
        
        if style == "normal": return (font_family, size)
        return (font_family, size, style)

    def __init__(self, root):
        self.root = root
        self.lang = "km"
        self.root.title(self.t("app_title"))
        
        # 1. កំណត់ទំហំស្តង់ដារ ពេលអ្នកប្រើប្រាស់ចុចបង្រួមអេក្រង់ (Restore Down)
        window_width = 1200
        window_height = 800
        
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(900, 600)
        # ប្រើ after ដើម្បីពន្យារពេល 100 milliseconds (0.1 វិនាទី) មុននឹងបញ្ជាឲ្យពេញអេក្រង់
        self.root.after(100, lambda: self.root.state('zoomed'))
        
        ctk.set_appearance_mode("Light")
        self.root.configure(fg_color="#F3F4F6")
        
        # === ១. បន្ថែមកូដ Load ហ្វុង Google នៅទីនេះ ===
        font_path = os.path.join(os.path.dirname(__file__), "Suwannaphum-Regular.ttf") # ដូរឈ្មោះនេះទៅតាមឯកសារហ្វុងដែលអ្នកបានដោនឡូត
        if os.path.exists(font_path):
            ctk.FontManager.load_font(font_path)
        
        self.req_session = requests.Session()
        
        # === ២. បន្ថយ max_workers មកត្រឹម 4 ដើម្បីកុំឲ្យកម្មវិធីគាំង/ស្អិត ===
        self.img_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        
        self.all_products = []
        self.image_cache = {} 
        self.page_history = [] 
        
        self.current_category = self.t("all")
        self.search_query = ""
        
        self.spinner_frames = self.create_spinner_frames()
        self.playing_video = {"cap": None, "running": False}
        
        self.load_local_data()
        
        self.top_bar_container = ctk.CTkFrame(self.root, fg_color="#131921", height=70, corner_radius=0)
        self.top_bar_container.pack(fill="x", side="top")
        
        self.setup_top_bar()
        
        self.body_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.body_container.pack(fill="both", expand=True)

        self.load_products()
        self.current_page = 0
        self.navigate_to("home")
        self.auto_refresh_data()  # បិទ Auto Refresh
        self.check_app_update() 

    def t(self, key): return LANG[self.lang].get(key, key)

    def manual_refresh(self):
        self.load_products()
        self.render_current_page()

    def change_page(self, delta):
        self.current_page += delta
        self.render_current_page()

    # === បន្ថែមកូដ Auto Refresh នៅទីនេះ ===
    def auto_refresh_data(self):
        def background_fetch():
            needs_ui_update = False
            try:
                # ១. ទាញយកទិន្នន័យទំនិញថ្មីៗពី Supabase (អាប់ដេតមុខទំនិញថ្មី/កែប្រែ/លុប)
                res_prod = self.req_session.get(f"{SUPABASE_URL}/rest/v1/products?select=*", headers=HEADERS)
                if res_prod.status_code == 200:
                    new_products = res_prod.json()
                    # ឆែកមើលបើមានការប្រែប្រួលទិន្នន័យទំនិញ
                    if str(new_products) != str(self.all_products):
                        self.all_products = new_products
                        needs_ui_update = True
                
                # ២. ទាញយកទិន្នន័យបញ្ជាទិញពី JSONBin (អាប់ដេត Tracking ពេល Admin ប្តូរ)
                res_bin = self.req_session.get(JSONBIN_URL, headers=JSONBIN_HEADERS)
                if res_bin.status_code == 200:
                    data = res_bin.json().get("record", {})
                    new_orders = data.get("order_history", {})
                    if str(new_orders) != str(getattr(self, "order_history", {})):
                        self.order_history = new_orders
                        needs_ui_update = True
                
                # ៣. ប្រសិនបើមានទិន្នន័យប្រែប្រួល ធ្វើបច្ចុប្បន្នភាព UI ភ្លាមៗ
                if needs_ui_update:
                    self.root.after(0, self.update_top_badges)
                    self.root.after(0, lambda: self.render_current_page() if hasattr(self, 'body_container') and self.body_container.winfo_exists() else None)
                    
            except Exception:
                pass
            
            # បញ្ជាឲ្យវាឆែករៀងរាល់ ១៥ វិនាទីម្តង
            self.root.after(15000, self.auto_refresh_data)

        # ដំណើរការក្នុង Background
        import threading
        threading.Thread(target=background_fetch, daemon=True).start()

    def stop_video(self):
        self.playing_video["running"] = False
        if self.playing_video["cap"]:
            self.playing_video["cap"].release()
            self.playing_video["cap"] = None

    def show_bottom_toast(self, message, target_widget=None, is_remove=False):
        bg_color = "#E74C3C" if is_remove else "#2ECC71"
        toast = ctk.CTkFrame(self.root, fg_color=bg_color, corner_radius=8, border_width=1, border_color="#FFFFFF")
        
        lbl = ctk.CTkLabel(toast, text=message, font=self.get_font(12, "bold"), text_color="white")
        lbl.pack(padx=15, pady=8)
        
        # បើមានបោះ Target Widget មក ឲ្យវាលោតពីក្រោម Widget នោះ
        if target_widget and target_widget.winfo_exists():
            toast.update_idletasks() # ឲ្យកម្មវិធីអានទំហំ Toast សិន
            
            # ទាញយកទីតាំង (X,Y) របស់ប៊ូតុងធៀបនឹងអេក្រង់កម្មវិធី
            root_x = self.root.winfo_rootx()
            root_y = self.root.winfo_rooty()
            
            widget_x = target_widget.winfo_rootx() - root_x
            widget_y = target_widget.winfo_rooty() - root_y
            
            # រៀបចំទីតាំងឲ្យចំកណ្តាលពីក្រោម Target Widget នោះ
            pos_x = widget_x + (target_widget.winfo_width() // 2) - (toast.winfo_width() // 2)
            pos_y = widget_y + target_widget.winfo_height() + 8 # ដកឃ្លា 8px ពីក្រោមប៊ូតុង
            
            toast.place(x=pos_x, y=pos_y)
            toast.lift() # រុញឲ្យវាមកនៅផ្ទាំងលើគេបង្អស់កុំអោយគេបាំង
        else:
            # បើគ្មាន Target ទេ ឲ្យវាលោតចំកណ្តាលផ្នែកខាងក្រោមធម្មតា (ដូចពេល Checkout)
            toast.place(relx=0.5, rely=0.9, anchor="center")
            
            self.root.after(2500, toast.destroy)
        def animate_bounce(step=0):
            try:
                if step < 15:
                    size = 10 + (step * 8); font_size = 5 + (step * 4)
                    toast.configure(width=size, height=size, corner_radius=size//2); lbl.configure(font=("Arial", font_size, "bold"))
                    self.root.after(15, animate_bounce, step + 1)
                elif step < 20: 
                    size = 130 - ((step - 15) * 4); font_size = 65 - ((step - 15) * 2)
                    toast.configure(width=size, height=size, corner_radius=size//2); lbl.configure(font=("Arial", font_size, "bold"))
                    self.root.after(15, animate_bounce, step + 1)
                else: self.root.after(1000, toast.destroy)
            except: pass
        animate_bounce()

    def toggle_language(self):
        old_lang = self.lang
        self.lang = "en" if self.lang == "km" else "km"
        self.root.title(self.t("app_title"))
        
        self.entry_search.delete(0, tk.END)
        self.entry_search.insert(0, self.t("search"))
        self.btn_lang.configure(text="🌐 EN" if self.lang == "km" else "🌐 ខ្មែរ")
        self.update_top_badges()
        
        exact_swaps = {LANG[old_lang][k]: LANG[self.lang][k] for k in LANG[old_lang]}
        partial_swaps = {
            LANG[old_lang]["stock"]: LANG[self.lang]["stock"],
            LANG[old_lang]["total"]: LANG[self.lang]["total"]
        }
        
        def update_widget(w):
            try:
                txt = w.cget("text")
                if isinstance(txt, str) and txt:
                    if txt in exact_swaps: w.configure(text=exact_swaps[txt])
                    else:
                        for old_p, new_p in partial_swaps.items():
                            if old_p in txt: w.configure(text=txt.replace(old_p, new_p))
                
                current_font = w.cget("font")
                if current_font and isinstance(current_font, (tuple, list)):
                    size = current_font[1] if len(current_font) > 1 else 14
                    style = current_font[2] if len(current_font) > 2 else "normal"
                    w.configure(font=self.get_font(size, style))
            except: pass
            for child in w.winfo_children(): update_widget(child)
            
        update_widget(self.body_container)
        #self.cat_var.set(self.t("category"))

    def check_app_update(self):
        def background_check():
            try:
                res = self.req_session.get(f"{SUPABASE_URL}/rest/v1/app_settings?id=eq.1&select=version,download_url", headers=HEADERS)
                if res.status_code == 200 and res.json():
                    data = res.json()[0]
                    server_version = data.get("version")
                    if server_version and str(server_version) != CURRENT_APP_VERSION:
                        self.root.after(0, lambda: self.show_update_alert_icon(server_version, data.get("download_url")))
            except: pass
        threading.Thread(target=background_check, daemon=True).start()
        #self.root.after(30000, self.check_app_update)

    def show_update_alert_icon(self, new_ver, dl_url):
        self.pending_update_ver = new_ver
        self.pending_update_url = dl_url
        if self.page_history and self.page_history[-1][0] == "home": self.render_current_page()

    def perform_auto_update(self, download_url):
        self.update_alert_btn.configure(text="⏳ កំពុងទាញយក... (Downloading)", state="disabled")
        self.root.update()
        def background_download():
            try:
                r = requests.get(download_url, stream=True)
                r.raise_for_status()
                current_file = os.path.abspath(sys.argv[0])
                current_dir = os.path.dirname(current_file)
                current_name = os.path.basename(current_file)
                ext = ".exe" if current_name.lower().endswith(".exe") else ".py"
                new_file = os.path.join(current_dir, f"new_update{ext}")
                with open(new_file, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
                if os.name == 'nt': 
                    bat_path = os.path.join(current_dir, "updater.bat")
                    with open(bat_path, "w") as b:
                        b.write("@echo off\ntimeout /t 3 /nobreak > NUL\n") 
                        b.write(f'del "{current_name}"\nren "new_update{ext}" "{current_name}"\n') 
                        if ext == ".py": b.write(f'start python "{current_name}"\n')
                        else: b.write(f'start "" "{current_name}"\n')
                        b.write('del "%~f0"\n') 
                    subprocess.Popen([bat_path], creationflags=0x08000000)
                else:
                    os.rename(new_file, current_file)
                    subprocess.Popen([sys.executable, current_file] if ext == ".py" else [current_file])
                os._exit(0)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Update Error", f"បរាជ័យក្នុងការទាញយក Update: {e}"))
                self.root.after(0, lambda: self.update_alert_btn.configure(text="❌ បរាជ័យ (Failed)", state="normal"))
        threading.Thread(target=background_download, daemon=True).start()

    def create_spinner_frames(self):
        frames = []
        for i in range(12):
            img = Image.new("RGBA", (100, 100), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            draw.arc([10, 10, 90, 90], start=0, end=360, fill="#E5E7EB", width=12)
            draw.arc([10, 10, 90, 90], start=i*30, end=i*30+120, fill="#3498DB", width=12)
            frames.append(ctk.CTkImage(light_image=img, size=(40, 40)))
        return frames

    # ================== JSONBin Cloud Storage Functions ==================
    def load_local_data(self):
        try:
            res = requests.get(JSONBIN_URL, headers=JSONBIN_HEADERS)
            if res.status_code == 200:
                data = res.json().get("record", {})
                self.recent_items = data.get("recent", [])
                self.current_user = data.get("current_user", None)
                self.order_history = data.get("order_history", {})
                self.user_profiles = data.get("user_profiles", {})
                
                self.user_carts = data.get("user_carts", {})
                self.user_favorites = data.get("user_favorites", {})
                
                if self.current_user:
                    self.cart_items = self.user_carts.get(self.current_user, [])
                    self.favorite_items = self.user_favorites.get(self.current_user, [])
                else:
                    self.cart_items, self.favorite_items = [], []
            else: self._set_empty_data()
        except: self._set_empty_data()

    def _set_empty_data(self):
        self.cart_items, self.favorite_items, self.recent_items, self.current_user, self.order_history, self.user_profiles, self.user_carts, self.user_favorites = [], [], [], None, {}, {}, {}, {}

    def save_local_data(self):
        if self.current_user:
            if not hasattr(self, "user_carts"): self.user_carts = {}
            if not hasattr(self, "user_favorites"): self.user_favorites = {}
            self.user_carts[self.current_user] = self.cart_items
            self.user_favorites[self.current_user] = self.favorite_items

        data = {
            "recent": self.recent_items,
            "current_user": self.current_user,
            "order_history": getattr(self, "order_history", {}),
            "user_profiles": getattr(self, "user_profiles", {}),
            "user_carts": getattr(self, "user_carts", {}),
            "user_favorites": getattr(self, "user_favorites", {})
        }
        
        def upload_to_cloud():
            try: requests.put(JSONBIN_URL, headers=JSONBIN_HEADERS, json=data)
            except: pass
        threading.Thread(target=upload_to_cloud, daemon=True).start()
    # =====================================================================

    def add_to_recent(self, product):
        self.recent_items = [p for p in self.recent_items if str(p.get("id")) != str(product.get("id"))]
        self.recent_items.insert(0, product)
        if len(self.recent_items) > 12: self.recent_items.pop()
        self.save_local_data()

    def navigate_to(self, page_name, data=None):
        self.stop_video()
        if not self.page_history or self.page_history[-1] != (page_name, data):
            self.page_history.append((page_name, data))
        self.render_current_page()

    def go_back(self):
        self.stop_video()
        if len(self.page_history) > 1:
            self.page_history.pop() 
            self.render_current_page()
        else: self.navigate_to("home")

    def render_current_page(self):
        for widget in self.body_container.winfo_children(): widget.destroy()
        if not self.page_history: return
        page_name, data = self.page_history[-1]
        
        # បង្ហាញម៉ឺនុយនេះនៅគ្រប់ទំព័រជានិច្ច
        self.cat_menu_frame.pack(side="left", padx=(0, 10), before=self.search_bg)

        if page_name == "home": self.render_home_page()
        elif page_name == "detail": self.render_detail_page(data)
        elif page_name == "cart": self.render_cart_page()
        elif page_name == "favorites": self.render_favorites_page()
        elif page_name == "recent": self.render_recent_page()
        elif page_name == "login": self.render_login_page()
        elif page_name == "register": self.render_register_page()
        elif page_name == "account": self.render_account_page()
        elif page_name == "forgot_password": self.render_forgot_password_page()

    def setup_top_bar(self):
        lbl_logo = ctk.CTkLabel(self.top_bar_container, text="🛒 TNY Shop", font=("Arial", 24, "bold"), text_color="white", cursor="hand2")
        lbl_logo.pack(side="left", padx=30, pady=15)
        lbl_logo.bind("<Button-1>", lambda e: (setattr(self, "current_category", self.t("all")), setattr(self, "search_query", ""), setattr(self, "current_page", 0), self.navigate_to("home")))
        
        search_frame = ctk.CTkFrame(self.top_bar_container, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True, padx=20)
        
        self.cat_menu_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        self.cat_var = ctk.StringVar(value=" ☰ ")
        
        self.btn_category_dropdown = ctk.CTkOptionMenu(
            self.cat_menu_frame,
            values=[self.t("all"), "Laptop", "PC", "Monitor", "Accessories", "Other"],
            variable=self.cat_var,
            font=("Arial", 22, "bold"),
            text_color="white",
            fg_color="#131921",
            button_color="#131921",
            button_hover_color="#1A252F",
            dropdown_font=self.get_font(13),
            width=50,
            command=self.filter_category_from_dropdown
        )
        self.btn_category_dropdown.pack(fill="both", expand=True)

        self.search_bg = ctk.CTkFrame(search_frame, fg_color="#FFFFFF", height=40, corner_radius=5)
        self.search_bg.pack(side="left", fill="x", expand=True)
        self.search_bg.pack_propagate(False)
        
        self.entry_search = tk.Entry(self.search_bg, font=self.get_font(14), bg="#FFFFFF", fg="#333333", bd=0, highlightthickness=0, insertbackground="black")
        self.entry_search.pack(fill="both", expand=True, padx=15, pady=8)
        self.entry_search.insert(0, self.t("search"))
        self.entry_search.bind("<FocusIn>", lambda e: (self.entry_search.delete(0, tk.END), self.entry_search.config(fg="black")) if self.entry_search.get() == self.t("search") else None)
        self.entry_search.bind("<FocusOut>", lambda e: (self.entry_search.insert(0, self.t("search")), self.entry_search.config(fg="gray")) if self.entry_search.get() == "" else None)
        
        btn_search = ctk.CTkButton(search_frame, text="🔍", font=("Arial", 18), width=50, height=40, fg_color="#FEBD69", hover_color="#F3A847", text_color="black", corner_radius=5, command=self.search_products)
        btn_search.pack(side="left", padx=(5, 0))

        # ប៊ូតុង Refresh
        btn_refresh = ctk.CTkButton(search_frame, text="⟳", font=("Arial", 20), width=40, height=40, fg_color="transparent", hover_color="#2980B9", text_color="white", corner_radius=5, command=self.manual_refresh)
        btn_refresh.pack(side="left", padx=(5, 10))

        right_menu = ctk.CTkFrame(self.top_bar_container, fg_color="transparent")
        right_menu.pack(side="right", padx=10)

        self.btn_lang = ctk.CTkButton(right_menu, text="🌐 EN" if self.lang == "km" else "🌐 ខ្មែរ", font=("Arial", 14, "bold"), fg_color="transparent", text_color="#F1C40F", width=60, hover_color="#232F3E", command=self.toggle_language)
        self.btn_lang.pack(side="left", padx=5)

        self.btn_recent = ctk.CTkButton(right_menu, text=self.t("recent"), font=self.get_font(14, "bold"), fg_color="transparent", hover_color="#232F3E", text_color="white", command=lambda: self.navigate_to("recent"))
        self.btn_recent.pack(side="left", padx=5)

        self.btn_fav = ctk.CTkButton(right_menu, text=f"{self.t('fav')} ({len(self.favorite_items)})", font=self.get_font(14, "bold"), fg_color="transparent", hover_color="#232F3E", text_color="white", command=lambda: self.navigate_to("favorites"))
        self.btn_fav.pack(side="left", padx=5)

        self.btn_cart = ctk.CTkButton(right_menu, text=f"{self.t('cart')} ({sum(i['qty'] for i in self.cart_items)})", font=self.get_font(14, "bold"), fg_color="transparent", hover_color="#232F3E", text_color="white", command=lambda: self.navigate_to("cart"))
        self.btn_cart.pack(side="left", padx=5)
        
        self.btn_account = ctk.CTkButton(right_menu, text="", font=self.get_font(14, "bold"), fg_color="transparent", hover_color="#232F3E", text_color="white", command=self.handle_account_click)
        self.btn_account.pack(side="left", padx=5)
        self.update_top_badges()

    def filter_category_from_dropdown(self, choice):
        self.cat_var.set(" ☰ ") 
        self.filter_category(choice)

    def update_top_badges(self):
        self.btn_cart.configure(text=f"{self.t('cart')} ({sum(i['qty'] for i in self.cart_items)})")
        self.btn_fav.configure(text=f"{self.t('fav')} ({len(self.favorite_items)})")
        if self.current_user:
            name = self.user_profiles.get(self.current_user, {}).get("name", self.current_user)
            self.btn_account.configure(text=f"👤 {name}")
        else:
            self.btn_account.configure(text=self.t("account"))

    def handle_account_click(self):
        if self.current_user: self.navigate_to("account")
        else: self.navigate_to("login")

    def load_products(self):
        try:
            res = self.req_session.get(f"{SUPABASE_URL}/rest/v1/products?select=*", headers=HEADERS)
            if res.status_code == 200: self.all_products = res.json()
        except: pass

    def get_telegram_media_url(self, file_id):
        try:
            res = self.req_session.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}").json()
            if res.get("ok"):
                file_path = res['result']['file_path']
                url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
                is_video = file_path.lower().endswith(('.mp4', '.mov', '.avi'))
                return url, is_video
        except: pass
        return None, False

    def fetch_image_worker(self, file_id, size, label_widget, is_loading_flag):
        cache_key = f"{file_id}_{size[0]}x{size[1]}"
        if cache_key in self.image_cache:
            img = self.image_cache[cache_key]
        else:
            try:
                url, is_video = self.get_telegram_media_url(file_id)
                if not url: img = None
                elif is_video:
                    cap = cv2.VideoCapture(url)
                    ret, frame = cap.read()
                    cap.release()
                    if ret:
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        original_img = Image.fromarray(frame)
                        original_img.thumbnail(size, RESAMPLE_METHOD)
                        new_img = Image.new("RGBA", size, (255, 255, 255, 255))
                        new_img.paste(original_img, ((size[0] - original_img.width) // 2, (size[1] - original_img.height) // 2))
                        draw = ImageDraw.Draw(new_img)
                        cx, cy = size[0]//2, size[1]//2
                        draw.polygon([(cx-10, cy-15), (cx-10, cy+15), (cx+15, cy)], fill=(255, 255, 255, 200))
                        img = ctk.CTkImage(light_image=new_img, size=size)
                        self.image_cache[cache_key] = img
                    else: img = None
                else:
                    img_data = self.req_session.get(url).content
                    original_img = Image.open(io.BytesIO(img_data))
                    if original_img.mode in ("RGBA", "P"): original_img = original_img.convert("RGB")
                    original_img.thumbnail(size, RESAMPLE_METHOD)
                    new_img = Image.new("RGBA", size, (255, 255, 255, 255))
                    new_img.paste(original_img, ((size[0] - original_img.width) // 2, (size[1] - original_img.height) // 2))
                    img = ctk.CTkImage(light_image=new_img, size=size)
                    self.image_cache[cache_key] = img
            except: img = None
            
        is_loading_flag[0] = False
        try:
            if img: 
                self.root.after(0, lambda: label_widget.configure(image=img, text="") if label_widget.winfo_exists() else None)
            else: 
                self.root.after(0, lambda: label_widget.configure(image="", text="Error") if label_widget.winfo_exists() else None)
        except: pass

    def load_image_fast(self, label_widget, file_id, size):
        is_loading = [True]
        try: label_widget.configure(text="⏳", font=("Arial", 28), text_color="#BDC3C7")
        except: pass
        self.img_executor.submit(self.fetch_image_worker, file_id, size, label_widget, is_loading)

    def create_product_card(self, parent_frame, product, row, col, is_fav_page=False):
        card = ctk.CTkFrame(parent_frame, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#E5E7EB")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        img_lbl = ctk.CTkLabel(card, text="", font=self.get_font(12), text_color="gray", height=160, width=180, cursor="hand2")
        img_lbl.pack(padx=10, pady=(10, 5))
        img_lbl.bind("<Button-1>", lambda e, p=product: self.navigate_to("detail", p))
            
        if product.get("image_id"): self.load_image_fast(img_lbl, product.get("image_id"), size=(180, 160))
        else: img_lbl.configure(text="គ្មានរូបភាព", text_color="#BDC3C7", font=self.get_font(12))
        
        name = product.get("name", "N/A")
        price = float(product.get('price') or 0.0)
        
        name_lbl = ctk.CTkLabel(card, text=name if len(name) < 25 else name[:22] + "...", font=self.get_font(14, "bold"), text_color="#2C3E50", cursor="hand2")
        name_lbl.pack(anchor="w", padx=10)
        name_lbl.bind("<Button-1>", lambda e, p=product: self.navigate_to("detail", p))

        short_desc = product.get("short_desc", "")
        if short_desc:
            desc_lbl = ctk.CTkLabel(card, text=short_desc, font=self.get_font(11), text_color="#555555", justify="left", anchor="w", wraplength=180)
            desc_lbl.pack(anchor="w", padx=10, pady=(2, 2))
            desc_lbl.bind("<Button-1>", lambda e, p=product: self.navigate_to("detail", p))

        disc = float(product.get('discount_percent') or 0)
        price_frame = ctk.CTkFrame(card, fg_color="transparent")
        price_frame.pack(anchor="w", padx=10, pady=5)

        if disc > 0:
            real_price = price - (price * disc / 100)
            ctk.CTkLabel(price_frame, text=f"${real_price:,.2f}", font=("Arial", 16, "bold"), text_color="#B12704").pack(side="left")
            ctk.CTkLabel(price_frame, text=f"${price:,.2f}", font=("Arial", 12, "overstrike"), text_color="gray").pack(side="left", padx=5)
            ctk.CTkLabel(price_frame, text=f"-{int(disc)}%", font=("Arial", 11, "bold"), fg_color="transparent", text_color="red").pack(side="left", padx=2, ipadx=4)
        else:
            ctk.CTkLabel(price_frame, text=f"${price:,.2f}", font=("Arial", 16, "bold"), text_color="#B12704").pack(side="left")
        
        if is_fav_page:
            def remove_this():
                self.favorite_items = [p for p in self.favorite_items if str(p.get("id")) != str(product.get("id"))]
                self.save_local_data()
                self.update_top_badges()
                self.render_current_page()
            ctk.CTkButton(card, text=self.t("remove_fav"), font=self.get_font(12, "bold"), fg_color="#FDEDEC", hover_color="#FADBD8", text_color="#E74C3C", command=remove_this).pack(fill="x", padx=10, pady=(5, 10))
        else:
            ctk.CTkButton(card, text=self.t("detail"), font=self.get_font(12), fg_color="#F0F2F2", hover_color="#E3E6E6", text_color="black", command=lambda p=product: self.navigate_to("detail", p)).pack(fill="x", padx=10, pady=(5, 10))

    def display_products_grid(self, container, products_list, is_fav_page=False, items_per_row=5):
        for widget in container.winfo_children(): widget.destroy()
        if not products_list: return ctk.CTkLabel(container, text=self.t("no_data"), font=self.get_font(18), text_color="gray").pack(pady=50)
        for index, product in enumerate(products_list):
            self.create_product_card(container, product, index // items_per_row, index % items_per_row, is_fav_page)

    def render_home_page(self):
        home_frame = ctk.CTkFrame(self.body_container, fg_color="transparent")
        home_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ១. ផ្ទាំង Sidebar ចំណាត់ថ្នាក់ (រក្សានៅខាងឆ្វេង)
        sidebar = ctk.CTkFrame(home_frame, width=220, fg_color="#FFFFFF", corner_radius=10)
        sidebar.pack(side="left", fill="y", padx=(0, 10))
        ctk.CTkLabel(sidebar, text=self.t("category"), font=self.get_font(16, "bold"), text_color="#2C3E50").pack(pady=(20, 10), padx=20, anchor="w")
        
        for cat in [self.t("all"), "Laptop", "PC", "Monitor", "Accessories", "Other"]:
            ctk.CTkButton(sidebar, text=cat, font=self.get_font(14), fg_color="transparent", text_color="#34495E", hover_color="#F1F2F6", anchor="w", command=lambda c=cat: self.filter_category(c)).pack(fill="x", padx=10, pady=2)
            
        # ២. ប្រអប់ New Version Update (រក្សាទុកក្នុង Sidebar ផ្នែកខាងក្រោម)
        if getattr(self, 'pending_update_ver', None):
            self.update_box = ctk.CTkFrame(sidebar, fg_color="transparent", cursor="hand2")
            self.update_box.pack(side="bottom", pady=20)
            lbl_version = ctk.CTkLabel(self.update_box, text=f"New Version {self.pending_update_ver}", font=("Arial", 12), text_color="#333333")
            lbl_version.pack(pady=(0, 2))
            lbl_update = ctk.CTkLabel(self.update_box, text="🚀 Update Now", font=("Arial", 13, "bold"), text_color="#E74C3C")
            lbl_update.pack()
            
            def on_update_click(e): self.perform_auto_update(self.pending_update_url)
            lbl_version.bind("<Button-1>", on_update_click)
            lbl_update.bind("<Button-1>", on_update_click)
            self.update_box.bind("<Button-1>", on_update_click)
            
            shine_colors = ["#E74C3C", "#EC7063", "#F1948A", "#F5B7B1", "#FADBD8", "#FFFFFF", "#FADBD8", "#F5B7B1", "#F1948A", "#EC7063"]
            def animate_update_text(step=0):
                try:
                    if lbl_update.winfo_exists():
                        lbl_update.configure(text_color=shine_colors[step % len(shine_colors)])
                        self.root.after(400, lambda: animate_update_text(step + 1))
                except Exception:
                    pass 
            animate_update_text()
            
        # ៣. ផ្ទាំងបង្ហាញទំនិញ (ខាងស្តាំ)
        right_content = ctk.CTkScrollableFrame(home_frame, fg_color="transparent", scrollbar_button_color="#D5D8DC", scrollbar_button_hover_color="#ABB2B9")
        right_content.pack(side="left", fill="both", expand=True)

        is_default_view = (getattr(self, "current_category", self.t("all")) == self.t("all") and getattr(self, "search_query", "") == "")

        if is_default_view:
            promo_title_frame = ctk.CTkFrame(right_content, fg_color="transparent")
            promo_title_frame.pack(fill="x")
            ctk.CTkLabel(promo_title_frame, text="🔥 ប្រូម៉ូសិនពិសេស (Promotions)", font=self.get_font(14, "bold"), text_color="#B12704").pack(side="left", padx=10, pady=5)
            
            promo_grid = ctk.CTkFrame(right_content, fg_color="#F8F7F0", corner_radius=10)
            promo_grid.pack(fill="x", padx=10, pady=(0, 15))
            promo_list = [p for p in self.all_products if p.get('is_promotion') == True or float(p.get('discount_percent') or 0) > 0]
            promo_items = promo_list[:4] if len(promo_list) >= 4 else promo_list
            self.display_products_grid(promo_grid, promo_items)
            
            main_title_frame = ctk.CTkFrame(right_content, fg_color="transparent")
            main_title_frame.pack(fill="x")
            ctk.CTkLabel(main_title_frame, text="🛍️ ផលិតផលទាំងអស់ (All Products)", font=self.get_font(14, "bold"), text_color="#2C3E50").pack(side="left", padx=10, pady=5)
            display_list = self.all_products
        else:
            filter_title = ctk.CTkFrame(right_content, fg_color="transparent")
            filter_title.pack(fill="x")
            if self.search_query:
                lbl = f"🔍 លទ្ធផលស្វែងរក: '{self.search_query}'"
                display_list = [p for p in self.all_products if self.search_query in p.get("name", "").lower()]
            else:
                lbl = f"📂 ប្រភេទ: {self.current_category}"
                display_list = [p for p in self.all_products if p.get("category") == self.current_category]
            ctk.CTkLabel(filter_title, text=lbl, font=self.get_font(18, "bold"), text_color="#2C3E50").pack(side="left", padx=10, pady=5)

        self.grid_frame = ctk.CTkFrame(right_content, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)
        
        # Pagination Setup
        if not hasattr(self, 'current_page'): self.current_page = 0
        items_per_page = 10
        start_idx = self.current_page * items_per_page
        end_idx = start_idx + items_per_page
        
        self.display_products_grid(self.grid_frame, display_list[start_idx:end_idx], items_per_row=5)
        
        pag_frame = ctk.CTkFrame(right_content, fg_color="transparent")
        pag_frame.pack(pady=20)
        
        if self.current_page > 0:
            ctk.CTkButton(pag_frame, text="⬅ Back", font=self.get_font(14, "bold"), width=100, command=lambda: self.change_page(-1)).pack(side="left", padx=10)
            
        if end_idx < len(display_list):
            ctk.CTkButton(pag_frame, text="Next ➡", font=self.get_font(14, "bold"), width=100, command=lambda: self.change_page(1)).pack(side="left", padx=10)

    def filter_category(self, category_name):
        self.current_category = category_name
        self.search_query = ""
        self.current_page = 0
        self.navigate_to("home")

    def search_products(self):
        q = self.entry_search.get().lower()
        if q == self.t("search").lower() or q == "": self.search_query = ""
        else: self.search_query = q
        self.current_category = self.t("all")
        self.current_page = 0
        self.navigate_to("home")

    def render_recent_page(self):
        frame = ctk.CTkFrame(self.body_container, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkButton(frame, text=self.t("back"), font=self.get_font(14), fg_color="transparent", text_color="#3498DB", hover_color="#F0F2F2", anchor="w", command=self.go_back).pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(frame, text=self.t("recent"), font=self.get_font(20, "bold")).pack(anchor="w", pady=10)
        grid = ctk.CTkScrollableFrame(frame, fg_color="transparent", scrollbar_button_color="#D5D8DC", scrollbar_button_hover_color="#ABB2B9")
        grid.pack(fill="both", expand=True)
        inner_grid = ctk.CTkFrame(grid, fg_color="transparent")
        inner_grid.pack(fill="both", expand=True)
        self.display_products_grid(inner_grid, self.recent_items)

    def render_favorites_page(self):
        frame = ctk.CTkFrame(self.body_container, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkButton(frame, text=self.t("back"), font=self.get_font(14), fg_color="transparent", text_color="#3498DB", hover_color="#F0F2F2", anchor="w", command=self.go_back).pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(frame, text=self.t("fav"), font=self.get_font(20, "bold")).pack(anchor="w", pady=10)
        grid = ctk.CTkScrollableFrame(frame, fg_color="transparent", scrollbar_button_color="#D5D8DC", scrollbar_button_hover_color="#ABB2B9")
        grid.pack(fill="both", expand=True)
        inner_grid = ctk.CTkFrame(grid, fg_color="transparent")
        inner_grid.pack(fill="both", expand=True)
        self.display_products_grid(inner_grid, self.favorite_items, is_fav_page=True)

    def render_login_page(self):
        frame = ctk.CTkFrame(self.body_container, fg_color="transparent")
        frame.pack(fill="both", expand=True)
        box = ctk.CTkFrame(frame, width=400, height=450, fg_color="#FFFFFF", corner_radius=15)
        box.place(relx=0.5, rely=0.5, anchor="center")
        box.pack_propagate(False)
        
        ctk.CTkButton(box, text=self.t("back"), font=self.get_font(12), fg_color="transparent", text_color="#3498DB", hover_color="#F0F2F2", command=self.go_back).pack(anchor="w", padx=10, pady=10)
        ctk.CTkLabel(box, text=self.t("login"), font=self.get_font(24, "bold"), text_color="#2C3E50").pack(pady=(10, 20))
        
        e_em = ctk.CTkEntry(box, placeholder_text=self.t("email"), width=300, height=45, font=("Arial", 14))
        e_em.pack(pady=10)
        e_pw = ctk.CTkEntry(box, placeholder_text=self.t("password"), width=300, height=45, font=("Arial", 14), show="*")
        e_pw.pack(pady=10)
        
        def do_login():
            if not e_em.get() or not e_pw.get(): return
            try:
                res = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_ANON_KEY}, json={"email": e_em.get(), "password": e_pw.get()})
                if res.status_code == 200:
                    self.current_user = e_em.get()
                    if not hasattr(self, "user_carts"): self.user_carts = {}
                    if not hasattr(self, "user_favorites"): self.user_favorites = {}
                    self.cart_items = self.user_carts.get(self.current_user, [])
                    self.favorite_items = self.user_favorites.get(self.current_user, [])
                    self.save_local_data()
                    self.update_top_badges()
                    self.go_back()
                else: messagebox.showerror("បរាជ័យ", "ចូលមិនបានជោគជ័យ: អ៊ីមែល ឬលេខកូដខុស")
            except Exception as e: messagebox.showerror("Error", str(e))
            
        ctk.CTkButton(box, text=self.t("login"), font=self.get_font(16, "bold"), width=300, height=45, fg_color="#3498DB", hover_color="#2980B9", command=do_login).pack(pady=10)
        ctk.CTkButton(box, text=self.t("register"), font=self.get_font(14), fg_color="transparent", text_color="#8E44AD", command=lambda: self.navigate_to("register")).pack()
        ctk.CTkButton(box, text="ភ្លេចពាក្យសម្ងាត់? (Forgot Password)", font=self.get_font(12), fg_color="transparent", text_color="#E74C3C", command=lambda: self.navigate_to("forgot_password")).pack(pady=(5, 0))

    def render_register_page(self):
        frame = ctk.CTkFrame(self.body_container, fg_color="transparent")
        frame.pack(fill="both", expand=True)
        box = ctk.CTkFrame(frame, width=400, height=550, fg_color="#FFFFFF", corner_radius=15)
        box.place(relx=0.5, rely=0.5, anchor="center")
        box.pack_propagate(False)
        
        ctk.CTkButton(box, text=self.t("back"), font=self.get_font(12), fg_color="transparent", text_color="#3498DB", hover_color="#F0F2F2", command=self.go_back).pack(anchor="w", padx=10, pady=10)
        ctk.CTkLabel(box, text=self.t("register"), font=self.get_font(24, "bold"), text_color="#2C3E50").pack(pady=(5, 15))
        
        e_name = ctk.CTkEntry(box, placeholder_text="ឈ្មោះអ្នកប្រើប្រាស់ (Full Name)", width=300, height=45, font=self.get_font(14))
        e_name.pack(pady=8)
        e_em = ctk.CTkEntry(box, placeholder_text=self.t("email"), width=300, height=45, font=("Arial", 14))
        e_em.pack(pady=8)
        e_pw = ctk.CTkEntry(box, placeholder_text=self.t("password"), width=300, height=45, font=("Arial", 14), show="*")
        e_pw.pack(pady=8)
        e_cpw = ctk.CTkEntry(box, placeholder_text=self.t("confirm_password"), width=300, height=45, font=self.get_font(14), show="*")
        e_cpw.pack(pady=8)
        
        def do_reg():
            if not e_name.get() or not e_em.get() or not e_pw.get() or not e_cpw.get(): return messagebox.showwarning("បញ្ហា", "បំពេញព័ត៌មានអោយគ្រប់!")
            if e_pw.get() != e_cpw.get(): return messagebox.showwarning("បញ្ហា", "ពាក្យសម្ងាត់មិនត្រូវគ្នាទេ!")
            try:
                res = requests.post(f"{SUPABASE_URL}/auth/v1/signup", headers={"apikey": SUPABASE_ANON_KEY}, json={"email": e_em.get(), "password": e_pw.get()})
                if res.status_code == 200: 
                    if not hasattr(self, "user_profiles"): self.user_profiles = {}
                    self.user_profiles[e_em.get()] = {"name": e_name.get(), "phone": "", "address": ""}
                    self.save_local_data()
                    messagebox.showinfo("ជោគជ័យ", "បង្កើតគណនីរួចរាល់ សូមចូលគណនី (Login)")
                    self.navigate_to("login")
                elif res.status_code == 429:
                    messagebox.showerror("ចំណាំ (Rate Limit)", "ប្រព័ន្ធ Supabase កំណត់ការបង្កើតគណនីបានត្រឹម ៣ដង/ម៉ោងប៉ុណ្ណោះ។\n\nសូមរង់ចាំ។")
                else: messagebox.showerror("បរាជ័យ", f"មិនអាចចុះឈ្មោះបានទេ: {res.json().get('msg')}")
            except Exception as e: messagebox.showerror("Error", str(e))
            
        ctk.CTkButton(box, text=self.t("register"), font=self.get_font(16, "bold"), width=300, height=45, fg_color="#2ECC71", hover_color="#27AE60", command=do_reg).pack(pady=15)

    def render_forgot_password_page(self):
        frame = ctk.CTkFrame(self.body_container, fg_color="transparent")
        frame.pack(fill="both", expand=True)
        box = ctk.CTkFrame(frame, width=400, height=350, fg_color="#FFFFFF", corner_radius=15)
        box.place(relx=0.5, rely=0.5, anchor="center")
        box.pack_propagate(False)
        ctk.CTkButton(box, text=self.t("back"), font=self.get_font(12), fg_color="transparent", text_color="#3498DB", hover_color="#F0F2F2", command=self.go_back).pack(anchor="w", padx=10, pady=10)
        ctk.CTkLabel(box, text="ភ្លេចពាក្យសម្ងាត់", font=self.get_font(24, "bold"), text_color="#2C3E50").pack(pady=(10, 20))
        e_em = ctk.CTkEntry(box, placeholder_text=self.t("email"), width=300, height=45, font=("Arial", 14))
        e_em.pack(pady=10)
        def do_reset():
            email = e_em.get().strip()
            if not email: return messagebox.showwarning("បញ្ហា", "សូមបញ្ចូលអ៊ីមែលរបស់អ្នកជាមុនសិន!")
            try:
                res = requests.post(f"{SUPABASE_URL}/auth/v1/recover", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email})
                if res.status_code == 200: 
                    messagebox.showinfo("ជោគជ័យ", "តំណភ្ជាប់សម្រាប់កំណត់ពាក្យសម្ងាត់ថ្មី (Reset Password) ត្រូវបានផ្ញើទៅកាន់អ៊ីមែលរបស់អ្នកហើយ។\n\nសូមពិនិត្យមើលប្រអប់សារ (Inbox) ឬ Spam របស់អ្នក។")
                    self.go_back()
                else: messagebox.showerror("បរាជ័យ", f"មិនអាចផ្ញើសារបានទេ: {res.json().get('msg')}")
            except Exception as e: messagebox.showerror("Error", str(e))
        ctk.CTkButton(box, text="ផ្ញើអ៊ីមែលសង្គ្រោះ", font=self.get_font(16, "bold"), width=300, height=45, fg_color="#E67E22", hover_color="#D35400", command=do_reset).pack(pady=20)

    def render_account_page(self):
        frame = ctk.CTkFrame(self.body_container, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=50, pady=30)
        
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        
        ctk.CTkButton(header, text=self.t("back"), font=self.get_font(14), fg_color="transparent", text_color="#3498DB", hover_color="#F0F2F2", command=self.go_back).pack(side="left")
        
        name = self.user_profiles.get(self.current_user, {}).get("name", self.current_user) if self.current_user else "Unknown"
        # 1. បង្ហាញឈ្មោះ
        ctk.CTkLabel(header, text=f"👤 គណនី: {name}", font=("Arial", 14, "bold"), text_color="#2C3E50").pack(side="left", padx=(20, 2))

# 2. បង្ហាញសញ្ញា Blue Tick (✔) នៅជាប់កន្ទុយឈ្មោះ
        ctk.CTkLabel(header, text="✔", font=("Arial", 14, "bold"), text_color="#1DA1F2").pack(side="left")
        
        def logout():
            if self.current_user:
                if not hasattr(self, "user_carts"): self.user_carts = {}
                if not hasattr(self, "user_favorites"): self.user_favorites = {}
                self.user_carts[self.current_user] = self.cart_items
                self.user_favorites[self.current_user] = self.favorite_items
                
            self.cart_items, self.favorite_items, self.current_user = [], [], None
            if os.path.exists("local_user_data.json"):
                try: os.remove("local_user_data.json")
                except: pass
            self.save_local_data()
            self.update_top_badges()
            self.navigate_to("home")
            
        ctk.CTkButton(header, text=self.t("logout"), font=self.get_font(14), fg_color="#E74C3C", hover_color="#C0392B", command=logout).pack(side="right")
        
        split_frame = ctk.CTkFrame(frame, fg_color="transparent")
        split_frame.pack(fill="both", expand=True, pady=10)

        left_col = ctk.CTkScrollableFrame(split_frame, fg_color="transparent", scrollbar_button_color="#D5D8DC", scrollbar_button_hover_color="#ABB2B9")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 20))

        right_col = ctk.CTkScrollableFrame(split_frame, fg_color="transparent", scrollbar_button_color="#D5D8DC", scrollbar_button_hover_color="#ABB2B9")
        right_col.pack(side="left", fill="both", expand=True, padx=(20, 0))

        profile_card = ctk.CTkFrame(left_col, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#E5E7EB")
        profile_card.pack(fill="x", pady=(0, 15))
        
        p_inner = ctk.CTkFrame(profile_card, fg_color="transparent")
        p_inner.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(p_inner, text="ព័ត៌មានផ្ទាល់ខ្លួន (Profile Info)", font=self.get_font(18, "bold"), text_color="#2C3E50").pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(p_inner, text=f"📧 អ៊ីមែល: {self.current_user}", font=("Arial", 14), text_color="gray").pack(anchor="w", pady=(0, 15))

        dynamic_profile_area = ctk.CTkFrame(p_inner, fg_color="transparent")
        dynamic_profile_area.pack(fill="x")

        def render_profile_ui(is_editing=False):
            for widget in dynamic_profile_area.winfo_children(): widget.destroy()

            if not hasattr(self, "user_profiles"): self.user_profiles = {}
            curr_profile = self.user_profiles.get(self.current_user, {})
            name = curr_profile.get("name", "")
            phone = curr_profile.get("phone", "")
            address = curr_profile.get("address", "")

            if is_editing or not name:
                e_name = ctk.CTkEntry(dynamic_profile_area, placeholder_text="ឈ្មោះ (Name)", width=350, height=45, font=self.get_font(14))
                e_name.pack(anchor="w", pady=5)
                e_name.insert(0, name)
                
                e_phone = ctk.CTkEntry(dynamic_profile_area, placeholder_text="លេខទូរស័ព្ទ (Phone)", width=350, height=45, font=("Arial", 14))
                e_phone.pack(anchor="w", pady=5)
                e_phone.insert(0, phone)
                
                e_address = ctk.CTkEntry(dynamic_profile_area, placeholder_text="អាស័យដ្ឋាន (Address)", width=350, height=45, font=self.get_font(14))
                e_address.pack(anchor="w", pady=5)
                e_address.insert(0, address)
                
                def save_profile():
                    self.user_profiles[self.current_user] = {"name": e_name.get(), "phone": e_phone.get(), "address": e_address.get()}
                    self.save_local_data()
                    render_profile_ui(is_editing=False) 
                    self.update_top_badges()
                    
                btn_frame = ctk.CTkFrame(dynamic_profile_area, fg_color="transparent")
                btn_frame.pack(anchor="w", pady=10)
                ctk.CTkButton(btn_frame, text="រក្សាទុក", font=self.get_font(14, "bold"), width=150, height=40, fg_color="#2ECC71", hover_color="#27AE60", command=save_profile).pack(side="left")
                if name: 
                    ctk.CTkButton(btn_frame, text="បោះបង់", font=self.get_font(14), width=100, height=40, fg_color="#E74C3C", command=lambda: render_profile_ui(is_editing=False)).pack(side="left", padx=10)
            else:
                ctk.CTkLabel(dynamic_profile_area, text=f"👤 ឈ្មោះ: {name}", font=self.get_font(15)).pack(anchor="w", pady=4)
                ctk.CTkLabel(dynamic_profile_area, text=f"📞 ទូរស័ព្ទ: {phone if phone else 'មិនទាន់បញ្ជាក់'}", font=self.get_font(15), text_color="black" if phone else "gray").pack(anchor="w", pady=4)
                ctk.CTkLabel(dynamic_profile_area, text=f"📍 អាស័យដ្ឋាន: {address if address else 'មិនទាន់បញ្ជាក់'}", font=self.get_font(15), text_color="black" if address else "gray").pack(anchor="w", pady=4)
                
                ctk.CTkButton(dynamic_profile_area, text="✏️ កែប្រែព័ត៌មាន", font=self.get_font(14), fg_color="#F39C12", hover_color="#D35400", width=150, height=35, command=lambda: render_profile_ui(is_editing=True)).pack(anchor="w", pady=(15, 0))
                
        render_profile_ui()

        pwd_card = ctk.CTkFrame(left_col, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#E5E7EB")
        pwd_card.pack(fill="x", pady=(0, 15))
        
        pw_inner = ctk.CTkFrame(pwd_card, fg_color="transparent")
        pw_inner.pack(fill="both", expand=True, padx=25, pady=25)
        
        ctk.CTkLabel(pw_inner, text="ផ្លាស់ប្តូរពាក្យសម្ងាត់ថ្មី (Change Password)", font=self.get_font(18, "bold"), text_color="#2C3E50").pack(anchor="w", pady=(0, 10))
        e_old_pw = ctk.CTkEntry(pw_inner, placeholder_text="លេខកូដចាស់ (Old Password)", width=350, height=45, font=("Arial", 14), show="*")
        e_old_pw.pack(anchor="w", pady=5)
        e_new_pw = ctk.CTkEntry(pw_inner, placeholder_text="លេខកូដថ្មី (New Password)", width=350, height=45, font=("Arial", 14), show="*")
        e_new_pw.pack(anchor="w", pady=5)
        
        def update_password():
            old_pw = e_old_pw.get(); new_pw = e_new_pw.get()
            if not old_pw or not new_pw: return messagebox.showwarning("បញ្ហា", "សូមបញ្ចូលលេខកូដទាំងចាស់ និងថ្មីឲ្យបានគ្រប់គ្រាន់!")
            if len(new_pw) < 6: return messagebox.showwarning("បញ្ហា", "លេខកូដថ្មីត្រូវមានយ៉ាងហោចណាស់ ៦ ខ្ទង់!")
            try:
                login_res = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_ANON_KEY}, json={"email": self.current_user, "password": old_pw})
                if login_res.status_code == 200:
                    access_token = login_res.json().get("access_token")
                    update_res = requests.put(f"{SUPABASE_URL}/auth/v1/user", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {access_token}"}, json={"password": new_pw})
                    if update_res.status_code == 200:
                        messagebox.showinfo("ជោគជ័យ", "លេខកូដសម្ងាត់ត្រូវបានផ្លាស់ប្តូរដោយជោគជ័យ!")
                        e_old_pw.delete(0, 'end'); e_new_pw.delete(0, 'end')
                    else: messagebox.showerror("បរាជ័យ", f"មិនអាចប្តូរលេខកូដបានទេ: {update_res.json().get('msg')}")
                else: messagebox.showerror("បរាជ័យ", "លេខកូដចាស់មិនត្រឹមត្រូវទេ!")
            except Exception as e: messagebox.showerror("Error", str(e))
                
        ctk.CTkButton(pw_inner, text="រក្សាទុកលេខកូដថ្មី", font=self.get_font(14, "bold"), width=200, height=40, fg_color="#3498DB", hover_color="#2980B9", command=update_password).pack(anchor="w", pady=(15, 0))

        history_frame = ctk.CTkFrame(right_col, fg_color="transparent")
        history_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(history_frame, text="📦 ប្រវត្តិការទិញទំនិញរបស់អ្នក", font=self.get_font(18, "bold"), text_color="#2C3E50").pack(anchor="w", padx=5, pady=(0, 10))
        
        user_orders = getattr(self, "order_history", {}).get(self.current_user, [])
        if not user_orders: 
            ctk.CTkLabel(history_frame, text="អ្នកមិនទាន់មានប្រវត្តិទិញទំនិញនៅឡើយទេ", font=self.get_font(16), text_color="gray").pack(pady=20, padx=5, anchor="w")
        else:
            for order in user_orders:
                card = ctk.CTkFrame(history_frame, fg_color="#FFFFFF", border_width=1, corner_radius=8, border_color="#E5E7EB")
                card.pack(fill="x", pady=6, padx=5)
                
                top_row = ctk.CTkFrame(card, fg_color="transparent")
                top_row.pack(fill="x", padx=20, pady=(15, 5))
                ctk.CTkLabel(top_row, text=f"📅 {order.get('date')}", font=self.get_font(12, "bold"), text_color="#34495E").pack(side="left")
                ctk.CTkLabel(top_row, text=f"{self.t('total')} ${order.get('total'):,.2f}", font=("Arial", 14, "bold"), text_color="#B12704").pack(side="right")
                
                item_text = "\n".join([f"• {i['name']} (x{i['qty']}) = ${i['price']*i['qty']:,.2f}" for i in order.get('items', [])])
                # បន្ថយ pady ពី 20 មក 15 ដើម្បីអោយកៀកនឹង Tracking Bar
                ctk.CTkLabel(card, text=item_text, font=self.get_font(14), text_color="#555555", justify="left").pack(anchor="w", padx=20, pady=(0, 15))

                # === កូដថ្មី សម្រាប់របារតាមដានទំនិញ (Tracking Timeline) ===
                status = order.get("status", "pending") # ទាញយក status ពី order, បើគ្មាន យក "pending"
                status_frame = ctk.CTkFrame(card, fg_color="#F8F9FA", corner_radius=5)
                status_frame.pack(fill="x", padx=20, pady=(0, 15), ipadx=10, ipady=10)

                # ដំណាក់កាលទាំង ៤
                stages = [
                    ("pending", "⏳ រង់ចាំបញ្ជាក់"),
                    ("confirmed", "📦 រៀបចំទំនិញ"),
                    ("shipping", "🚚 កំពុងដឹក"),
                    ("completed", "✅ ទទួលបាន")
                ]

                # ស្វែងរកទីតាំងស្ថានភាពបច្ចុប្បន្ន
                current_idx = 0
                for i, (st, _) in enumerate(stages):
                    if st == status: current_idx = i

                # គូររបារដំណាក់កាល
                for i, (st, label) in enumerate(stages):
                    # បើឆ្លងកាត់ហើយ លោតពណ៌បៃតង បើមិនទាន់ ពណ៌ប្រផេះ
                    color = "#2ECC71" if i <= current_idx else "#BDC3C7"
                    font_weight = "bold" if i == current_idx else "normal"
                    
                    lbl = ctk.CTkLabel(status_frame, text=label, font=self.get_font(13, font_weight), text_color=color)
                    lbl.pack(side="left", expand=True)
                    
                    if i < len(stages) - 1:
                        ctk.CTkLabel(status_frame, text=" ➔ ", font=("Arial", 12, "bold"), text_color="#E5E7EB").pack(side="left")

    def render_detail_page(self, product):
        try:
            self.add_to_recent(product) 
            detail_page = ctk.CTkFrame(self.body_container, fg_color="#FFFFFF")
            detail_page.pack(fill="both", expand=True, padx=10, pady=10)
            
            price = float(product.get('price') or 0.0)
            stock = int(product.get('stock_quantity') or 0)
            
            ctk.CTkButton(detail_page, text=self.t("back"), font=self.get_font(14), fg_color="transparent", text_color="#3498DB", hover_color="#F0F2F2", anchor="w", command=self.go_back).pack(anchor="w", padx=10, pady=10)
            split_frame = ctk.CTkFrame(detail_page, fg_color="transparent")
            split_frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            left_col = ctk.CTkFrame(split_frame, fg_color="transparent", width=450)
            left_col.pack(side="left", fill="y", padx=(10, 20))
            left_col.pack_propagate(False) 

            main_img_lbl = ctk.CTkLabel(left_col, text="", width=420, height=420, fg_color="#F8F9FA", cursor="hand2")
            main_img_lbl.pack(pady=(0, 15))
            gallery_container = ctk.CTkFrame(left_col, fg_color="transparent")
            gallery_container.pack(fill="x")

            all_fids = []
            if product.get("image_id"): all_fids.append(str(product.get("image_id")))
            img_ids_raw = product.get("image_ids")
            if isinstance(img_ids_raw, str) and img_ids_raw.strip(): all_fids.extend(img_ids_raw.split(","))
            elif isinstance(img_ids_raw, list): all_fids.extend([str(x) for x in img_ids_raw])
            all_fids = list(dict.fromkeys([f.strip() for f in all_fids if f and str(f).strip()]))
            
            current_fid = {"id": all_fids[0] if all_fids else None}
            
            def set_main(fid):
                current_fid["id"] = fid
                self.stop_video()
                
                is_loading = [True]
                def animate_loading(count=0):
                    if not is_loading[0]: return
                    try:
                        main_img_lbl.configure(image=self.spinner_frames[count % 12], text=" Loading...", compound="center")
                        self.root.after(80, animate_loading, count + 1)
                    except: pass
                animate_loading()

                def fetch_main():
                    url, is_video = self.get_telegram_media_url(fid)
                    is_loading[0] = False
                    if not url: return
                    
                    if is_video:
                        cap = cv2.VideoCapture(url)
                        self.playing_video["cap"] = cap
                        self.playing_video["running"] = True
                        
                        def update_video_frame():
                            if not self.playing_video["running"]: return
                            ret, frame = cap.read()
                            if not ret:
                                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                                ret, frame = cap.read()
                            if ret:
                                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                img = Image.fromarray(frame)
                                img.thumbnail((420, 420), RESAMPLE_METHOD)
                                bg = Image.new("RGBA", (420, 420), (0, 0, 0, 255))
                                bg.paste(img, ((420 - img.width) // 2, (420 - img.height) // 2))
                                ctk_img = ctk.CTkImage(light_image=bg, size=(420, 420))
                                try:
                                    main_img_lbl.configure(image=ctk_img, text="")
                                    self.root.after(33, update_video_frame)
                                except: self.stop_video()
                            else: self.stop_video()
                        self.root.after(0, update_video_frame)
                    else:
                        img_data = self.req_session.get(url).content
                        raw = Image.open(io.BytesIO(img_data))
                        if raw.mode in ("RGBA", "P"): raw = raw.convert("RGB")
                        raw.thumbnail((420, 420), RESAMPLE_METHOD)
                        bg = Image.new("RGBA", (420, 420), (255, 255, 255, 255))
                        bg.paste(raw, ((420 - raw.width) // 2, (420 - raw.height) // 2))
                        ctk_img = ctk.CTkImage(light_image=bg, size=(420, 420))
                        self.root.after(0, lambda: main_img_lbl.configure(image=ctk_img, text=""))
                        
                threading.Thread(target=fetch_main, daemon=True).start()

            if all_fids:
                set_main(all_fids[0])
                for fid in all_fids[:4]:
                    thumb = ctk.CTkLabel(gallery_container, text="", width=80, height=80, fg_color="#E0E0E0", cursor="hand2")
                    thumb.pack(side="left", padx=5)
                    self.load_image_fast(thumb, fid, size=(80, 80))
                    thumb.bind("<Button-1>", lambda e, f=fid: set_main(f)) 

            def view_full(e):
                if not current_fid["id"]: return
                overlay = ctk.CTkFrame(self.root, fg_color="#000000", corner_radius=0)
                overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
                canvas = tk.Canvas(overlay, bg="#000000", highlightthickness=0, cursor="fleur")
                canvas.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)
                
                is_playing_full = [False]
                full_cap = [None]
                
                def close_overlay():
                    is_playing_full[0] = False
                    if full_cap[0]: full_cap[0].release()
                    overlay.destroy()
                    
                ctk.CTkButton(overlay, text="❌ Close", font=("Arial", 16, "bold"), fg_color="#E74C3C", hover_color="#C0392B", command=close_overlay).place(relx=0.95, rely=0.05, anchor="ne")
                lbl_stat = ctk.CTkLabel(overlay, text="", font=self.get_font(16, "bold"), text_color="#3498DB")
                lbl_stat.place(relx=0.5, rely=0.5, anchor="center")
                lbl_stat.lift() 
                
                is_loading = [True]
                def animate_zoom(count=0):
                    if not is_loading[0]: return
                    try: 
                        lbl_stat.configure(image=self.spinner_frames[count % 12], text=" Loading...", compound="left")
                        self.root.after(80, animate_zoom, count + 1)
                    except: pass
                animate_zoom()
                
                canvas.scale = 1.0
                def load_draw():
                    url, is_video = self.get_telegram_media_url(current_fid['id'])
                    if not url: return
                    
                    if is_video:
                        full_cap[0] = cv2.VideoCapture(url)
                        is_playing_full[0] = True
                        ret, frame = full_cap[0].read()
                        if ret:
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            canvas.raw_image = Image.fromarray(frame)
                            canvas.scale = min(overlay.winfo_width()/canvas.raw_image.width, (overlay.winfo_height()-70)/canvas.raw_image.height)*0.9 
                        
                        def loop_video():
                            if not is_playing_full[0]: return
                            ret, f = full_cap[0].read()
                            if not ret:
                                full_cap[0].set(cv2.CAP_PROP_POS_FRAMES, 0)
                                ret, f = full_cap[0].read()
                            if ret:
                                f = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
                                canvas.raw_image = Image.fromarray(f)
                                draw()
                                overlay.after(33, loop_video)
                        
                        is_loading[0] = False
                        try: self.root.after(0, lbl_stat.destroy)
                        except: pass
                        self.root.after(0, loop_video)
                    else:
                        try:
                            raw = Image.open(io.BytesIO(self.req_session.get(url).content))
                            if raw.mode in ("RGBA", "P"): raw = raw.convert("RGB")
                            is_loading[0] = False; canvas.raw_image = raw
                            try: self.root.after(0, lbl_stat.destroy)
                            except: pass
                            def render_first_time():
                                canvas.scale = min(overlay.winfo_width()/raw.width, (overlay.winfo_height()-70)/raw.height)*0.9 
                                draw()
                            self.root.after(0, render_first_time)
                        except: is_loading[0] = False

                def draw():
                    if not getattr(canvas, 'raw_image', None): return
                    w, h = int(canvas.raw_image.width * canvas.scale), int(canvas.raw_image.height * canvas.scale)
                    if w < 100 or h < 100: return
                    canvas.image_ref = ImageTk.PhotoImage(canvas.raw_image.resize((w, h), RESAMPLE_METHOD))
                    canvas.delete("all")
                    canvas.create_image(canvas.winfo_width()//2, canvas.winfo_height()//2, anchor="center", image=canvas.image_ref)
                    
                def zoom(ev): canvas.scale *= 1.15 if ev.delta > 0 or ev.num == 4 else 0.85; draw()
                canvas.bind("<MouseWheel>", zoom); canvas.bind("<Button-4>", zoom); canvas.bind("<Button-5>", zoom)
                canvas.bind("<ButtonPress-1>", lambda ev: canvas.scan_mark(ev.x, ev.y)); canvas.bind("<B1-Motion>", lambda ev: canvas.scan_dragto(ev.x, ev.y, gain=1))
                self.img_executor.submit(load_draw)
                
            main_img_lbl.bind("<Button-1>", view_full)

            right_col = ctk.CTkScrollableFrame(split_frame, fg_color="transparent", scrollbar_button_color="#D5D8DC", scrollbar_button_hover_color="#ABB2B9")
            right_col.pack(side="left", fill="both", expand=True)

            ctk.CTkLabel(right_col, text=product.get("name", "N/A"), font=self.get_font(24, "bold"), text_color="black", wraplength=550).pack(anchor="w", pady=(0, 5))
            
            cat_brand_frame = ctk.CTkFrame(right_col, fg_color="transparent")
            cat_brand_frame.pack(anchor="w", pady=(0, 10))
            ctk.CTkLabel(cat_brand_frame, text=f"ប្រភេទ: {product.get('category', 'N/A')}", font=self.get_font(14), fg_color="#F0F2F2", corner_radius=5).pack(side="left", padx=(0, 10), ipady=2, ipadx=5)
            ctk.CTkLabel(cat_brand_frame, text=f"ម៉ាក: {product.get('brand', 'N/A')}", font=self.get_font(14), fg_color="#F0F2F2", corner_radius=5).pack(side="left", ipady=2, ipadx=5)
            
            ctk.CTkLabel(right_col, text=f"${price:,.2f}", font=("Arial", 30, "bold"), text_color="#B12704").pack(anchor="w", pady=(0, 10))
            ctk.CTkLabel(right_col, text=f"{self.t('stock')} {stock}" if stock > 0 else self.t("out_stock"), font=self.get_font(16), text_color="#007600" if stock > 0 else "#B12704").pack(anchor="w", pady=(0, 10))
            
            qty_frame = ctk.CTkFrame(right_col, fg_color="transparent")
            qty_frame.pack(anchor="w", pady=(5, 10))
            ctk.CTkLabel(qty_frame, text=self.t("qty"), font=self.get_font(16, "bold"), text_color="black").pack(side="left", padx=(0, 10))
            
            selected_qty = tk.IntVar(value=1)
            ctk.CTkButton(qty_frame, text="-", width=40, height=40, fg_color="#F3F4F6", text_color="black", command=lambda: selected_qty.set(selected_qty.get() - 1) if selected_qty.get() > 1 else None).pack(side="left")
            ctk.CTkLabel(qty_frame, textvariable=selected_qty, font=("Arial", 18, "bold"), width=50, text_color="black").pack(side="left", padx=5)
            ctk.CTkButton(qty_frame, text="+", width=40, height=40, fg_color="#F3F4F6", text_color="black", command=lambda: selected_qty.set(selected_qty.get() + 1) if selected_qty.get() < stock else None).pack(side="left")

            btn_action_frame = ctk.CTkFrame(right_col, fg_color="transparent")
            btn_action_frame.pack(anchor="w", pady=(10, 20))

            def add_to_cart():
                if not self.current_user:
                    messagebox.showinfo("ជូនដំណឹង", "សូមធ្វើការចូលគណនី (Login) ជាមុនសិន ដើម្បីអាចដាក់ទំនិញចូលកន្ត្រកបាន!")
                    self.navigate_to("login")
                    return

                if stock <= 0: return
                qty = selected_qty.get()
                existing = next((item for item in self.cart_items if str(item["product"].get("id")) == str(product.get('id'))), None)
                if existing: existing["qty"] += qty
                else: self.cart_items.append({"product": product, "qty": qty})
                self.save_local_data()
                self.update_top_badges()

            btn_fav = ctk.CTkButton(btn_action_frame, text="", font=("Arial", 18), fg_color="#F3F4F6", border_width=1, height=45)
            def update_fav_btn():
                is_fav = any(str(p.get("id")) == str(product.get("id")) for p in self.favorite_items)
                btn_fav.configure(text="❤️" if is_fav else "🤍", text_color="#E74C3C" if is_fav else "black")
                
            def toggle_fav():
                if not self.current_user:
                    messagebox.showinfo("ជូនដំណឹង", "សូមធ្វើការចូលគណនី (Login) ជាមុនសិន ដើម្បីអាចរក្សាទុកទំនិញជាចំណូលចិត្តបាន!")
                    self.navigate_to("login")
                    return

                if any(str(p.get("id")) == str(product.get("id")) for p in self.favorite_items):
                    self.favorite_items = [p for p in self.favorite_items if str(p.get("id")) != str(product.get("id"))]
                else: 
                    self.favorite_items.append(product)
                self.save_local_data()
                self.update_top_badges()
                update_fav_btn()

            btn_fav.configure(command=toggle_fav)
            ctk.CTkButton(btn_action_frame, text=self.t("add_cart"), font=self.get_font(16, "bold"), fg_color="#FFD814", hover_color="#F7CA00", text_color="black", width=200, height=45, command=add_to_cart).pack(side="left", padx=(0, 10))
            btn_fav.pack(side="left")
            update_fav_btn()

            ctk.CTkLabel(right_col, text=self.t("desc"), font=self.get_font(16, "bold"), text_color="black").pack(anchor="w", pady=(10, 5))
            ctk.CTkLabel(right_col, text=product.get("description", ""), font=self.get_font(14), text_color="#333", justify="left", wraplength=550).pack(anchor="w")

            specs_data = product.get("specs", {})
            if isinstance(specs_data, str):
                try: specs_data = json.loads(specs_data)
                except: specs_data = {}
            if isinstance(specs_data, dict) and specs_data:
                ctk.CTkLabel(right_col, text=self.t("specs"), font=self.get_font(16, "bold"), text_color="black").pack(anchor="w", pady=(20, 5))
                for k, v in specs_data.items():
                    row = ctk.CTkFrame(right_col, fg_color="transparent")
                    row.pack(fill="x", pady=2)
                    ctk.CTkLabel(row, text=f"• {k}: {v}", font=self.get_font(14), text_color="black").pack(side="left")

            ctk.CTkLabel(right_col, text=self.t("similar"), font=self.get_font(18, "bold"), text_color="black").pack(anchor="w", pady=(40, 10))
            sim_frame = ctk.CTkFrame(right_col, fg_color="transparent")
            sim_frame.pack(fill="x", pady=10)
            
            all_similar = [p for p in self.all_products if p.get('category') == product.get('category') and str(p.get('id')) != str(product.get('id'))]
            
            # បង្ហាញត្រឹម ៣ ផលិតផលក្នុងមួយជួរ
            self.display_products_grid(sim_frame, all_similar[:3], items_per_row=3)
            
            # បន្ថែមប៊ូតុង View More ពេលមានទំនិញលើសពី ៣
            if len(all_similar) > 3:
                ctk.CTkButton(right_col, text="មើលបន្ថែម (View More)", font=self.get_font(14, "bold"), fg_color="#3498DB", command=lambda: self.filter_category(product.get('category'))).pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", str(e)); self.go_back()

    def render_cart_page(self):
        cart_page = ctk.CTkFrame(self.body_container, fg_color="#F3F4F6")
        cart_page.pack(fill="both", expand=True, padx=10, pady=10)
        header = ctk.CTkFrame(cart_page, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(5, 15))
        ctk.CTkButton(header, text=self.t("back"), font=self.get_font(14), fg_color="transparent", text_color="#3498DB", command=self.go_back).pack(side="left")
        ctk.CTkLabel(header, text=self.t("cart"), font=self.get_font(22, "bold"), text_color="black").pack(side="left", padx=30)

        split = ctk.CTkFrame(cart_page, fg_color="transparent")
        split.pack(fill="both", expand=True, padx=10)
        left_cart = ctk.CTkScrollableFrame(split, fg_color="#FFFFFF", corner_radius=10, scrollbar_button_color="#D5D8DC", scrollbar_button_hover_color="#ABB2B9")
        left_cart.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right_checkout = ctk.CTkFrame(split, fg_color="#FFFFFF", corner_radius=10, width=400)
        right_checkout.pack(side="right", fill="y")
        right_checkout.pack_propagate(False)

        lbl_total = ctk.CTkLabel(right_checkout, text=f"{self.t('total')} $0.00", font=("Arial", 22, "bold"), text_color="#B12704")
        lbl_total.pack(pady=(20, 30))

        def refresh_cart():
            for w in left_cart.winfo_children(): w.destroy()
            if not self.cart_items:
                lbl_total.configure(text=f"{self.t('total')} $0.00")
                return ctk.CTkLabel(left_cart, text=self.t("no_data"), font=self.get_font(16), text_color="gray").pack(pady=50)

            total = 0
            for idx, item in enumerate(self.cart_items):
                p_data, qty = item["product"], item["qty"]
                price = float(p_data.get("price") or 0.0)
                stock = int(p_data.get("stock_quantity") or 0)
                sub = price * qty; total += sub
                
                row = ctk.CTkFrame(left_cart, fg_color="#F9FAFB", border_width=1, corner_radius=8)
                row.pack(fill="x", pady=5, padx=10)
                
                name_lbl = ctk.CTkLabel(row, text=p_data.get("name", "N/A"), font=self.get_font(14, "bold"), text_color="black", cursor="hand2")
                name_lbl.pack(anchor="w", padx=10, pady=(10, 5))
                name_lbl.bind("<Button-1>", lambda e, p=p_data: self.navigate_to("detail", p))

                bot = ctk.CTkFrame(row, fg_color="transparent")
                bot.pack(fill="x", padx=10, pady=(0, 10))
                ctk.CTkLabel(bot, text=f"${price:,.2f}", font=("Arial", 16), text_color="#555").pack(side="left")
                qbox = ctk.CTkFrame(bot, fg_color="transparent")
                qbox.pack(side="left", padx=40)
                
                def chg_q(i, amt, m_stk):
                    nq = self.cart_items[i]["qty"] + amt
                    if nq > m_stk or nq < 1: return
                    self.cart_items[i]["qty"] = nq
                    self.save_local_data(); self.update_top_badges(); refresh_cart()
                    
                ctk.CTkButton(qbox, text="-", width=35, height=30, fg_color="#E5E7EB", text_color="black", command=lambda i=idx, s=stock: chg_q(i, -1, s)).pack(side="left")
                ctk.CTkLabel(qbox, text=str(qty), font=("Arial", 16, "bold"), width=40, text_color="black").pack(side="left")
                ctk.CTkButton(qbox, text="+", width=35, height=30, fg_color="#E5E7EB", text_color="black", command=lambda i=idx, s=stock: chg_q(i, 1, s)).pack(side="left")
                ctk.CTkLabel(bot, text=f"${sub:,.2f}", font=("Arial", 16, "bold"), text_color="#B12704").pack(side="right", padx=10)
                
                def rm(i): self.cart_items.pop(i); self.save_local_data(); self.update_top_badges(); refresh_cart()
                ctk.CTkButton(row, text=self.t("remove"), width=60, height=30, fg_color="transparent", text_color="#E74C3C", command=lambda i=idx: rm(i)).place(relx=0.98, rely=0.2, anchor="ne")
                
            lbl_total.configure(text=f"{self.t('total')} ${total:,.2f}")

        frm = ctk.CTkFrame(right_checkout, fg_color="transparent")
        frm.pack(fill="both", expand=True, padx=20)
        ctk.CTkLabel(frm, text=self.t("checkout_info"), font=self.get_font(16, "bold"), text_color="black").pack(anchor="w", pady=(0, 15))
        
        e_n = ctk.CTkEntry(frm, placeholder_text="ឈ្មោះ (Name)", font=self.get_font(14), height=45); e_n.pack(fill="x", pady=8)
        e_p = ctk.CTkEntry(frm, placeholder_text="លេខទូរស័ព្ទ (Phone)", font=("Arial", 14), height=45); e_p.pack(fill="x", pady=8)
        e_a = ctk.CTkEntry(frm, placeholder_text="អាស័យដ្ឋាន (Address)", font=self.get_font(14), height=45); e_a.pack(fill="x", pady=8)
        
        if self.current_user and hasattr(self, "user_profiles"):
            profile = self.user_profiles.get(self.current_user, {})
            if profile.get("name"): e_n.insert(0, profile["name"])
            if profile.get("phone"): e_p.insert(0, profile["phone"])
            if profile.get("address"): e_a.insert(0, profile["address"])
        
        def submit():
            if not self.cart_items or not e_n.get() or not e_p.get() or not e_a.get(): return
            total_amt = sum(float(i['product'].get('price') or 0) * i['qty'] for i in self.cart_items)
            msg = f"🔔 <b>New Order!</b>\n👤 {e_n.get()}\n📞 {e_p.get()}\n📍 {e_a.get()}\n\n💰 <b>Total: ${total_amt:,.2f}</b>"
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_ADMIN_CHAT_ID, "text": msg, "parse_mode": "HTML"})
            
            if self.current_user:
                import random
                import string
                
                # បង្កើតលេខកូដ Order ID (ឧទាហរណ៍: ORD-20260922-A1B2)
                rand_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
                order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{rand_str}"

                # បន្ថែម "order_id" និង "status" ចូលក្នុង order_record
                order_record = {
                    "order_id": order_id, 
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                    "total": total_amt, 
                    "status": "pending", 
                    "items": [{"name": i['product']['name'], "qty": i['qty'], "price": float(i['product'].get('price') or 0)} for i in self.cart_items]
                }
                
                if self.current_user not in self.order_history: self.order_history[self.current_user] = []
                self.order_history[self.current_user].insert(0, order_record)
                
                if not hasattr(self, "user_profiles"): self.user_profiles = {}
                self.user_profiles[self.current_user] = {"name": e_n.get(), "phone": e_p.get(), "address": e_a.get()}
            
            self.cart_items.clear()
            self.save_local_data() 
            self.update_top_badges() 
            
            # ២. ប្តូរពីការរត់ទៅ "home" ឲ្យរត់ទៅទំព័រ "account" (ប្រវត្តិទិញ) វិញ
            self.navigate_to("account")

        ctk.CTkButton(right_checkout, text=self.t("checkout"), font=self.get_font(16, "bold"), height=50, fg_color="#2ECC71", command=submit).pack(fill="x", padx=20, pady=20)
        refresh_cart()

if __name__ == "__main__":
    try:
        root = ctk.CTk()
        app = UserStoreApp(root)
        root.mainloop()
    except Exception as e:
        err_msg = traceback.format_exc()
        err_root = tk.Tk()
        err_root.withdraw()
        messagebox.showerror("Critical Crash", f"កម្មវិធីមានបញ្ហា:\n\n{err_msg}")