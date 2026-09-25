import customtkinter as ctk
from tkinter import filedialog
from tkinter import ttk
import tkinter as tk
from tkinter import font
import requests
import json
import os
from datetime import datetime
import threading
import tempfile
import webbrowser

# 🔑 បញ្ចូលព័ត៌មានរបស់អ្នកទីនេះ
SUPABASE_URL = "https://arrupyibnwvghwhgjfqg.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFycnVweWlibnd2Z2h3aGdqZnFnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk3OTY2NjUsImV4cCI6MjEwNTM3MjY2NX0.T8HQhUNNhB-lo948870hfqmoabbjo4yr-TTvoPPLb1E"
TELEGRAM_BOT_TOKEN = "8940465802:AAFdV3ZimYVkKC2iLq83LbxhaX_0Z0QtzxY"
TELEGRAM_CHAT_ID = "-1003435915451"

# 🔑 បន្ថែមព័ត៌មាន JSONBin ទីនេះ
JSONBIN_API_KEY = "$2a$10$zLpShJzAqZEDcD2JFAVA6uECAzPLVVZc/r009uIxoGJooGVxkFTsm"
JSONBIN_BIN_ID = "6ab0c526ffd5d160531e3259"
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
JSONBIN_HEADERS = {
    "X-Master-Key": JSONBIN_API_KEY,
    "Content-Type": "application/json"
}

HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json"
}

# កំណត់ហ្វុង (Fonts Configuration)
TITLE_FONT = ("Suwannaphum", 22, "bold")      # សម្រាប់ចំណងជើង
APP_FONT = ("Kantumruy Pro", 14)              # សម្រាប់អក្សរធម្មតា, Label, Button
INPUT_FONT = ("DaunPenh", 14)            # សម្រាប់ប្រអប់វាយអក្សរ (Entry/Textbox) ការពារលោតសញ្ញា ???

# ពណ៌ទំនើបសម្រាប់ប៊ូតុងទូទៅ (Neutral Colors)
NEUTRAL_BTN_COLOR = "#E5E7EB"
NEUTRAL_BTN_HOVER = "#D1D5DB"
NEUTRAL_TEXT_COLOR = "#1F2937"

