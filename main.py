import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import json

# Directories for images
BASE_DIR = r'C:\GI JOE Trader'
YEAR_FOLDERS = [str(year) for year in range(1982, 1995)]
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')

# Categorization files
WANT_FILE = 'want.json'
HAVE_FILE = 'have.json'
DONT_WANT_FILE = 'dont_want.json'

class GIJoeApp:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title(f'GI JOE Collectables Viewer - {self.username}')
        self.root.geometry('600x700')

        self.image_paths = self.load_all_images()
        self.current_index = 0
        self.want_mode = False  # Track if we're in want-list mode
        self.want_image_paths = []
        self.want_index = 0
        self.categories = {'want': set(), 'have': set(), 'dont_want': set()}
        self.load_categories()
        self.current_sort = None  # Track current sort mode

        # Toggle button for want-list mode
        self.toggle_frame = tk.Frame(self.root)
        self.toggle_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.want_toggle_btn = tk.Button(self.toggle_frame, text='Show Wants Only: OFF', command=self.toggle_want_mode, bg='#eee')
        self.want_toggle_btn.pack(side=tk.TOP, pady=2)

        # Sorting buttons frame
        self.sort_frame = tk.Frame(self.root)
        self.sort_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.sort_year_btn = tk.Button(self.sort_frame, text='Sort by Year', command=self.sort_by_year, bg='#e0e0e0')
        self.sort_year_btn.pack(side=tk.LEFT, padx=5)
        self.sort_name_btn = tk.Button(self.sort_frame, text='Sort by Name', command=self.sort_by_name, bg='#e0e0e0')
        self.sort_name_btn.pack(side=tk.LEFT, padx=5)
        self.sort_category_btn = tk.Button(self.sort_frame, text='Sort by Category', command=self.sort_by_category, bg='#e0e0e0')
        self.sort_category_btn.pack(side=tk.LEFT, padx=5)

        # Shop button
        self.shop_btn = tk.Button(self.toggle_frame, text='Open Shop', command=self.open_shop_window, bg='#ffc107')
        self.shop_btn.pack(side=tk.TOP, pady=2)

        self.image_label = tk.Label(self.root)
        self.image_label.pack(expand=True, fill=tk.BOTH)

        # Metadata label below image
        self.meta_label = tk.Label(self.root, text='', font=("Arial", 12), justify=tk.LEFT, wraplength=550)
        self.meta_label.pack(side=tk.TOP, pady=5)

        # Load figure metadata
        self.figure_meta = self.load_figure_metadata()

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        self.want_btn = tk.Button(btn_frame, text='Want It', command=self.mark_want, width=15, bg='#4CAF50', fg='white')
        self.have_btn = tk.Button(btn_frame, text='Have It', command=self.mark_have, width=15, bg='#2196F3', fg='white')
        self.dont_want_btn = tk.Button(btn_frame, text="Don't Want", command=self.mark_dont_want, width=15, bg='#F44336', fg='white')

        # Pack buttons in requested order: Don't Want, Have It, Want It
        self.dont_want_btn.pack(side=tk.LEFT, padx=5)
        self.have_btn.pack(side=tk.LEFT, padx=5)
        self.want_btn.pack(side=tk.LEFT, padx=5)

        nav_frame = tk.Frame(self.root)
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        self.prev_btn = tk.Button(nav_frame, text='Previous', command=self.prev_image, width=10)
        self.next_btn = tk.Button(nav_frame, text='Next', command=self.next_image, width=10)
        self.prev_btn.pack(side=tk.LEFT, padx=10)
        self.next_btn.pack(side=tk.RIGHT, padx=10)

        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        compare_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Compare', menu=compare_menu)
        compare_menu.add_command(label='Compare with Seller List', command=self.compare_with_seller)

        self.display_image()

    def open_shop_window(self):
        ShopWindow(self.root, self.username)

    def load_all_images(self):
        image_paths = []
        for year in YEAR_FOLDERS:
            folder = os.path.join(BASE_DIR, year)
            if os.path.isdir(folder):
                for fname in os.listdir(folder):
                    if fname.lower().endswith(IMAGE_EXTENSIONS):
                        image_paths.append(os.path.join(folder, fname))
        return image_paths

    def display_image(self):
        paths = self.get_active_image_list()
        if not paths:
            self.image_label.config(text='No images found!')
            self.meta_label.config(text='')
            self.root.title('GI JOE Collectables Viewer')
            return
        idx = self.get_active_index()
        img_path = paths[idx]
        img = Image.open(img_path)
        img.thumbnail((550, 550))
        self.tk_img = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.tk_img, text='')
        mode = 'WANT LIST' if self.want_mode else 'ALL'
        self.root.title(f'GI JOE Collectables Viewer - {self.username} [{mode}]')
        rel_path = os.path.relpath(img_path, BASE_DIR).replace('\\', '/')
        meta = self.figure_meta.get(rel_path)
        if meta:
            name = meta.get('name', 'Unknown')
            year = meta.get('year', 'Unknown')
            weapons = ', '.join(meta.get('weapons', [])) if meta.get('weapons') else 'Unknown'
            vehicle = meta.get('vehicle') or ''
            figure_id = meta.get('id', 'Unknown')
            meta_text = f"ID: {figure_id}\nName: {name}\nYear: {year}\nWeapons: {weapons}"
            if vehicle:
                meta_text += f"\nVehicle: {vehicle}"
        else:
            meta_text = "Name: Unknown\nYear: Unknown\nWeapons: Unknown"
        self.meta_label.config(text=meta_text)

    def next_image(self):
        paths = self.get_active_image_list()
        if not paths:
            return
        if self.want_mode:
            self.want_index = (self.want_index + 1) % len(paths)
        else:
            self.current_index = (self.current_index + 1) % len(paths)
        self.display_image()

    def prev_image(self):
        paths = self.get_active_image_list()
        if not paths:
            return
        if self.want_mode:
            self.want_index = (self.want_index - 1) % len(paths)
        else:
            self.current_index = (self.current_index - 1) % len(paths)
        self.display_image()

    def mark_want(self):
        self.categorize_current('want')

    def mark_have(self):
        self.categorize_current('have')

    def mark_dont_want(self):
        self.categorize_current('dont_want')

    def categorize_current(self, category):
        img_path = self.get_active_image_list()[self.get_active_index()]
        for cat in self.categories:
            self.categories[cat].discard(img_path)
        self.categories[category].add(img_path)
        self.save_categories()
        self.refresh_want_list()
        self.next_image()

    def save_categories(self):
        user_dir = os.path.join(os.path.dirname(__file__), 'users', self.username)
        os.makedirs(user_dir, exist_ok=True)
        for cat in self.categories:
            file_path = os.path.join(user_dir, f'{cat}.json')
            with open(file_path, 'w') as f:
                json.dump(list(self.categories[cat]), f, indent=2)

    def load_categories(self):
        user_dir = os.path.join(os.path.dirname(__file__), 'users', self.username)
        for cat in self.categories:
            file_path = os.path.join(user_dir, f'{cat}.json')
            try:
                with open(file_path, 'r') as f:
                    self.categories[cat] = set(json.load(f))
            except Exception:
                self.categories[cat] = set()
        self.refresh_want_list()

    def load_figure_metadata(self):
        import json
        import os
        meta_path = os.path.join(os.path.dirname(__file__), 'figures.json')
        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def compare_with_seller(self):
        seller_file = filedialog.askopenfilename(title='Select Seller List', filetypes=[('JSON or CSV', '*.json *.csv')])
        if not seller_file:
            return
        seller_wants = set()
        if seller_file.endswith('.json'):
            try:
                with open(seller_file, 'r') as f:
                    seller_wants = set(json.load(f))
            except Exception as e:
                messagebox.showerror('Error', f'Failed to load seller JSON: {e}')
                return
        elif seller_file.endswith('.csv'):
            try:
                with open(seller_file, 'r') as f:
                    for line in f:
                        seller_wants.add(line.strip())
            except Exception as e:
                messagebox.showerror('Error', f'Failed to load seller CSV: {e}')
                return
        matches = self.categories['want'] & seller_wants
        if not matches:
            messagebox.showinfo('No Matches', 'No images you want are available from this seller.')
        else:
            match_list = '\n'.join(os.path.basename(m) for m in matches)
            messagebox.showinfo('Matches', f'Images you want from this seller:\n\n{match_list}')

    def toggle_want_mode(self):
        self.want_mode = not self.want_mode
        if self.want_mode:
            self.want_toggle_btn.config(text='Show Wants Only: ON', bg='#FFD700')
            self.want_index = 0
        else:
            self.want_toggle_btn.config(text='Show Wants Only: OFF', bg='#eee')
            self.current_index = 0
        self.display_image()

    def refresh_want_list(self):
        self.want_image_paths = [p for p in self.image_paths if p in self.categories['want']]
        # If want_mode is active and the want list shrinks, reset want_index if needed
        if self.want_mode and self.want_index >= len(self.want_image_paths):
            self.want_index = 0

    def get_active_image_list(self):
        if self.want_mode:
            return self.want_image_paths
        return self.image_paths

    def sort_by_year(self):
        def get_year(path):
            rel_path = os.path.relpath(path, BASE_DIR).replace('\\', '/')
            meta = self.figure_meta.get(rel_path, {})
            return meta.get('year', 0)
        self.image_paths.sort(key=get_year)
        self.want_image_paths.sort(key=get_year)
        self.current_sort = 'year'
        self.current_index = 0
        self.want_index = 0
        self.display_image()

    def sort_by_name(self):
        def get_name(path):
            rel_path = os.path.relpath(path, BASE_DIR).replace('\\', '/')
            meta = self.figure_meta.get(rel_path, {})
            return meta.get('name', '')
        self.image_paths.sort(key=get_name)
        self.want_image_paths.sort(key=get_name)
        self.current_sort = 'name'
        self.current_index = 0
        self.want_index = 0
        self.display_image()

    def sort_by_category(self):
        def get_cat(path):
            if path in self.categories['want']:
                return 0
            elif path in self.categories['have']:
                return 1
            elif path in self.categories['dont_want']:
                return 2
            return 3
        self.image_paths.sort(key=get_cat)
        self.want_image_paths.sort(key=get_cat)
        self.current_sort = 'category'
        self.current_index = 0
        self.want_index = 0
        self.display_image()

    def get_active_index(self):
        return self.want_index if self.want_mode else self.current_index

