import tkinter as tk
from tkinter import ttk, messagebox
import json
from PIL import Image, ImageTk
import os

SALE_ITEMS_FILE = 'sale_items.json'
IMAGE_DIR = 'images'  # Match Sale Item Builder's image folder

class SaleItemsViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Sale Items Viewer')
        self.geometry('600x400')
        self.items = self.load_items()
        self.filtered_items = self.items.copy()
        self.create_widgets()

    def load_items(self):
        try:
            with open(SALE_ITEMS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load items: {e}')
            return []

    def create_widgets(self):
        # Search bar
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(search_frame, text='Search Name:').pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.update_filter)

        ttk.Label(search_frame, text='Min Price:').pack(side='left', padx=(10,0))
        self.min_price_var = tk.StringVar()
        min_price_entry = ttk.Entry(search_frame, textvariable=self.min_price_var, width=7)
        min_price_entry.pack(side='left')
        min_price_entry.bind('<KeyRelease>', self.update_filter)

        ttk.Label(search_frame, text='Max Price:').pack(side='left', padx=(10,0))
        self.max_price_var = tk.StringVar()
        max_price_entry = ttk.Entry(search_frame, textvariable=self.max_price_var, width=7)
        max_price_entry.pack(side='left')
        max_price_entry.bind('<KeyRelease>', self.update_filter)

        # Listbox for items
        self.items_listbox = tk.Listbox(self)
        self.items_listbox.pack(fill='both', expand=True, padx=10, pady=5)
        self.items_listbox.bind('<<ListboxSelect>>', self.show_item_details)

        # Details area
        self.details_frame = ttk.Frame(self)
        self.details_frame.pack(fill='x', padx=10, pady=5)
        self.details_label = ttk.Label(self.details_frame, text='', anchor='w', justify='left')
        self.details_label.pack(side='left')
        self.image_label = ttk.Label(self.details_frame)
        self.image_label.pack(side='right')

        self.update_listbox()

    def update_filter(self, event=None):
        name = self.search_var.get().lower()
        min_price = self.min_price_var.get()
        max_price = self.max_price_var.get()
        try:
            min_price = float(min_price) if min_price else None
        except ValueError:
            min_price = None
        try:
            max_price = float(max_price) if max_price else None
        except ValueError:
            max_price = None
        self.filtered_items = []
        for item in self.items:
            if name and name not in item['name'].lower():
                continue
            try:
                price = float(item['price'])
            except Exception:
                price = 0
            if min_price is not None and price < min_price:
                continue
            if max_price is not None and price > max_price:
                continue
            self.filtered_items.append(item)
        self.update_listbox()

    def update_listbox(self):
        self.items_listbox.delete(0, tk.END)
        for item in self.filtered_items:
            self.items_listbox.insert(tk.END, f"{item['name']} (${item['price']})")
        self.details_label.config(text='')
        self.image_label.config(image='')
        self.image_label.image = None

    def show_item_details(self, event):
        selection = self.items_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        item = self.filtered_items[idx]
        details = f"ID: {item['id']}\nName: {item['name']}\nDescription: {item.get('description', 'N/A')}\nPrice: ${item['price']}"
        self.details_label.config(text=details)
        # Show image if available
        img_path = os.path.join(IMAGE_DIR, item.get('image', ''))
        if os.path.isfile(img_path):
            try:
                img = Image.open(img_path)
                img.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(img)
                self.image_label.config(image=photo)
                self.image_label.image = photo
            except Exception:
                self.image_label.config(image='')
                self.image_label.image = None
        else:
            self.image_label.config(image='')
            self.image_label.image = None

if __name__ == '__main__':
    app = SaleItemsViewer()
    app.mainloop()