class AdminDashboard:
    def __init__(self, root, admin_name="Unknown"):
        self.root = root
        self.admin_name = admin_name
        self.root.title(f"ប្រព័ន្ធគ្រប់គ្រងទំនិញ (Admin Dashboard) - កំពុងប្រើប្រាស់ដោយ៖ {self.admin_name}")
        
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        taskbar_height = 80  
        available_height = screen_height - taskbar_height
        window_width = 1150
        window_height = available_height - 60  
        
        x = (screen_width // 2) - (window_width // 2)
        y = (available_height // 2) - (window_height // 2)
        y = max(0, y) 
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        ctk.set_appearance_mode("Light")
        self.root.configure(fg_color="#F4F6F9")
        
        self.optional_specs = {}
        self.selected_thumbnail = None  
        self.selected_album = []        
        self.all_products_data = []
        self.current_filtered_data = [] 
        
        self.categories = ["Laptop", "PC", "Monitor", "Accessories", "Other"]
        self.colors = ["មិនកំណត់", "ខ្មៅ (Black)", "ស (White)", "ប្រផេះ (Gray)", "ទឹកប្រាក់ (Silver)", "ក្រហម (Red)", "ខៀវ (Blue)"]
        self.spaces = ["មិនកំណត់", "128GB", "256GB", "512GB", "1TB", "2TB"]
        self.years = ["ឆ្នាំទាំងអស់"]
        self.months = ["ខែទាំងអស់"]
        self.days = ["ថ្ងៃទាំងអស់"]
        self.origins = ["ប្រភពទាំងអស់"] 
        
        self.load_categories()

        header_frame = ctk.CTkFrame(self.root, fg_color="#FFFFFF", height=60, corner_radius=0)
        header_frame.pack(fill="x", pady=(0, 10))
        
        lbl_title = ctk.CTkLabel(
            header_frame, 
            text=f"⚙️ ប្រព័ន្ធគ្រប់គ្រងទំនិញក្នុងឃ្លាំង | Admin: {self.admin_name}    ", 
            font=TITLE_FONT, 
            text_color="#2C3E50"
        )
        lbl_title.pack(pady=15, expand=True, fill="x")

        self.tabview = ctk.CTkTabview(self.root, width=1100, height=750)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        self.tabview._segmented_button.configure(font=("Kantumruy Pro", 14, "bold"))

        self.tab_list = self.tabview.add("📦 បញ្ជីទំនិញ")
        self.tab_orders = self.tabview.add("🛍️ ការបញ្ជាទិញ") 
        self.tab_post = self.tabview.add("📢 Post Product")
        self.tab_update = self.tabview.add("🚀 Update User App")
        
        self.setup_list_tab()
        self.setup_orders_tab() 
        self.setup_post_tab()
        self.setup_update_tab()
        self.load_products()

    def custom_messagebox(self, title, message, msg_type="info"):
        popup = ctk.CTkToplevel(self.root)
        popup.title(title)
        
        ww, wh = 420, 220
        sw = popup.winfo_screenwidth()
        sh = popup.winfo_screenheight()
        x = (sw // 2) - (ww // 2)
        y = (sh // 2) - (wh // 2)
        popup.geometry(f"{ww}x{wh}+{x}+{y}")
        popup.attributes("-topmost", True)
        popup.grab_set()
        
        color = "#3498DB" 
        if msg_type == "warning": color = "#F39C12"
        elif msg_type == "error": color = "#E74C3C"
        
        lbl = ctk.CTkLabel(popup, text=message, font=("Kantumruy Pro", 14), wraplength=380, justify="center")
        lbl.pack(expand=True, padx=20, pady=20)
        
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))
        
        self.popup_result = False
        
        def on_ok():
            self.popup_result = True
            popup.destroy()
            
        def on_no():
            self.popup_result = False
            popup.destroy()

        if msg_type == "ask":
            ctk.CTkButton(btn_frame, text="យល់ព្រម (Yes)", font=("Kantumruy Pro", 14, "bold"), fg_color="#27AE60", width=110, height=35, command=on_ok).pack(side="left", padx=10)
            ctk.CTkButton(btn_frame, text="ទេ (No)", font=("Kantumruy Pro", 14, "bold"), fg_color="#E74C3C", width=110, height=35, command=on_no).pack(side="left", padx=10)
        else:
            ctk.CTkButton(btn_frame, text="បិទ (OK)", font=("Kantumruy Pro", 14, "bold"), fg_color=color, width=120, height=35, command=on_ok).pack(pady=10)
            
        self.root.wait_window(popup)
        return self.popup_result

    def add_custom_option(self, title, options_list, dropdown_widget):
        dialog = ctk.CTkInputDialog(text=f"បញ្ចូល {title} ថ្មី៖", title=f"បន្ថែម {title}")
        new_val = dialog.get_input()
        if new_val and new_val.strip():
            new_val = new_val.strip()
            if new_val not in options_list:
                options_list.append(new_val)
                dropdown_widget.configure(values=options_list)
            dropdown_widget.set(new_val)

    def edit_attribute(self, attr_list, dropdown_widget, title):
        target = dropdown_widget.get()
        if not target or target == "មិនកំណត់": return
        dialog = ctk.CTkInputDialog(text=f"កែប្រែ {title} '{target}' ទៅជា៖", title=f"កែប្រែ {title}")
        new_val = dialog.get_input()
        if new_val and new_val.strip() and new_val.strip() != target:
            new_val = new_val.strip()
            idx = attr_list.index(target)
            attr_list[idx] = new_val
            dropdown_widget.configure(values=attr_list)
            dropdown_widget.set(new_val)

    def delete_attribute(self, attr_list, dropdown_widget, title):
        target = dropdown_widget.get()
        if not target or target == "មិនកំណត់": return
        if self.custom_messagebox("បញ្ជាក់", f"តើអ្នកពិតជាចង់លុប {title} '{target}' មែនទេ?", "ask"):
            attr_list.remove(target)
            dropdown_widget.configure(values=attr_list)
            dropdown_widget.set("មិនកំណត់" if "មិនកំណត់" in attr_list else (attr_list[0] if attr_list else ""))

    def extract_dynamic_filters(self):
        dynamic_years = set()
        dynamic_origins = set() 
        for p in self.all_products_data:
            dt = p.get("saved_date", "")
            if dt and len(dt) >= 4:
                year = dt[:4]
                if year.isdigit(): dynamic_years.add(year)
            origin = p.get("origin", "")
            if origin and origin.strip(): dynamic_origins.add(origin.strip())
        
        self.years = ["ឆ្នាំទាំងអស់"] + sorted(list(dynamic_years), reverse=True)
        if hasattr(self, 'combo_filter_year'):
            self.combo_filter_year.configure(values=self.years)
            if self.filter_year_var.get() not in self.years: self.filter_year_var.set("ឆ្នាំទាំងអស់")

        self.origins = ["ប្រភពទាំងអស់"] + sorted(list(dynamic_origins))
        if hasattr(self, 'combo_filter_origin'):
            self.combo_filter_origin.configure(values=self.origins)
            if self.filter_origin_var.get() not in self.origins: self.filter_origin_var.set("ប្រភពទាំងអស់")

    def update_dependent_dropdowns(self):
        year_filter = getattr(self, 'filter_year_var', ctk.StringVar(value="ឆ្នាំទាំងអស់")).get()
        month_filter = getattr(self, 'filter_month_var', ctk.StringVar(value="ខែទាំងអស់")).get()
        
        available_months = set()
        available_days = set()
        for p in self.all_products_data:
            dt = str(p.get("saved_date", ""))
            if len(dt) >= 10:
                y = dt[:4]; m = dt[5:7]; d = dt[8:10]
                if year_filter == "ឆ្នាំទាំងអស់" or y == year_filter:
                    if m.isdigit(): available_months.add(m)
                    if month_filter == "ខែទាំងអស់" or m == month_filter:
                        if d.isdigit(): available_days.add(d)

        self.months = ["ខែទាំងអស់"] + sorted(list(available_months))
        if hasattr(self, 'combo_filter_month'):
            self.combo_filter_month.configure(values=self.months)
            if self.filter_month_var.get() not in self.months: self.filter_month_var.set("ខែទាំងអស់")

        self.days = ["ថ្ងៃទាំងអស់"] + sorted(list(available_days))
        if hasattr(self, 'combo_filter_day'):
            self.combo_filter_day.configure(values=self.days)
            if self.filter_day_var.get() not in self.days: self.filter_day_var.set("ថ្ងៃទាំងអស់")

    def setup_orders_tab(self):
        container_frame = self.tab_orders
        for widget in container_frame.winfo_children(): widget.destroy()
        
        ctk.CTkLabel(container_frame, text="📦 គ្រប់គ្រងការបញ្ជាទិញអតិថិជន", font=("Suwannaphum", 20, "bold")).pack(pady=10)
        search_frame = ctk.CTkFrame(container_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=5)
        
        center_search_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        center_search_container.pack(anchor="center")
        
        self.order_search_var = ctk.StringVar()
        # ប្រអប់វាយស្វែងរកប្រើ INPUT_FONT
        self.entry_order_search = ctk.CTkEntry(center_search_container, textvariable=self.order_search_var, placeholder_text="ស្កេន ឬវាយលេខកូដ, ឈ្មោះ, លេខទូរស័ព្ទ...", font=INPUT_FONT, width=350, height=40)
        self.entry_order_search.pack(side="left", padx=5)
        self.entry_order_search.focus() 
        
        ctk.CTkButton(center_search_container, text="🔍 ស្វែងរក", font=("Kantumruy Pro", 14, "bold"), width=100, height=40, fg_color="#2ECC71", command=lambda: self.render_orders_ui(self.order_search_var.get())).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="🔄 ផ្ទុកឡើងវិញ", font=("Kantumruy Pro", 14, "bold"), width=120, height=40, fg_color="#3498DB", command=self.fetch_and_render_orders).pack(side="right", padx=10)

        self.current_order_status = "pending"
        tab_nav_frame = ctk.CTkFrame(container_frame, fg_color="transparent")
        tab_nav_frame.pack(fill="x", padx=20, pady=15)
        
        tab_configs = {
            "pending": "⏳ រង់ចាំបញ្ជាក់",
            "confirmed": "📦 រៀបចំទំនិញ",
            "shipping": "🚚 កំពុងដឹក",
            "completed": "✅ ទទួលបាន"
        }
        self.order_tab_buttons = {}
        
        def switch_order_tab(status_key):
            self.current_order_status = status_key
            for k, btn in self.order_tab_buttons.items():
                if k == status_key:
                    btn.configure(fg_color="#3498DB", text_color="white", font=("Kantumruy Pro", 13, "bold"))
                else:
                    btn.configure(fg_color="#E5E7EB", text_color="black", font=("Kantumruy Pro", 13, "normal"))
            for k, sf in self.order_scroll_frames.items():
                if k == status_key: sf.pack(fill="both", expand=True)
                else: sf.pack_forget()
            self.render_orders_ui(self.order_search_var.get())

        self.order_content_frame = ctk.CTkFrame(container_frame, fg_color="transparent")
        self.order_content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.order_scroll_frames = {}
        for key in tab_configs.keys():
            sf = ctk.CTkScrollableFrame(self.order_content_frame, fg_color="transparent")
            self.order_scroll_frames[key] = sf

        for idx, (key, title) in enumerate(tab_configs.items()):
            btn = ctk.CTkButton(tab_nav_frame, text=title, font=("Kantumruy Pro", 13), width=150, height=35, corner_radius=20, command=lambda k=key: switch_order_tab(k))
            btn.pack(side="left", expand=True, padx=2)
            self.order_tab_buttons[key] = btn
            if idx < len(tab_configs) - 1:
                ctk.CTkLabel(tab_nav_frame, text="━━━━━━", font=("Arial", 10, "bold"), text_color="#95A5A6").pack(side="left", expand=True)

        self.lbl_order_loading = ctk.CTkLabel(container_frame, text="កំពុងទាញយកទិន្នន័យ...", font=("Kantumruy Pro", 14))
        self.entry_order_search.bind("<Return>", self.perform_order_search) 
        
        switch_order_tab("pending")
        self.fetch_and_render_orders()

    def fetch_and_render_orders(self):
        self.lbl_order_loading.pack(pady=20)
        self.lbl_order_loading.configure(text="កំពុងទាញយកទិន្នន័យ...")
        
        def do_fetch():
            try:
                res = requests.get(JSONBIN_URL, headers=JSONBIN_HEADERS)
                if res.status_code == 200:
                    self.full_cloud_data = res.json().get("record", {})
                    self.all_orders = self.full_cloud_data.get("order_history", {})
                    self.root.after(0, lambda: self.lbl_order_loading.pack_forget())
                    self.root.after(0, lambda: self.render_orders_ui())
                else:
                    self.root.after(0, lambda: self.lbl_order_loading.configure(text="បរាជ័យក្នុងការទាញយកទិន្នន័យ!"))
            except Exception as e: 
                self.root.after(0, lambda: self.lbl_order_loading.configure(text=f"Error: {e}"))

        threading.Thread(target=do_fetch, daemon=True).start()

    def perform_order_search(self, *args):
        self.render_orders_ui(self.order_search_var.get())

    def render_orders_ui(self, filter_text=""):
        current_sf = self.order_scroll_frames.get(self.current_order_status)
        if current_sf:
            for w in current_sf.winfo_children(): w.destroy()
            
        if not getattr(self, "all_orders", None): return
        filter_text = filter_text.lower().strip()

        status_options = {
            "pending": "⏳ រង់ចាំបញ្ជាក់ (pending)",
            "confirmed": "📦 រៀបចំទំនិញ (confirmed)",
            "shipping": "🚚 កំពុងដឹក (shipping)",
            "completed": "✅ ទទួលបាន (completed)"
        }
        status_badges = {
            "pending": "⏳ រង់ចាំបញ្ជាក់", "confirmed": "📦 រៀបចំទំនិញ",
            "shipping": "🚚 កំពុងដឹក", "completed": "✅ ទទួលបាន"
        }
        reverse_status = {v: k for k, v in status_options.items()}
        user_profiles = getattr(self, "full_cloud_data", {}).get("user_profiles", {})

        for user_email, orders in self.all_orders.items():
            profile = user_profiles.get(user_email, {})
            cust_name = profile.get("name", user_email)
            cust_phone = profile.get("phone", "គ្មានទូរស័ព្ទ")
            cust_address = profile.get("address", "គ្មានអាសយដ្ឋាន")

            for order_idx, order in enumerate(orders):
                order_id = order.get("order_id", "គ្មានលេខកូដ")
                current_status = order.get("status", "pending")
                
                if filter_text:
                    match_query = (filter_text in order_id.lower() or filter_text in user_email.lower() or 
                                   filter_text in cust_name.lower() or filter_text in cust_phone.lower())
                    if not match_query: continue
                    target_frame = current_sf
                else:
                    if current_status != self.current_order_status: continue
                    target_frame = current_sf

                card = ctk.CTkFrame(target_frame, fg_color="#FFFFFF", border_width=1, border_color="#D1D5DB", corner_radius=10)
                card.pack(fill="x", pady=12, padx=15)

                card_inner = ctk.CTkFrame(card, fg_color="transparent")
                card_inner.pack(fill="both", expand=True, padx=22, pady=18)
                
                top_row = ctk.CTkFrame(card_inner, fg_color="transparent")
                top_row.pack(fill="x", pady=(0, 12))
                
                order_info_str = f"🆔 {order_id}  |  👤 {cust_name}  |  📞 {cust_phone}  |  📍 {cust_address}  |  📅 {order.get('date')}"
                ctk.CTkLabel(top_row, text=order_info_str, font=("Kantumruy Pro", 13, "bold"), text_color="#2C3E50").pack(side="left")
                ctk.CTkLabel(top_row, text=f"Total: ${order.get('total'):,.2f}", font=("Kantumruy Pro", 13, "bold"), text_color="#B12704").pack(side="right")
                
                items_str = "\n".join([f"• {i['name']} (x{i['qty']})" for i in order.get('items', [])])
                ctk.CTkLabel(card_inner, text=items_str, font=("Kantumruy Pro", 14), justify="left").pack(anchor="w", pady=(0, 10))

                assigned_serials = order.get("assigned_serials", {})
                if assigned_serials:
                    sn_display = "🆔 Serial បានកំណត់៖ " + ", ".join([f"[{k}: {v}]" for k, v in assigned_serials.items()])
                    ctk.CTkLabel(card_inner, text=sn_display, font=("Kantumruy Pro", 12), text_color="#27AE60").pack(anchor="w", pady=(0, 10))

                action_row = ctk.CTkFrame(card_inner, fg_color="transparent")
                action_row.pack(fill="x", pady=(5, 0))
                
                is_locked = current_status in ["shipping", "completed"]

                btn_serial = ctk.CTkButton(action_row, text="🏷️ កំណត់ បន្ថែម", fg_color="#8E44AD", font=("Kantumruy Pro", 12), command=lambda e=user_email, i=order_idx, o=order: self.open_serial_assignment_popup(e, i, o))
                btn_serial.pack(side="left", padx=(0, 15))
                if is_locked: btn_serial.configure(state="disabled", fg_color="gray")

                ctk.CTkLabel(action_row, text="ប្តូរស្ថានភាព៖", font=("Kantumruy Pro", 14)).pack(side="left", padx=(0, 5))
                
                display_status_var = ctk.StringVar(value=status_options.get(current_status, status_options["pending"]))
                status_menu = ctk.CTkOptionMenu(action_row, variable=display_status_var, values=list(status_options.values()), fg_color="#3498DB", font=("Kantumruy Pro", 14), width=160)
                status_menu.pack(side="left")
                if is_locked: status_menu.configure(state="disabled")
                
                def save_status(email=user_email, idx=order_idx, ds_var=display_status_var, btn_widget=None):
                    new_status_key = reverse_status.get(ds_var.get(), "pending")
                    btn_widget.configure(text="កំពុងរក្សាទុក...", state="disabled")
                    def do_update():
                        try:
                            self.all_orders[email][idx]["status"] = new_status_key
                            self.full_cloud_data["order_history"] = self.all_orders
                            requests.put(JSONBIN_URL, headers=JSONBIN_HEADERS, json=self.full_cloud_data)
                            
                            if new_status_key in ["confirmed", "shipping", "completed"]:
                                assigned = self.all_orders[email][idx].get("assigned_serials", {})
                                for _, s_val in assigned.items():
                                    if s_val and s_val != "គ្មាន Serial ក្នុងស្តុក":
                                        requests.patch(f"{SUPABASE_URL}/rest/v1/products?serial_number=eq.{s_val}", headers=HEADERS, json={"status": "sold"})
                            self.root.after(0, lambda: btn_widget.configure(text="✔ រក្សាទុករួចរាល់", fg_color="#2ECC71"))
                            self.root.after(1000, lambda: [self.fetch_and_render_orders(), self.load_products()])
                        except Exception as e: 
                            self.root.after(0, lambda: self.custom_messagebox("Error", str(e), "error"))
                            self.root.after(0, lambda: btn_widget.configure(text="រក្សាទុក (Save)", state="normal"))
                    threading.Thread(target=do_update, daemon=True).start()

                btn_save = ctk.CTkButton(action_row, text="រក្សាទុក", fg_color="#F39C12", font=("Kantumruy Pro", 14), width=90)
                btn_save.configure(command=lambda e=user_email, i=order_idx, v=display_status_var, b=btn_save: save_status(e, i, v, b))
                btn_save.pack(side="left", padx=10)
                if is_locked: btn_save.configure(state="disabled", fg_color="gray")

                def delete_order(email=user_email, idx=order_idx):
                    if self.custom_messagebox("បញ្ជាក់", "តើអ្នកពិតជាចង់លុបការបញ្ជាទិញនេះមែនទេ?", "ask"):
                        def do_delete():
                            try:
                                self.all_orders[email].pop(idx)
                                if not self.all_orders[email]: del self.all_orders[email]
                                self.full_cloud_data["order_history"] = self.all_orders
                                requests.put(JSONBIN_URL, headers=JSONBIN_HEADERS, json=self.full_cloud_data)
                                self.root.after(0, lambda: self.render_orders_ui(self.order_search_var.get()))
                            except Exception as e:
                                self.root.after(0, lambda: self.custom_messagebox("Error", str(e), "error"))
                        threading.Thread(target=do_delete, daemon=True).start()

                btn_del = ctk.CTkButton(action_row, text="🗑️ លុប", fg_color="#E74C3C", hover_color="#C0392B", width=70, font=("Kantumruy Pro", 14), command=delete_order)
                btn_del.pack(side="right", padx=5)
                
                badge_text = status_badges.get(current_status, "⏳ រង់ចាំបញ្ជាក់")
                ctk.CTkLabel(action_row, text=f" 📌 {badge_text} ", font=("Kantumruy Pro", 12, "bold"), text_color="#2C3E50", fg_color="#E5E7EB", corner_radius=6).pack(side="right")

    def open_serial_assignment_popup(self, user_email, order_idx, order):
        popup = ctk.CTkToplevel(self.root)
        popup.title(f"🏷️ កំណត់ Serial Numbers សម្រាប់ Order: {order.get('order_id')}")
        popup.grab_set()
        popup.update_idletasks()
        sw = popup.winfo_screenwidth(); sh = popup.winfo_screenheight()
        ww, wh = 650, 550
        popup.geometry(f"{ww}x{wh}+{(sw//2)-(ww//2)}+{max(0, ((sh-80)//2)-(wh//2))}")

        scroll_f = ctk.CTkScrollableFrame(popup, fg_color="#FFFFFF", corner_radius=10)
        scroll_f.pack(fill="both", expand=True, padx=15, pady=15)
        ctk.CTkLabel(scroll_f, text=f"អតិថិជន៖ {user_email}", font=("Kantumruy Pro", 14, "bold"), text_color="#2C3E50").pack(anchor="w", pady=(0, 10))

        available_serials = [p.get("serial_number") for p in self.all_products_data if p.get("status", "available") == "available" and p.get("serial_number")]
        if not available_serials: available_serials = ["គ្មាន Serial ក្នុងស្តុក"]

        existing_assigned = order.get("assigned_serials", {})
        serial_dropdown_vars = {}

        for item_idx, item in enumerate(order.get("items", [])):
            item_name = item.get("name", "ទំនិញ")
            qty = int(item.get("qty", 1))
            ctk.CTkLabel(scroll_f, text=f"📦 {item_name} (ចំនួន៖ {qty})", font=("Kantumruy Pro", 13, "bold"), text_color="#E67E22").pack(anchor="w", pady=(10, 5))

            for q in range(qty):
                row_q = ctk.CTkFrame(scroll_f, fg_color="#F8F9FA", corner_radius=5)
                row_q.pack(fill="x", padx=10, pady=3)
                ctk.CTkLabel(row_q, text=f"គ្រឿងទី {q+1}:", font=("Kantumruy Pro", 12)).pack(side="left", padx=10)
                
                key_id = f"{item_idx}_{q}"
                var = ctk.StringVar(value=existing_assigned.get(key_id, available_serials[0]))
                serial_dropdown_vars[key_id] = var
                ctk.CTkOptionMenu(row_q, variable=var, values=available_serials, width=250, font=("Kantumruy Pro", 12)).pack(side="right", padx=10, pady=5)

        def save_serials_to_order():
            final_assigned = {k: v.get() for k, v in serial_dropdown_vars.items()}
            selected_vals = [v for v in final_assigned.values() if v != "គ្មាន Serial ក្នុងស្តុក"]
            if len(selected_vals) != len(set(selected_vals)): return self.custom_messagebox("ព្រមាន", "មានការជ្រើសរើស Serial Number ជាន់គ្នា!", "warning")

            try:
                self.all_orders[user_email][order_idx]["assigned_serials"] = final_assigned
                self.full_cloud_data["order_history"] = self.all_orders
                requests.put(JSONBIN_URL, headers=JSONBIN_HEADERS, json=self.full_cloud_data)
                self.custom_messagebox("ជោគជ័យ", "បានកំណត់ Serial Numbers រួចរាល់!", "info")
                popup.destroy()
                self.render_orders_ui(self.order_search_var.get())
            except Exception as e: self.custom_messagebox("Error", str(e), "error")

        ctk.CTkButton(scroll_f, text="💾 រក្សាទុក Serial Numbers", font=("Kantumruy Pro", 14, "bold"), fg_color="#27AE60", width=220, height=40, command=save_serials_to_order).pack(anchor="center", pady=20)

    def load_categories(self):
        try:
            res = requests.get(f"{SUPABASE_URL}/rest/v1/categories?select=name", headers=HEADERS)
            if res.status_code == 200:
                fetched = [item['name'] for item in res.json()]
                if fetched: self.categories = fetched
            if hasattr(self, 'combo_category'): self.combo_category.configure(values=self.categories)
            if hasattr(self, 'combo_filter_cat'): self.combo_filter_cat.configure(values=["ប្រភេទទាំងអស់"] + self.categories)
        except Exception as e: print("Error loading categories:", e)

    def add_new_category(self, dropdown_widget=None):
        widget = dropdown_widget if dropdown_widget else getattr(self, "combo_category", None)
        if widget: self.add_custom_option("ប្រភេទ", self.categories, widget)

    def edit_category(self, dropdown_widget=None):
        widget = dropdown_widget if dropdown_widget else getattr(self, "combo_category", None)
        target = widget.get() if widget else ""
        if not target: return
        dialog = ctk.CTkInputDialog(text=f"កែប្រែឈ្មោះប្រភេទ '{target}' ទៅជា៖", title="កែប្រែប្រភេទ")
        new_cat = dialog.get_input()
        if new_cat and new_cat.strip() and new_cat.strip() != target:
            try:
                res = requests.patch(f"{SUPABASE_URL}/rest/v1/categories?name=eq.{target}", headers=HEADERS, json={"name": new_cat.strip()})
                if res.status_code in [200, 204]:
                    requests.patch(f"{SUPABASE_URL}/rest/v1/products?category=eq.{target}", headers=HEADERS, json={"category": new_cat.strip()})
                    self.load_categories(); widget.set(new_cat.strip()); self.load_products()
                    self.custom_messagebox("ជោគជ័យ", "កែប្រែប្រភេទបានជោគជ័យ!", "info")
                else: self.custom_messagebox("បរាជ័យ", res.text, "error")
            except Exception as e: self.custom_messagebox("Error", str(e), "error")

    def delete_category(self, dropdown_widget=None):
        widget = dropdown_widget if dropdown_widget else getattr(self, "combo_category", None)
        target = widget.get() if widget else ""
        if not target: return

        products_in_cat = [p for p in self.all_products_data if p.get("category") == target]
        if not products_in_cat:
            if self.custom_messagebox("បញ្ជាក់", f"តើអ្នកពិតជាចង់លុបប្រភេទ '{target}' មែនទេ?", "ask"):
                try:
                    res = requests.delete(f"{SUPABASE_URL}/rest/v1/categories?name=eq.{target}", headers=HEADERS)
                    if res.status_code in [200, 204]:
                        self.load_categories(); widget.set(self.categories[0] if self.categories else "")
                        self.custom_messagebox("ជោគជ័យ", "លុបប្រភេទបានជោគជ័យ!", "info")
                    else: self.custom_messagebox("បរាជ័យ", res.text, "error")
                except Exception as e: self.custom_messagebox("Error", str(e), "error")
            return
        
        self.custom_messagebox("ព្រមាន", f"មិនអាចលុបបានទេ ព្រោះមានទំនិញកំពុងប្រើប្រាស់ប្រភេទ '{target}' នេះ!", "warning")

    def setup_list_tab(self):
        top_frame = ctk.CTkFrame(self.tab_list, fg_color="transparent")
        top_frame.pack(fill="x", pady=(10, 5))
        
        self.lbl_total_products = ctk.CTkLabel(top_frame, text="សរុបទំនិញ៖ 0 គ្រឿង", font=("Kantumruy Pro", 16, "bold"), text_color="#E67E22")
        self.lbl_total_products.pack(side="left", padx=10)
        self.lbl_total_value = ctk.CTkLabel(top_frame, text="តម្លៃសរុប៖ $0.00", font=("Kantumruy Pro", 16, "bold"), text_color="#27AE60")
        self.lbl_total_value.pack(side="left", padx=20)
        
        # ប្រអប់វាយស្វែងរកប្រើ INPUT_FONT
        self.entry_search = ctk.CTkEntry(top_frame, placeholder_text="ស្វែងរកតាម ឈ្មោះ ឬ Serial...", font=INPUT_FONT, width=280)
        self.entry_search.pack(side="left", padx=(10, 10))
        
        ctk.CTkButton(top_frame, text="🔍 ស្វែងរក", font=("Kantumruy Pro", 14, "bold"), width=90, command=self.filter_list_data).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="➕ បញ្ចូលទំនិញថ្មី", font=("Kantumruy Pro", 14, "bold"), fg_color="#27AE60", hover_color="#219653", width=140, command=self.open_add_product_popup).pack(side="left", padx=15)
        ctk.CTkButton(top_frame, text="🔄 ផ្ទុកឡើងវិញ", font=("Kantumruy Pro", 14, "bold"), width=120, fg_color="#3498DB", command=self.load_products).pack(side="right", padx=10)
        ctk.CTkButton(top_frame, text="🖨️ ព្រីនរបាយការណ៍", font=("Kantumruy Pro", 14, "bold"), width=140, fg_color="#9B59B6", command=self.print_direct_report).pack(side="right", padx=10)

        filter_frame = ctk.CTkFrame(self.tab_list, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#E5E7EB")
        filter_frame.pack(fill="x", pady=(0, 10), padx=10, ipady=5)

        self.list_status_var = ctk.StringVar(value="📦 ក្នុងស្តុក")
        self.seg_btn_status = ctk.CTkSegmentedButton(filter_frame, values=["📦 ក្នុងស្តុក", "🔴 លក់ចេញ", "📋 ទាំងអស់"], variable=self.list_status_var, command=self.filter_list_data, font=("Kantumruy Pro", 13, "bold"), selected_color="#3498DB")
        self.seg_btn_status.pack(side="left", padx=10, pady=5)

        self.filter_category_var = ctk.StringVar(value="ប្រភេទទាំងអស់")
        self.combo_filter_cat = ctk.CTkOptionMenu(filter_frame, variable=self.filter_category_var, values=["ប្រភេទទាំងអស់"] + self.categories, font=("Kantumruy Pro", 13), command=self.filter_list_data, width=120)
        self.combo_filter_cat.pack(side="left", padx=5, pady=5)

        self.filter_origin_var = ctk.StringVar(value="ប្រភពទាំងអស់")
        self.combo_filter_origin = ctk.CTkOptionMenu(filter_frame, variable=self.filter_origin_var, values=self.origins, font=("Kantumruy Pro", 13), command=self.filter_list_data, width=120)
        self.combo_filter_origin.pack(side="left", padx=5, pady=5)

        self.filter_year_var = ctk.StringVar(value="ឆ្នាំទាំងអស់")
        self.combo_filter_year = ctk.CTkOptionMenu(filter_frame, variable=self.filter_year_var, values=self.years, font=("Kantumruy Pro", 13), command=self.filter_list_data, width=100)
        self.combo_filter_year.pack(side="left", padx=5, pady=5)

        self.filter_month_var = ctk.StringVar(value="ខែទាំងអស់")
        self.combo_filter_month = ctk.CTkOptionMenu(filter_frame, variable=self.filter_month_var, values=self.months, font=("Kantumruy Pro", 13), command=self.filter_list_data, width=90)
        self.combo_filter_month.pack(side="left", padx=5, pady=5)

        self.filter_day_var = ctk.StringVar(value="ថ្ងៃទាំងអស់")
        self.combo_filter_day = ctk.CTkOptionMenu(filter_frame, variable=self.filter_day_var, values=self.days, font=("Kantumruy Pro", 13), command=self.filter_list_data, width=90)
        self.combo_filter_day.pack(side="left", padx=5, pady=5)

        bottom_frame = ctk.CTkFrame(self.tab_list, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", pady=15) 
        ctk.CTkButton(bottom_frame, text="✏️ កែប្រែ (Edit)", font=("Kantumruy Pro", 14, "bold"), fg_color="#F1C40F", hover_color="#F39C12", text_color="black", height=40, command=self.open_edit_window).pack(side="left", padx=10)
        ctk.CTkButton(bottom_frame, text="🗑️ លុប (Delete)", font=("Kantumruy Pro", 14, "bold"), fg_color="#E74C3C", hover_color="#C0392B", height=40, command=self.delete_product).pack(side="right", padx=10)

        table_frame = ctk.CTkFrame(self.tab_list)
        table_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        tree_scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", font=("Suwannaphum", 13, "bold"))
        style.configure("Treeview", font=("Kantumruy Pro", 12), rowheight=30)
        
        columns = ("serial", "name", "brand", "category", "cost", "price", "discount", "real_price", "status", "stock", "warranty", "origin", "date", "color", "space", "admin_name")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="tree headings", yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        self.tree.heading("#0", text="ល.រ") 
        self.tree.heading("serial", text="លេខកូដ (Serial)")
        self.tree.heading("name", text="ឈ្មោះទំនិញ")
        self.tree.heading("brand", text="ម៉ាក")
        self.tree.heading("category", text="ប្រភេទ")
        self.tree.heading("cost", text="តម្លៃដើម") 
        self.tree.heading("price", text="តម្លៃតាំងលក់")
        self.tree.heading("discount", text="បញ្ចុះ")
        self.tree.heading("real_price", text="លក់ជាក់ស្តែង")
        self.tree.heading("status", text="ស្ថានភាព")
        self.tree.heading("stock", text="ស្តុក")
        self.tree.heading("warranty", text="ការធានា")
        self.tree.heading("origin", text="ប្រភពនាំចូល")
        self.tree.heading("date", text="ថ្ងៃបញ្ចូល")
        self.tree.heading("color", text="ពណ៍")
        self.tree.heading("space", text="ទំហំ")
        self.tree.heading("admin_name", text="Admin (អ្នកកែ/បញ្ចូល)")

        self.tree.column("#0", width=60, minwidth=60, stretch=False, anchor="center")
        self.tree.column("serial", width=180, stretch=True, anchor="w") 
        self.tree.column("name", width=200, stretch=True, anchor="w")   
        for col in columns[2:]: self.tree.column(col, width=90, stretch=False, anchor="center")
        self.tree.pack(fill="both", expand=True)

        self.tree.tag_configure("sold_out", background="#FFF9C4")
        self.tree.tag_configure("out_of_stock", background="#FFCDD2")

        self.tooltip_win = None
        self.hovered_cell = None

    def filter_list_data(self, *args):
        self.update_dependent_dropdowns()
        query = self.entry_search.get().lower().strip()
        status_filter = self.list_status_var.get()
        cat_filter = getattr(self, "filter_category_var", ctk.StringVar(value="ប្រភេទទាំងអស់")).get()
        origin_filter = getattr(self, "filter_origin_var", ctk.StringVar(value="ប្រភពទាំងអស់")).get()
        year_filter = getattr(self, "filter_year_var", ctk.StringVar(value="ឆ្នាំទាំងអស់")).get()
        month_filter = getattr(self, "filter_month_var", ctk.StringVar(value="ខែទាំងអស់")).get()
        day_filter = getattr(self, "filter_day_var", ctk.StringVar(value="ថ្ងៃទាំងអស់")).get()

        filtered_data = []
        for p in self.all_products_data:
            specs = p.get("specs", {}) if isinstance(p.get("specs", {}), dict) else {}
            if query and query not in str(p.get("name", "")).lower() and query not in str(p.get("serial_number", "")).lower(): continue
            p_status = p.get("status", "available")
            if status_filter == "📦 ក្នុងស្តុក" and p_status != "available": continue
            if status_filter == "🔴 លក់ចេញ" and p_status != "sold": continue
            if cat_filter != "ប្រភេទទាំងអស់" and p.get("category") != cat_filter: continue
            if origin_filter != "ប្រភពទាំងអស់" and p.get("origin", "").strip() != origin_filter: continue
            
            dt = str(p.get("saved_date", ""))
            p_year = dt[0:4] if len(dt) >= 4 else ""; p_month = dt[5:7] if len(dt) >= 7 else ""; p_day = dt[8:10] if len(dt) >= 10 else ""
            if year_filter != "ឆ្នាំទាំងអស់" and p_year != year_filter: continue
            if month_filter != "ខែទាំងអស់" and p_month != month_filter: continue
            if day_filter != "ថ្ងៃទាំងអស់" and p_day != day_filter: continue
            filtered_data.append(p)
        
        self.current_filtered_data = filtered_data
        self.populate_table(filtered_data)

    def print_direct_report(self):
        data = getattr(self, "current_filtered_data", self.all_products_data)
        year_filter = getattr(self, "filter_year_var", ctk.StringVar(value="ឆ្នាំទាំងអស់")).get()
        month_filter = getattr(self, "filter_month_var", ctk.StringVar(value="ខែទាំងអស់")).get()
        day_filter = getattr(self, "filter_day_var", ctk.StringVar(value="ថ្ងៃទាំងអស់")).get()
        
        filter_title = f"របាយការណ៍ប្រតិបត្តិការ៖ {day_filter}/{month_filter}/{year_filter}"
        if year_filter == "ឆ្នាំទាំងអស់" and month_filter == "ខែទាំងអស់" and day_filter == "ថ្ងៃទាំងអស់":
            filter_title = "របាយការណ៍ប្រតិបត្តិការទំនិញសរុបទាំងអស់"

        html_content = f"""
        <!DOCTYPE html>
        <html lang="km">
        <head>
            <meta charset="UTF-8">
            <title>{filter_title}</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Kantumruy+Pro:wght@400;700&family=Suwannaphum:wght@400;700&display=swap');
                body {{ font-family: 'Kantumruy Pro', sans-serif; padding: 20px; color: #333; }}
                h2 {{ font-family: 'Suwannaphum', serif; text-align: center; color: #2C3E50; margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 14px; vertical-align: middle; }}
                th {{ font-family: 'Suwannaphum', serif; background-color: #F4F6F9; font-weight: bold; text-align: center; }}
                .center {{ text-align: center; }}
                .summary-container {{ display: flex; justify-content: flex-end; margin-top: 20px; }}
                .summary-box {{ border: 1px solid #ddd; padding: 15px 25px; border-radius: 8px; background-color: #F9FAFB; width: 350px; font-size: 16px; line-height: 1.8; }}
                .summary-box p {{ margin: 5px 0; display: flex; justify-content: space-between; }}
                .summary-divider {{ border: 0; border-top: 1px dashed #bdc3c7; margin: 10px 0; }}
                .print-btn {{ padding: 10px 20px; font-size: 16px; font-family: 'Kantumruy Pro', sans-serif; font-weight: bold; background-color: #27AE60; color: white; border: none; border-radius: 5px; cursor: pointer; display: block; margin: 0 auto 20px auto; }}
                @media print {{ .print-btn {{ display: none; }} body {{ padding: 0; }} }}
            </style>
        </head>
        <body>
            <button class="print-btn" onclick="window.print()">🖨️ ព្រីនរបាយការណ៍ (Print)</button>
            <h2>{filter_title}</h2>
            <table>
                <thead>
                    <tr>
                        <th>កាលបរិច្ឆេទ</th>
                        <th>ព័ត៌មានលម្អិតទំនិញ</th>
                        <th>Admin</th>
                        <th>ស្ថានភាព</th>
                        <th>ចំណាយដើម</th>
                        <th>ចំណូលលក់</th>
                        <th>ប្រាក់ចំណេញ</th>
                    </tr>
                </thead>
                <tbody>
        """
        total_revenue = 0.0; total_cost = 0.0; total_profit = 0.0; total_stock_value = 0.0
        
        for p in data:
            dt = str(p.get("saved_date", ""))
            formatted_date = dt[:10] if len(dt) >= 10 else "N/A"
            name = p.get("name", "Unknown"); serial = p.get("serial_number", ""); admin_maker = p.get("admin_name", "មិនស្គាល់")
            
            specs = p.get("specs", {}) if isinstance(p.get("specs", {}), dict) else {}
            color = specs.get("Color", ""); space = specs.get("Space", "")
            
            cost = float(p.get("cost_price") or 0); price = float(p.get("price") or 0); disc = float(p.get("discount_percent") or 0)
            real_sold_price = price - (price * disc / 100); stock = int(p.get("stock_quantity", 1))
            status = p.get("status", "available")
            
            if status == "sold":
                money_in_str = f"${real_sold_price:,.2f}"; money_out_str = f"${cost:,.2f}"
                profit = real_sold_price - cost; profit_str = f"${profit:,.2f}"
                status_label = "<span style='color: #E74C3C;'>លក់ចេញ (SOLD)</span>"
                total_revenue += real_sold_price; total_cost += cost; total_profit += profit
            else:
                money_in_str = "-"; money_out_str = f"${cost:,.2f}"; profit_str = "-"
                real_sold_price = 0.0
                status_label = "<span style='color: #27AE60;'>ក្នុងស្តុក (STOCK)</span>"
                total_stock_value += (cost * stock)
                
            details_html = f"<b>{name}</b><br><small>Serial: {serial}</small>"
            if color and color != "មិនកំណត់": details_html += f"<br><small>ពណ៌: {color}</small>"
            if space and space != "មិនកំណត់": details_html += f"<br><small>ទំហំ: {space}</small>"

            html_content += f"""
                <tr>
                    <td class="center">{formatted_date}</td>
                    <td>{details_html}</td>
                    <td class="center">{admin_maker}</td>
                    <td class="center"><b>{status_label}</b></td>
                    <td class="center" style="color: #E74C3C;">{money_out_str}</td>
                    <td class="center" style="color: #27AE60;">{money_in_str}</td>
                    <td class="center" style="color: #3498DB; font-weight:bold;">{profit_str}</td>
                </tr>
            """

        html_content += f"""
                </tbody>
            </table>
            <div class="summary-container">
                <div class="summary-box">
                    <p><span><b>សរុបចំណូល (Revenue):</b></span> <span style="color: #27AE60; font-weight: bold;">${total_revenue:,.2f}</span></p>
                    <p><span><b>សរុបចំណាយ (Cost):</b></span> <span style="color: #E74C3C; font-weight: bold;">${total_cost:,.2f}</span></p>
                    <p><span><b>ប្រាក់ចំណេញ (Profit):</b></span> <span style="color: #3498DB; font-weight: bold; font-size: 18px;">${total_profit:,.2f}</span></p>
                    <hr class="summary-divider">
                    <p><span><b>សរុបនៅសល់ស្តុក (Stock):</b></span> <span style="color: #8E44AD; font-weight: bold;">${total_stock_value:,.2f}</span></p>
                </div>
            </div>
            <script>window.onload = function() {{ window.print(); }}</script>
        </body>
        </html>
        """
        try:
            fd, path = tempfile.mkstemp(suffix=".html")
            with os.fdopen(fd, 'w', encoding='utf-8') as f: f.write(html_content)
            webbrowser.open(f"file://{os.path.abspath(path)}")
        except Exception as e: self.custom_messagebox("Error", f"មិនអាចបង្កើត Print Preview បានទេ: {e}", "error")

    def open_add_product_popup(self):
        popup = ctk.CTkToplevel(self.root)
        popup.title("➕ បញ្ចូលទំនិញថ្មីចូលឃ្លាំង")
        popup.grab_set(); popup.update_idletasks()
        sw = popup.winfo_screenwidth(); sh = popup.winfo_screenheight()
        ww, wh = 1100, 600 
        popup.geometry(f"{ww}x{wh}+{(sw//2)-(ww//2)}+{max(0, ((sh-80)//2)-(wh//2))}")

        scroll_frame = ctk.CTkScrollableFrame(popup, fg_color="#FFFFFF", corner_radius=10)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        scroll_frame.grid_columnconfigure(0, weight=6); scroll_frame.grid_columnconfigure(1, weight=4)
        left_f = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        left_f.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        right_f = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        right_f.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(left_f, text="ឈ្មោះទំនិញ៖", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        p_name = ctk.CTkEntry(left_f, placeholder_text="ឈ្មោះទំនិញ", font=INPUT_FONT, width=180, height=35)
        p_name.pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(left_f, text="ម៉ាក (Brand):", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        p_brand = ctk.CTkEntry(left_f, placeholder_text="ម៉ាក", font=INPUT_FONT, width=100, height=35)
        p_brand.pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(left_f, text="ព័ត៌មានកូដទំនិញ, ពណ៌ និង ទំហំ:", font=("Suwannaphum", 14, "bold")).pack(anchor="w", pady=(15, 5))
        serial_container = ctk.CTkFrame(left_f, fg_color="transparent")
        serial_container.pack(anchor="w", pady=(0, 5), fill="x")
        serial_entries = []

        def add_serial_box():
            row_frame = ctk.CTkFrame(serial_container, fg_color="#F8F9FA", corner_radius=8)
            row_frame.pack(anchor="w", pady=5, fill="x", padx=2)
            s_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            s_frame.pack(fill="x", padx=10, pady=(10, 5))
            
            ctk.CTkLabel(s_frame, text="លេខកូដ (Serial):", font=("Kantumruy Pro", 12)).pack(side="left")
            ent_s = ctk.CTkEntry(s_frame, placeholder_text="វាយបញ្ចូលលេខកូដ", font=INPUT_FONT, height=35)
            ent_s.pack(side="left", fill="x", expand=True, padx=(10, 10))
            
            bot_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            bot_frame.pack(fill="x", padx=10, pady=(0, 10))
            color_f = ctk.CTkFrame(bot_frame, fg_color="transparent")
            color_f.pack(side="left", fill="x", expand=True, padx=(0, 10))
            ctk.CTkLabel(color_f, text="ពណ៌ (Color):", font=("Kantumruy Pro", 12)).pack(anchor="w", pady=(0, 2))
            opt_c = ctk.CTkOptionMenu(color_f, values=self.colors, font=("Kantumruy Pro", 13), height=35)
            opt_c.set(self.colors[0] if self.colors else "មិនកំណត់")
            opt_c.pack(fill="x", expand=True)

            space_f = ctk.CTkFrame(bot_frame, fg_color="transparent")
            space_f.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(space_f, text="ទំហំ (Space):", font=("Kantumruy Pro", 12)).pack(anchor="w", pady=(0, 2))
            opt_sp = ctk.CTkOptionMenu(space_f, values=self.spaces, font=("Kantumruy Pro", 13), height=35)
            opt_sp.set(self.spaces[0] if self.spaces else "មិនកំណត់")
            opt_sp.pack(fill="x", expand=True)

            s_data = {"serial": ent_s, "color": opt_c, "space": opt_sp}
            serial_entries.append(s_data)
            
            if len(serial_entries) > 1:
                def remove_box(r=row_frame, d=s_data):
                    if d in serial_entries: serial_entries.remove(d)
                    r.destroy()
                ctk.CTkButton(s_frame, text="❌", font=("Kantumruy Pro", 14), width=35, height=35, fg_color="#FEE2E2", text_color="#DC2626", hover_color="#FECACA", command=remove_box).pack(side="right")

        add_serial_box()
        ctk.CTkButton(left_f, text="➕ បន្ថែមលេខកូដ (Serial)", font=("Kantumruy Pro", 14, "bold"), fg_color=NEUTRAL_BTN_COLOR, text_color=NEUTRAL_TEXT_COLOR, command=add_serial_box).pack(anchor="w", pady=(5, 15))

        ctk.CTkLabel(left_f, text="ការធានា (Warranty):", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        p_warranty = ctk.CTkEntry(left_f, placeholder_text="ឧ. ១ ឆ្នាំ, ៣ ខែ, គ្មានធានា...", font=INPUT_FONT, width=90, height=35)
        p_warranty.pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(left_f, text="ប្រភពនាំចូល:", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        p_origin = ctk.CTkEntry(left_f, placeholder_text="ប្រភពនាំចូល", font=INPUT_FONT, width=100, height=35)
        p_origin.pack(anchor="w", pady=(0, 15))

        row_p = ctk.CTkFrame(left_f, fg_color="transparent")
        row_p.pack(anchor="w", pady=(5, 0), fill="x")
        
        s0 = ctk.CTkFrame(row_p, fg_color="transparent")
        s0.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(s0, text="តម្លៃដើម($):", font=("Kantumruy Pro", 12), text_color="#E74C3C").pack(anchor="w")
        p_cost = ctk.CTkEntry(s0, placeholder_text="0", font=INPUT_FONT, width=80, height=30)
        p_cost.pack(anchor="w")

        s1 = ctk.CTkFrame(row_p, fg_color="transparent")
        s1.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(s1, text="តម្លៃតាំងលក់($):", font=("Kantumruy Pro", 12), text_color="#2980B9").pack(anchor="w")
        p_base_price = ctk.CTkEntry(s1, placeholder_text="0", font=INPUT_FONT, width=90, height=30)
        p_base_price.pack(anchor="w")

        s2 = ctk.CTkFrame(row_p, fg_color="transparent")
        s2.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(s2, text="តម្លៃលក់ចេញ($):", font=("Kantumruy Pro", 12), text_color="#27AE60").pack(anchor="w")
        p_sold_price = ctk.CTkEntry(s2, placeholder_text="0", font=INPUT_FONT, width=90, height=30)
        p_sold_price.pack(anchor="w")

        s3 = ctk.CTkFrame(row_p, fg_color="transparent")
        s3.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(s3, text="បញ្ចុះ(%):", font=("Kantumruy Pro", 12)).pack(anchor="w")
        p_disc = ctk.CTkEntry(s3, font=INPUT_FONT, width=70, height=30)
        p_disc.insert(0, "0"); p_disc.pack(anchor="w"); p_disc.configure(state="readonly")

        def add_auto_calculate_discount(event=None):
            try:
                base = float(p_base_price.get().strip() or 0); sold = float(p_sold_price.get().strip() or 0)
                discount = ((base - sold) / base) * 100 if base > 0 and sold <= base else 0.0
                p_disc.configure(state="normal"); p_disc.delete(0, 'end'); p_disc.insert(0, f"{discount:.2f}"); p_disc.configure(state="readonly")
            except ValueError: pass

        p_base_price.bind("<KeyRelease>", add_auto_calculate_discount)
        p_sold_price.bind("<KeyRelease>", add_auto_calculate_discount)

        s4 = ctk.CTkFrame(row_p, fg_color="transparent")
        s4.pack(side="left", padx=(5, 0))
        ctk.CTkLabel(s4, text="ស្តុក:", font=("Kantumruy Pro", 12)).pack(anchor="w")
        p_stock = ctk.CTkEntry(s4, placeholder_text="1", font=INPUT_FONT, width=60, height=30)
        p_stock.insert(0, "1"); p_stock.pack(anchor="w")

        ctk.CTkLabel(right_f, text="ប្រភេទ (Category):", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        p_cat = ctk.CTkOptionMenu(right_f, values=self.categories, font=("Kantumruy Pro", 14), width=180, height=35)
        if self.categories: p_cat.set(self.categories[0])
        p_cat.pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(right_f, text="ការពិពណ៌នាពេញលេញ (Description):", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        p_desc = ctk.CTkTextbox(right_f, font=INPUT_FONT, width=380, height=130)
        p_desc.pack(anchor="w", pady=(0, 5))
        p_desc.insert("1.0", "បញ្ចូលការពិពណ៌នាទំនិញ...")

        def save_popup_product():
            name = p_name.get().strip(); base_price_val = float(p_base_price.get().strip() or 0)
            if not name or not base_price_val: return self.custom_messagebox("ព្រមាន", "សូមបញ្ចូលឈ្មោះ និងតម្លៃទំនិញតាំងលក់!", "warning")

            brand_val = p_brand.get().strip(); cat_val = p_cat.get(); origin_val = p_origin.get().strip()
            warranty_val = p_warranty.get().strip(); cost_val = float(p_cost.get().strip() or 0)
            disc_val = float(p_disc.get().strip() or 0)
            valid_serials_data = [item for item in serial_entries if item["serial"].get().strip()]

            try:
                success_count = 0
                if valid_serials_data:
                    for item in valid_serials_data:
                        serial_val = item["serial"].get().strip(); color_val = item["color"].get().strip(); space_val = item["space"].get().strip()
                        specs_data = {}
                        if color_val and color_val != "មិនកំណត់": specs_data["Color"] = color_val
                        if space_val and space_val != "មិនកំណត់": specs_data["Space"] = space_val

                        product_data = {
                            "name": name, "short_desc": "", "brand": brand_val, "serial_number": serial_val, "warranty": warranty_val,
                            "origin": origin_val, "category": cat_val, "cost_price": cost_val, "price": base_price_val,
                            "discount_percent": disc_val, "is_promotion": disc_val > 0, "stock_quantity": 1, "status": "available",
                            "specs": specs_data, "description": p_desc.get("1.0", "end-1c").strip(), "saved_date": datetime.now().isoformat(), "admin_name": self.admin_name
                        }
                        res = requests.post(f"{SUPABASE_URL}/rest/v1/products", headers=HEADERS, json=product_data)
                        if res.status_code == 201: success_count += 1
                        else: self.custom_messagebox("កំហុស", f"មិនអាចរក្សាទុក Serial: {serial_val}\n{res.text}", "error")
                else:
                    stock_val = int(p_stock.get().strip() or 1)
                    product_data = {
                        "name": name, "short_desc": "", "brand": brand_val, "serial_number": "", "warranty": warranty_val,
                        "origin": origin_val, "category": cat_val, "cost_price": cost_val, "price": base_price_val,
                        "discount_percent": disc_val, "is_promotion": disc_val > 0, "stock_quantity": stock_val, "status": "available",
                        "specs": {}, "description": p_desc.get("1.0", "end-1c").strip(), "saved_date": datetime.now().isoformat(), "admin_name": self.admin_name
                    }
                    res = requests.post(f"{SUPABASE_URL}/rest/v1/products", headers=HEADERS, json=product_data)
                    if res.status_code == 201: success_count += 1

                if success_count > 0:
                    self.custom_messagebox("ជោគជ័យ", f"បានបញ្ចូលទំនិញថ្មីចំនួន {success_count} ជួរចូលបញ្ជីដោយជោគជ័យ!", "info")
                    popup.destroy(); self.load_products()
            except Exception as e: self.custom_messagebox("Error", str(e), "error")
            
        ctk.CTkButton(right_f, text="💾 រក្សាទុកទំនិញថ្មី", font=("Kantumruy Pro", 14, "bold"), fg_color="#2563EB", hover_color="#1D4ED8", text_color="white", width=220, height=40, command=save_popup_product).pack(anchor="w", pady=20)

    def load_products(self):
        try:
            res = requests.get(f"{SUPABASE_URL}/rest/v1/products?select=*", headers=HEADERS)
            if res.status_code == 200:
                self.all_products_data = res.json()
                self.extract_dynamic_filters() 
                self.filter_list_data() 
        except Exception as e: print("Error loading products:", e)

    def populate_table(self, data):
        for item in self.tree.get_children(): self.tree.delete(item)
        grouped_data = {}; total_list_value = 0.0 

        for p in data:
            name_key = p.get("name", "Unknown")
            if name_key not in grouped_data: grouped_data[name_key] = []
            grouped_data[name_key].append(p)
            price = float(p.get("price") or 0); disc = float(p.get("discount_percent") or 0)
            real_price = price - (price * disc / 100); stock = int(p.get("stock_quantity", 0))
            total_list_value += (real_price * stock)

        self.lbl_total_value.configure(text=f"តម្លៃសរុប៖ ${total_list_value:,.2f}")
        group_index = 1
        for name, items in grouped_data.items():
            first_item = items[0]
            total_stock = sum(int(i.get("stock_quantity", 0)) for i in items)
            cost = float(first_item.get("cost_price", 0)); price = float(first_item.get("price") or 0); disc = float(first_item.get("discount_percent") or 0)
            real_price = price - (price * disc / 100)
            dt = first_item.get("saved_date", "")[:10] if first_item.get("saved_date") else "N/A"

            if len(items) > 1:
                status_parent = "🟢 ក្នុងស្តុក" if any(i.get("status") == "available" for i in items) else "🔴 បានលក់"
                parent_id = self.tree.insert("", "end", text=str(group_index), values=(
                    "👉 ចុចទីនេះមើលលម្អិត", name, first_item.get("brand", ""), first_item.get("category", "N/A"), 
                    f"${cost:,.2f}", f"${price:,.2f}", f"-{disc}%" if disc > 0 else "-", f"${real_price:,.2f}", 
                    status_parent, total_stock, first_item.get("warranty", ""), first_item.get("origin", ""), dt, "", "", first_item.get("admin_name", "មិនស្គាល់")
                ), tags=("parent_node",)) 

                for p in items:
                    p_cost = float(p.get("cost_price", 0)); p_price = float(p.get("price") or 0); p_disc = float(p.get("discount_percent") or 0)
                    p_real = p_price - (p_price * p_disc / 100); p_status_val = p.get("status", "available"); p_stock = int(p.get("stock_quantity", 0))
                    row_tag = "" 
                    if p_status_val == "sold": p_status = "🔴 បានលក់"; row_tag = "sold_out" 
                    elif p_stock <= 0: p_status = "⭕ អស់ស្តុក"; row_tag = "out_of_stock" 
                    else: p_status = "🟢 ក្នុងស្តុក"
                    
                    specs = p.get("specs", {}) if isinstance(p.get("specs", {}), dict) else {}
                    c_val = specs.get("Color", ""); s_val = specs.get("Space", "")
                    
                    self.tree.insert(parent_id, "end", text=" └", values=(
                        str(p.get("serial_number", "គ្មាន")), p.get("name"), p.get("brand", ""), p.get("category", "N/A"), 
                        f"${p_cost:,.2f}", f"${p_price:,.2f}", f"-{p_disc}%" if p_disc > 0 else "-", f"${p_real:,.2f}", 
                        p_status, p.get("stock_quantity", 0), p.get("warranty", ""), p.get("origin", ""), 
                        p.get("saved_date", "")[:10] if p.get("saved_date") else "N/A", c_val, s_val, p.get("admin_name", "មិនស្គាល់")
                    ), tags=(str(p.get("id")), row_tag)) 
            else:
                p = items[0]
                p_status_val = p.get("status", "available"); p_stock = int(p.get("stock_quantity", 0))
                row_tag = ""
                if p_status_val == "sold": p_status = "🔴 បានលក់"; row_tag = "sold_out" 
                elif p_stock <= 0: p_status = "⭕ អស់ស្តុក"; row_tag = "out_of_stock" 
                else: p_status = "🟢 ក្នុងស្តុក"
                specs = p.get("specs", {}) if isinstance(p.get("specs", {}), dict) else {}
                
                self.tree.insert("", "end", text=str(group_index), values=(
                    str(p.get("serial_number", "គ្មាន")), p.get("name"), p.get("brand", ""), p.get("category", "N/A"), 
                    f"${cost:,.2f}", f"${price:,.2f}", f"-{disc}%" if disc > 0 else "-", f"${real_price:,.2f}", 
                    p_status, p.get("stock_quantity", 0), p.get("warranty", ""), p.get("origin", ""), dt, 
                    specs.get("Color", ""), specs.get("Space", ""), p.get("admin_name", "មិនស្គាល់")
                ), tags=(str(p.get("id")), row_tag)) 
            group_index += 1

        self.lbl_total_products.configure(text=f"សរុបទំនិញ៖ {sum(int(i.get('stock_quantity', 0)) for i in data)} គ្រឿង ({len(grouped_data)} ក្រុម)")
        self.auto_adjust_columns()

    def delete_product(self):
        selected = self.tree.selection()
        if not selected: return self.custom_messagebox("ព្រមាន", "សូមជ្រើសរើសទំនិញ!", "warning")
        prod_id = self.tree.item(selected[0], "tags")[0]
        if prod_id == "parent_node": return self.custom_messagebox("ព្រមាន", "មិនអាចលុបជួរសរុបបានទេ!", "warning")
        
        if self.custom_messagebox("បញ្ជាក់", f"តើអ្នកពិតជាចង់លុប {self.tree.item(selected[0], 'values')[1]} ឬទេ?", "ask"):
            try:
                res = requests.delete(f"{SUPABASE_URL}/rest/v1/products?id=eq.{prod_id}", headers=HEADERS)
                if res.status_code in [200, 204]: self.load_products()
            except Exception as e: self.custom_messagebox("Error", str(e), "error")

    def open_edit_window(self):
        selected = self.tree.selection()
        if not selected: return self.custom_messagebox("ព្រមាន", "សូមជ្រើសរើសទំនិញ!", "warning")
        prod_id = self.tree.item(selected[0], "tags")[0]
        if prod_id == "parent_node": return self.custom_messagebox("ព្រមាន", "មិនអាចកែប្រែជួរសរុបបានទេ!", "warning")

        p_info = next((p for p in self.all_products_data if str(p.get("id")) == str(prod_id)), None)
        if not p_info: return

        win = ctk.CTkToplevel(self.root)
        win.title("កែប្រែទិន្នន័យទំនិញ"); win.grab_set(); win.update_idletasks()
        sw = win.winfo_screenwidth(); sh = win.winfo_screenheight(); ww, wh = 950, 580 
        win.geometry(f"{ww}x{wh}+{(sw//2)-(ww//2)}+{max(0, ((sh-80)//2)-(wh//2))}")

        scroll_frame = ctk.CTkScrollableFrame(win, fg_color="#FFFFFF", corner_radius=10)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        scroll_frame.grid_columnconfigure(0, weight=1); scroll_frame.grid_columnconfigure(1, weight=1)
        left_f = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        left_f.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        right_f = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        right_f.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(left_f, text="ឈ្មោះទំនិញ៖", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        e_name = ctk.CTkEntry(left_f, width=180, height=35, font=INPUT_FONT)
        e_name.insert(0, p_info.get("name", "")); e_name.pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(left_f, text="ម៉ាក (Brand):", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        e_brand = ctk.CTkEntry(left_f, width=110, height=35, font=INPUT_FONT)
        e_brand.insert(0, p_info.get("brand", "") or ""); e_brand.pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(left_f, text="លេខកូដ (Serial):", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        e_serial = ctk.CTkEntry(left_f, width=380, height=35, font=INPUT_FONT)
        e_serial.insert(0, p_info.get("serial_number", "") or ""); e_serial.pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(left_f, text="ការធានា (Warranty):", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        e_warranty = ctk.CTkEntry(left_f, width=100, height=35, font=INPUT_FONT)
        e_warranty.insert(0, p_info.get("warranty", "") or ""); e_warranty.pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(left_f, text="ប្រភពនាំចូល:", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        e_origin = ctk.CTkEntry(left_f, width=100, height=35, font=INPUT_FONT)
        e_origin.insert(0, p_info.get("origin", "") or ""); e_origin.pack(anchor="w", pady=(0, 15))

        row_p = ctk.CTkFrame(left_f, fg_color="transparent")
        row_p.pack(anchor="w", pady=(5, 0), fill="x")
        s0 = ctk.CTkFrame(row_p, fg_color="transparent"); s0.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(s0, text="តម្លៃដើម($):", font=("Kantumruy Pro", 12), text_color="#E74C3C").pack(anchor="w")
        e_cost = ctk.CTkEntry(s0, width=80, height=30, font=INPUT_FONT)
        e_cost.insert(0, str(p_info.get("cost_price", "0"))); e_cost.pack(anchor="w")

        s1 = ctk.CTkFrame(row_p, fg_color="transparent"); s1.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(s1, text="តម្លៃតាំងលក់($):", font=("Kantumruy Pro", 12), text_color="#2980B9").pack(anchor="w")
        e_base_price = ctk.CTkEntry(s1, width=90, height=30, font=INPUT_FONT)
        e_base_price.insert(0, str(p_info.get("price", "0"))); e_base_price.pack(anchor="w")

        old_base = float(p_info.get("price") or 0); old_disc = float(p_info.get("discount_percent") or 0)
        old_sold_price = old_base - (old_base * old_disc / 100)
        s2 = ctk.CTkFrame(row_p, fg_color="transparent"); s2.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(s2, text="តម្លៃលក់ចេញ($):", font=("Kantumruy Pro", 12), text_color="#27AE60").pack(anchor="w")
        e_sold_price = ctk.CTkEntry(s2, width=90, height=30, font=INPUT_FONT)
        e_sold_price.insert(0, f"{old_sold_price:.2f}"); e_sold_price.pack(anchor="w")

        s3 = ctk.CTkFrame(row_p, fg_color="transparent"); s3.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(s3, text="បញ្ចុះ(%):", font=("Kantumruy Pro", 12)).pack(anchor="w")
        e_disc = ctk.CTkEntry(s3, width=70, height=30, font=INPUT_FONT)
        e_disc.insert(0, str(p_info.get("discount_percent", "0"))); e_disc.pack(anchor="w"); e_disc.configure(state="readonly")

        def auto_calculate_discount(event=None):
            try:
                base = float(e_base_price.get().strip() or 0); sold = float(e_sold_price.get().strip() or 0)
                discount = ((base - sold) / base) * 100 if base > 0 and sold <= base else 0.0
                e_disc.configure(state="normal"); e_disc.delete(0, 'end'); e_disc.insert(0, f"{discount:.2f}"); e_disc.configure(state="readonly")
            except ValueError: pass

        e_base_price.bind("<KeyRelease>", auto_calculate_discount)
        e_sold_price.bind("<KeyRelease>", auto_calculate_discount)

        s4 = ctk.CTkFrame(row_p, fg_color="transparent"); s4.pack(side="left", padx=(5, 0))
        ctk.CTkLabel(s4, text="ស្តុក:", font=("Kantumruy Pro", 12)).pack(anchor="w")
        e_stock = ctk.CTkEntry(s4, width=60, height=30, font=INPUT_FONT)
        e_stock.insert(0, str(p_info.get("stock_quantity", "0"))); e_stock.pack(anchor="w")

        ctk.CTkLabel(right_f, text="ប្រភេទ (Category):", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        e_cat = ctk.CTkOptionMenu(right_f, values=self.categories, width=180, height=35, font=("Kantumruy Pro", 14))
        e_cat.set(p_info.get("category", self.categories[0] if self.categories else "")); e_cat.pack(anchor="w", pady=(0, 15))

        existing_specs = p_info.get("specs", {}) if isinstance(p_info.get("specs", {}), dict) else {}
        ctk.CTkLabel(right_f, text="ពណ៌ (Color):", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        e_color = ctk.CTkOptionMenu(right_f, values=self.colors, width=100, height=35, font=("Kantumruy Pro", 14))
        e_color.set(existing_specs.get("Color", "មិនកំណត់")); e_color.pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(right_f, text="ទំហំផ្ទុក (Space):", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        e_space = ctk.CTkOptionMenu(right_f, values=self.spaces, width=130, height=35, font=("Kantumruy Pro", 14))
        e_space.set(existing_specs.get("Space", "មិនកំណត់")); e_space.pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(right_f, text="ស្ថានភាព (Status):", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        e_status = ctk.CTkOptionMenu(right_f, values=["available", "sold"], width=80, height=35, font=("Kantumruy Pro", 14))
        e_status.set(p_info.get("status", "available")); e_status.pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(right_f, text="ការពិពណ៌នាពេញលេញ (Description):", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        e_full_desc = ctk.CTkTextbox(right_f, width=380, height=130, font=INPUT_FONT)
        e_full_desc.insert("1.0", p_info.get("description", "") or ""); e_full_desc.pack(anchor="w", pady=(0, 5))

        def save_edits():
            try:
                name = e_name.get().strip(); brand = e_brand.get().strip(); serial = e_serial.get().strip(); warranty = e_warranty.get().strip()
                category = e_cat.get(); stock = e_stock.get().strip(); origin = e_origin.get().strip(); status = e_status.get()
                full_desc = e_full_desc.get("1.0", "end-1c").strip()
                cost_price = float(e_cost.get().strip() or 0); price = float(e_base_price.get().strip() or 0); disc_val = float(e_disc.get().strip() or 0)
                
                updated_specs = p_info.get("specs", {}) if isinstance(p_info.get("specs", {}), dict) else {}
                color_val = e_color.get().strip()
                if color_val and color_val != "មិនកំណត់": updated_specs["Color"] = color_val
                else: updated_specs.pop("Color", None) 
                    
                space_val = e_space.get().strip()
                if space_val and space_val != "មិនកំណត់": updated_specs["Space"] = space_val
                else: updated_specs.pop("Space", None) 

                data = {
                    "name": name, "short_desc": "", "brand": brand, "serial_number": serial, "warranty": warranty,
                    "origin": origin, "category": category, "cost_price": cost_price, "price": price, 
                    "discount_percent": disc_val, "is_promotion": disc_val > 0, "stock_quantity": int(stock) if stock else 0,
                    "status": status, "specs": updated_specs, "description": full_desc, "admin_name": self.admin_name
                }
                res = requests.patch(f"{SUPABASE_URL}/rest/v1/products?id=eq.{prod_id}", headers=HEADERS, data=json.dumps(data))
                if res.status_code in [200, 204]: win.destroy(); self.load_products(); self.custom_messagebox("ជោគជ័យ", "បានកែប្រែទិន្នន័យជោគជ័យ!", "info")
                else: self.custom_messagebox("បរាជ័យ", f"មិនអាចរក្សាទុកបានទេ៖ {res.text}", "error")
            except Exception as e: self.custom_messagebox("Error", str(e), "error")
        
        ctk.CTkButton(right_f, text="💾 រក្សាទុកការកែប្រែ", font=("Kantumruy Pro", 14, "bold"), fg_color="#2563EB", hover_color="#1D4ED8", text_color="white", width=240, height=45, command=save_edits).pack(anchor="w", pady=20)

    def setup_post_tab(self):
        main_frame = ctk.CTkScrollableFrame(self.tab_post, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#E0E0E0")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        main_frame.grid_columnconfigure(0, weight=1); main_frame.grid_columnconfigure(1, weight=1)

        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(left_frame, text="ឈ្មោះទំនិញ៖", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        self.entry_name = ctk.CTkEntry(left_frame, placeholder_text="ឈ្មោះទំនិញ", font=INPUT_FONT, width=380, height=35)
        self.entry_name.pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(left_frame, text="ព័ត៌មានសង្ខេប (អតិបរមា ៣ បន្ទាត់)៖", font=("Kantumruy Pro", 12)).pack(anchor="w", pady=(5, 0))
        self.desc_line1 = ctk.CTkEntry(left_frame, placeholder_text="បន្ទាត់ទី ១", font=INPUT_FONT, width=380, height=30)
        self.desc_line1.pack(anchor="w", pady=(2, 2))
        self.desc_line2 = ctk.CTkEntry(left_frame, placeholder_text="បន្ទាត់ទី ២", font=INPUT_FONT, width=380, height=30)
        self.desc_line2.pack(anchor="w", pady=(2, 2))
        self.desc_line3 = ctk.CTkEntry(left_frame, placeholder_text="បន្ទាត់ទី ៣", font=INPUT_FONT, width=380, height=30)
        self.desc_line3.pack(anchor="w", pady=(2, 10))

        ctk.CTkLabel(left_frame, text="ម៉ាក (Brand):", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        self.entry_brand = ctk.CTkEntry(left_frame, placeholder_text="Brand", font=INPUT_FONT, width=380, height=35)
        self.entry_brand.pack(anchor="w", pady=(0, 15))

        row_price = ctk.CTkFrame(left_frame, fg_color="transparent")
        row_price.pack(anchor="w", pady=(5, 0), fill="x")
        p_sub1 = ctk.CTkFrame(row_price, fg_color="transparent"); p_sub1.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(p_sub1, text="តម្លៃ ($):", font=("Kantumruy Pro", 12)).pack(anchor="w")
        self.entry_price = ctk.CTkEntry(p_sub1, placeholder_text="0", font=INPUT_FONT, width=110, height=30)
        self.entry_price.pack(anchor="w")

        p_sub2 = ctk.CTkFrame(row_price, fg_color="transparent"); p_sub2.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(p_sub2, text="បញ្ចុះ(%):", font=("Kantumruy Pro", 12)).pack(anchor="w")
        self.entry_discount = ctk.CTkEntry(p_sub2, placeholder_text="0", font=INPUT_FONT, width=110, height=30)
        self.entry_discount.pack(anchor="w")

        p_sub3 = ctk.CTkFrame(row_price, fg_color="transparent"); p_sub3.pack(side="left")
        ctk.CTkLabel(p_sub3, text="ស្តុក:", font=("Kantumruy Pro", 12)).pack(anchor="w")
        self.entry_stock = ctk.CTkEntry(p_sub3, placeholder_text="1", font=INPUT_FONT, width=110, height=30)
        self.entry_stock.insert(0, "1"); self.entry_stock.pack(anchor="w")

        ctk.CTkLabel(right_frame, text="ប្រភេទ (Category):", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        self.combo_category = ctk.CTkOptionMenu(right_frame, values=self.categories, font=("Kantumruy Pro", 14), width=210, height=35)
        self.combo_category.pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(right_frame, text="ការពិពណ៌នាពេញលេញ (Description):", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        self.txt_desc = ctk.CTkTextbox(right_frame, font=INPUT_FONT, width=380, height=70)
        self.txt_desc.pack(anchor="w", pady=(0, 5))
        self.txt_desc.insert("1.0", "បញ្ចូលការពិពណ៌នាទំនិញនៅទីនេះ...")

        ctk.CTkLabel(right_frame, text="YouTube Video URL:", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        self.entry_video_url = ctk.CTkEntry(right_frame, placeholder_text="🔗 YouTube URL", font=INPUT_FONT, width=380, height=35)
        self.entry_video_url.pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(right_frame, text="រូបភាពទំនិញ៖", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        thumb_row = ctk.CTkFrame(right_frame, fg_color="transparent"); thumb_row.pack(anchor="w", pady=2)
        ctk.CTkButton(thumb_row, text="🖼️ រូបភាពគោល", font=("Kantumruy Pro", 13), width=130, height=30, command=self.select_thumbnail).pack(side="left", padx=(0, 10))
        self.lbl_thumb = ctk.CTkLabel(thumb_row, text="មិនទាន់មាន", text_color="#7F8C8D", font=("Kantumruy Pro", 12))
        self.lbl_thumb.pack(side="left")

        album_row = ctk.CTkFrame(right_frame, fg_color="transparent"); album_row.pack(anchor="w", pady=(2, 5))
        ctk.CTkButton(album_row, text="🖼️ រូបភាពបន្ថែម", font=("Kantumruy Pro", 13), width=130, height=30, command=self.select_album).pack(side="left", padx=(0, 10))
        self.lbl_album = ctk.CTkLabel(album_row, text="មិនទាន់មាន", text_color="#7F8C8D", font=("Kantumruy Pro", 12))
        self.lbl_album.pack(side="left")

        ctk.CTkLabel(right_frame, text="លក្ខណៈបច្ចេកទេសបន្ថែម (Specs):", font=("Kantumruy Pro", 14)).pack(anchor="w", pady=(5, 0))
        row_opt = ctk.CTkFrame(right_frame, fg_color="transparent"); row_opt.pack(anchor="w", pady=2)
        self.entry_opt_key = ctk.CTkEntry(row_opt, placeholder_text="ឈ្មោះ (ឧ. RAM)", font=INPUT_FONT, width=110, height=30)
        self.entry_opt_key.pack(side="left", padx=(0, 5))
        self.entry_opt_val = ctk.CTkEntry(row_opt, placeholder_text="តម្លៃ (ឧ. 16GB)", font=INPUT_FONT, width=110, height=30)
        self.entry_opt_val.pack(side="left", padx=(0, 5))
        ctk.CTkButton(row_opt, text="➕ បន្ថែម", font=("Kantumruy Pro", 13), width=80, height=30, command=self.add_option).pack(side="left")

        self.specs_list_frame = ctk.CTkScrollableFrame(right_frame, fg_color="#F8F9FA", corner_radius=5, width=370, height=75)
        self.specs_list_frame.pack(anchor="w", pady=5)
        ctk.CTkButton(right_frame, text="📢 ផុសផលិតផលទៅ User App", font=("Kantumruy Pro", 14, "bold"), fg_color="#2563EB", hover_color="#1D4ED8", text_color="white", width=240, height=40, command=self.save_product).pack(anchor="w", pady=10)
    
    def select_thumbnail(self):
        file_path = filedialog.askopenfilename(title="ជ្រើសរើសរូបភាពគោល", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path: self.selected_thumbnail = file_path; self.lbl_thumb.configure(text="បានជ្រើសរើស ១ សន្លឹក", text_color="#27AE60")

    def select_album(self):
        file_paths = filedialog.askopenfilenames(title="ជ្រើសរើសរូបភាពបន្ថែម", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_paths: self.selected_album = file_paths; self.lbl_album.configure(text=f"បានជ្រើសរើស {len(file_paths)} សន្លឹក", text_color="#27AE60")

    def upload_thumbnail(self, caption):
        if not self.selected_thumbnail: return None
        try:
            with open(self.selected_thumbnail, "rb") as f:
                res = requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto", data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption, "parse_mode": "HTML"}, files={"photo": f})
            if res.status_code == 200: return res.json()["result"]["photo"][-1]["file_id"]
        except Exception as e: print("Thumb Error:", e)
        return None

    def upload_album(self):
        if not self.selected_album: return None
        media_group, files, uploaded_ids = [], {}, []
        try:
            for i, path in enumerate(self.selected_album):
                if i >= 10: break
                key = f"photo{i}"
                media_group.append({"type": "photo", "media": f"attach://{key}"}); files[key] = open(path, "rb")
            res = requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMediaGroup", data={"chat_id": TELEGRAM_CHAT_ID, "media": json.dumps(media_group)}, files=files)
            for f in files.values(): f.close()
            if res.status_code == 200:
                for msg in res.json()["result"]: uploaded_ids.append(msg["photo"][-1]["file_id"])
                return ",".join(uploaded_ids)
        except Exception as e: print("Album Error:", e)
        return None

    def add_option(self):
        k, v = self.entry_opt_key.get().strip(), self.entry_opt_val.get().strip()
        if k and v:
            self.optional_specs[k] = v; self.entry_opt_key.delete(0, 'end'); self.entry_opt_val.delete(0, 'end'); self.update_specs_display()

    def remove_option(self, key):
        if key in self.optional_specs: del self.optional_specs[key]; self.update_specs_display()

    def edit_option(self, key):
        if key in self.optional_specs:
            val = self.optional_specs[key]
            self.entry_opt_key.delete(0, 'end'); self.entry_opt_key.insert(0, key)
            self.entry_opt_val.delete(0, 'end'); self.entry_opt_val.insert(0, val)
            self.remove_option(key)

    def update_specs_display(self):
        for w in self.specs_list_frame.winfo_children(): w.destroy()
        for k, v in self.optional_specs.items():
            row = ctk.CTkFrame(self.specs_list_frame, fg_color="#F8F9FA", corner_radius=5)
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=f"▪ {k} : {v}", font=("Kantumruy Pro", 14), text_color="black").pack(side="left", padx=15, pady=5)
            ctk.CTkButton(row, text="❌ លុប", font=("Kantumruy Pro", 13), width=60, height=28, fg_color="#FEE2E2", text_color="#DC2626", hover_color="#FECACA", command=lambda key=k: self.remove_option(key)).pack(side="right", padx=10, pady=5)
            ctk.CTkButton(row, text="កែប្រែ", font=("Kantumruy Pro", 13), width=60, height=28, command=lambda key=k: self.edit_option(key)).pack(side="right", padx=5, pady=5)

    def save_product(self):
        lines = [line.strip() if line.strip().startswith("-") else "- " + line.strip() for line in [self.desc_line1.get(), self.desc_line2.get(), self.desc_line3.get()] if line.strip()]
        short_desc = "\n".join(lines)
        name = self.entry_name.get().strip(); brand = self.entry_brand.get().strip(); category = self.combo_category.get()
        price = self.entry_price.get().strip(); discount = self.entry_discount.get().strip(); stock = self.entry_stock.get().strip()
        desc = self.txt_desc.get("1.0", "end-1c").strip(); video_url = self.entry_video_url.get().strip()

        if not name or not price: return self.custom_messagebox("ព្រមាន", "សូមបញ្ចូលឈ្មោះ និងតម្លៃ!", "warning")

        disc_val = float(discount) if discount else 0.0
        caption = f"📦 <b>ទំនិញ:</b> {name}\n"
        if brand: caption += f"🏢 <b>ម៉ាក:</b> {brand}\n"
        caption += f"🏷 <b>ប្រភេទ:</b> {category}\n💲 <b>តម្លៃ:</b> ${price}\n📊 <b>ស្តុក:</b> {stock}\n\n"
        if desc and desc != "បញ្ចូលការពិពណ៌នាទំនិញនៅទីនេះ...": caption += f"📝 <b>ការពិពណ៌នា:</b>\n{desc}\n\n"
        
        self.lbl_thumb.configure(text="កំពុងដំណើរការ...", text_color="#F39C12"); self.root.update()
        thumb_id = self.upload_thumbnail(caption) if self.selected_thumbnail else None
        album_ids = self.upload_album() if self.selected_album else None

        try:
            product_data = {
                "name": name, "short_desc": short_desc, "brand": brand, "discount_percent": disc_val, "is_promotion": disc_val > 0,
                "category": category, "price": float(price), "stock_quantity": int(stock) if stock else 1, "status": "available",
                "description": desc, "specs": self.optional_specs, "image_id": thumb_id, "image_ids": album_ids,
                "video_url": video_url, "saved_date": datetime.now().isoformat(), "admin_name": self.admin_name
            }
            res = requests.post(f"{SUPABASE_URL}/rest/v1/products", headers=HEADERS, json=product_data)
            if res.status_code == 201:
                self.custom_messagebox("ជោគជ័យ", "ផុសផលិតផលទៅ User App បានជោគជ័យ!", "info")
                self.reset_form(); self.load_products()
            else: self.custom_messagebox("កំហុស", res.text, "error")
        except Exception as e: self.custom_messagebox("កំហុស", str(e), "error")

    def reset_form(self):
        for e in [self.entry_name, self.entry_brand, self.entry_price, self.entry_stock, self.entry_video_url, self.entry_discount, self.desc_line1, self.desc_line2, self.desc_line3]: e.delete(0, 'end')
        self.txt_desc.delete("1.0", "end"); self.txt_desc.insert("1.0", "បញ្ចូលការពិពណ៌នាទំនិញនៅទីនេះ...")
        self.combo_category.set(self.categories[0] if self.categories else "")
        self.optional_specs.clear(); self.update_specs_display()
        self.selected_thumbnail = None; self.selected_album = []
        self.lbl_thumb.configure(text="មិនទាន់មាន", text_color="#7F8C8D"); self.lbl_album.configure(text="មិនទាន់មាន", text_color="#7F8C8D")

    def setup_update_tab(self):
        up_frame = ctk.CTkFrame(self.tab_update, fg_color="#FFFFFF", corner_radius=10)
        up_frame.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(up_frame, text="🚀 បញ្ចូល Link សម្រាប់អាប់ដេតកម្មវិធី User App ជំនាន់ថ្មី", font=("Suwannaphum", 18, "bold")).pack(pady=(20, 10))
        self.entry_app_version = ctk.CTkEntry(up_frame, placeholder_text="ជំនាន់ App ថ្មី (ឧ. 1.2)", font=INPUT_FONT, width=300, height=45)
        self.entry_app_version.pack(pady=10)
        self.entry_download_url = ctk.CTkEntry(up_frame, placeholder_text="Paste Direct Download Link ទីនេះ...", font=INPUT_FONT, width=600, height=45)
        self.entry_download_url.pack(pady=10)
        ctk.CTkButton(up_frame, text="✅ រក្សាទុកការ Update", font=("Kantumruy Pro", 16, "bold"), fg_color="#2563EB", text_color="white", width=250, height=45, command=self.save_update_link).pack(pady=30)

    def save_update_link(self):
        version = self.entry_app_version.get().strip(); download_link = self.entry_download_url.get().strip()
        if not version or not download_link: return self.custom_messagebox("បញ្ហា", "សូមបញ្ចូលជំនាន់ (Version) និង Link សម្រាប់ទាញយក!", "warning")
        try:
            res_update = requests.patch(f"{SUPABASE_URL}/rest/v1/app_settings?id=eq.1", headers=HEADERS, json={"version": version, "download_url": download_link})
            if res_update.status_code in [200, 204]:
                self.custom_messagebox("ជោគជ័យ", "បានដាក់បញ្ចូលការ Update ថ្មីដោយជោគជ័យ!", "info")
                self.entry_app_version.delete(0, 'end'); self.entry_download_url.delete(0, 'end')
            else: self.custom_messagebox("បរាជ័យ", f"មិនអាច Update Setting បានទេ: {res_update.text}", "error")
        except Exception as e: self.custom_messagebox("Error", str(e), "error")

    def auto_adjust_columns(self):
        measure_font = font.Font(family="Kantumruy Pro", size=12)
        for col in self.tree["columns"]:
            max_width = measure_font.measure(self.tree.heading(col)["text"]) + 30
            def check_children(parent):
                nonlocal max_width
                for item in self.tree.get_children(parent):
                    val = str(self.tree.set(item, col))
                    item_width = measure_font.measure(val) + 30 
                    if item_width > max_width: max_width = item_width
                    check_children(item)
            check_children("")
            max_width = min(max_width, 400)
            self.tree.column(col, width=max_width, minwidth=max_width)
            
        max_width_0 = measure_font.measure(self.tree.heading("#0")["text"]) + 30
        def check_children_0(parent):
            nonlocal max_width_0
            for item in self.tree.get_children(parent):
                val = str(self.tree.item(item, "text")); indent = 20 if parent else 0 
                item_width = measure_font.measure(val) + 40 + indent
                if item_width > max_width_0: max_width_0 = item_width
                check_children_0(item)
        check_children_0("")
        max_width_0 = min(max_width_0, 300)
        self.tree.column("#0", width=max_width_0, minwidth=max_width_0)

class AdminLogin:
    def __init__(self, root):
        self.root = root
        self.root.title("ចូលប្រព័ន្ធ (Admin Login)")
        window_width = 450; window_height = 350
        sw = self.root.winfo_screenwidth(); sh = self.root.winfo_screenheight()
        self.root.geometry(f"{window_width}x{window_height}+{(sw//2)-(window_width//2)}+{(sh//2)-(window_height//2)}")
        ctk.set_appearance_mode("Light")
        self.root.configure(fg_color="#F4F6F9")

        ctk.CTkLabel(root, text="🔐 ប្រព័ន្ធគ្រប់គ្រង (Admin Login)", font=TITLE_FONT).pack(pady=(40, 20))
        # ប្រអប់វាយឈ្មោះ និង លេខកូដ ត្រូវបានប្រើ INPUT_FONT ដើម្បីអោយវាយខ្មែរបាន
        self.username = ctk.CTkEntry(root, placeholder_text="ឈ្មោះ Admin (Username)", font=INPUT_FONT, width=280, height=40)
        self.username.pack(pady=10)
        
        self.password = ctk.CTkEntry(root, placeholder_text="លេខសម្ងាត់ (Password)", show="*", font=INPUT_FONT, width=280, height=40)
        self.password.pack(pady=10)
        
        self.lbl_error = ctk.CTkLabel(root, text="", text_color="red", font=("Kantumruy Pro", 12))
        self.lbl_error.pack()
        ctk.CTkButton(root, text="ចូលប្រព័ន្ធ (Login)", font=("Kantumruy Pro", 16, "bold"), width=280, height=40, command=self.login).pack(pady=10)

    def login(self):
        user = self.username.get().strip(); pwd = self.password.get().strip()
        valid_admins = {"admin1": "1234", "admin2": "1234", "sokha": "1234"}
        
        if user in valid_admins and valid_admins[user] == pwd:
            self.root.withdraw() 
            dashboard_window = ctk.CTkToplevel(self.root)
            app = AdminDashboard(dashboard_window, admin_name=user) 
            dashboard_window.protocol("WM_DELETE_WINDOW", self.root.destroy)
        else:
            self.lbl_error.configure(text="ឈ្មោះ ឬលេខសម្ងាត់មិនត្រឹមត្រូវទេ!")

def load_custom_fonts():
    """ មុខងារសម្រាប់ Auto-load Fonts ពី Folder ឈ្មោះ 'font' របស់អ្នក """
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "font")
    
    fonts_to_load = [
        "Suwannaphum-Regular.ttf",
        "Suwannaphum-Bold.ttf",
        "KantumruyPro-Regular.ttf",
        "KantumruyPro-Bold.ttf"
    ]
    
    if os.path.exists(font_dir):
        for font_file in fonts_to_load:
            font_path = os.path.join(font_dir, font_file)
            if os.path.exists(font_path):
                try:
                    ctk.FontManager.load_font(font_path)
                except Exception as e:
                    print(f"មិនអាច Load Font {font_file} បានទេ: {e}")

if __name__ == "__main__":
    load_custom_fonts()
    login_root = ctk.CTk()
    login_app = AdminLogin(login_root)
    login_root.mainloop()