def main():
    root = tk.Tk()
    # User selection popup
    username = UserSelectionDialog(root).result
    print(f"DEBUG: username dialog returned: {repr(username)}")
    if not username:
        root.destroy()
        return
    app = GIJoeApp(root, username)
    root.mainloop()

# --- User selection dialog ---
class UserSelectionDialog(tk.simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Enter your username:").pack()
        self.entry = tk.Entry(master)
        self.entry.pack()
        return self.entry
    def apply(self):
        self.result = self.entry.get().strip()

# --- Shop window scaffold ---
class ShopWindow(tk.Toplevel):
    def __init__(self, master, username):
        super().__init__(master)
        self.title(f"Shop - {username}")
        self.geometry('500x600')
        self.username = username
        self.want_only = tk.BooleanVar(value=False)

        top_frame = tk.Frame(self)
        top_frame.pack(fill=tk.X, pady=5)
        tk.Button(top_frame, text="Add Item", command=self.add_item_dialog).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(top_frame, text="Show Want List Only", variable=self.want_only, command=self.refresh_items).pack(side=tk.LEFT)
        self.items_listbox = tk.Listbox(self, width=60, height=25)
        self.items_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.refresh_items()

    def add_item_dialog(self):
        # Simple dialog for adding item (to be implemented)
        messagebox.showinfo("Add Item", "Add item dialog coming soon!")

    def refresh_items(self):
        # Load items and filter if needed (to be implemented)
        self.items_listbox.delete(0, tk.END)
        self.items_listbox.insert(tk.END, "[Shop items will appear here]")
    def sort_by_year(self):
        def get_year(path):
            rel_path = os.path.relpath(path, BASE_DIR).replace('\\', '/')
            meta = self.figure_meta.get(rel_path, {})
            return meta.get('year', 0)
        self.image_paths.sort(key=get_year)
        self.want_image_paths.sort(key=get_year)
        self.current_sort = 'year'
        self.current_index = 0
        self.want_index = 0
        self.display_image()

    def sort_by_name(self):
        def get_name(path):
            rel_path = os.path.relpath(path, BASE_DIR).replace('\\', '/')
            meta = self.figure_meta.get(rel_path, {})
            return meta.get('name', '')
        self.image_paths.sort(key=get_name)
        self.want_image_paths.sort(key=get_name)
        self.current_sort = 'name'
        self.current_index = 0
        self.want_index = 0
        self.display_image()

    def sort_by_category(self):
        def get_cat(path):
            if path in self.categories['want']:
                return 0
            elif path in self.categories['have']:
                return 1
            elif path in self.categories['dont_want']:
                return 2
            return 3
        self.image_paths.sort(key=get_cat)
        self.want_image_paths.sort(key=get_cat)
        self.current_sort = 'category'
        self.current_index = 0
        self.want_index = 0
        self.display_image()

if __name__ == '__main__':
    main()

