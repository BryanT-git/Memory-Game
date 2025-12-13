import tkinter as tk
from PIL import Image, ImageTk
import random, os

# --- CẤU HÌNH ---
ASSET_DIR = "assets"
BG_NORMAL = os.path.join(ASSET_DIR, "Background", "normalbg.png")
BG_WIN    = os.path.join(ASSET_DIR, "Background", "winbg.png")
CARD_BACK = os.path.join(ASSET_DIR, "Item", "card_back.png")

ICON_PATHS = [
    os.path.join(ASSET_DIR, "Item", "baconburger.png"),
    os.path.join(ASSET_DIR, "Item", "bag_of_chips.png"),
    os.path.join(ASSET_DIR, "Item", "fries.png"),
    os.path.join(ASSET_DIR, "Item", "grilled_cod.png"),
    os.path.join(ASSET_DIR, "Item", "hamburger.png"),
    os.path.join(ASSET_DIR, "Item", "hotdog.png"),
    os.path.join(ASSET_DIR, "Item", "pizza.png"),
    os.path.join(ASSET_DIR, "Item", "popcorn.png"),
    os.path.join(ASSET_DIR, "Item", "porksandwich.png"),
    os.path.join(ASSET_DIR, "Item", "ratatouille.png"),
    os.path.join(ASSET_DIR, "Item", "rice.png"),
    os.path.join(ASSET_DIR, "Item", "spaghetti.png"),
    os.path.join(ASSET_DIR, "Item", "steaksandwich.png"),
    os.path.join(ASSET_DIR, "Item", "sushi.png"),
]

# ---------- LOAD LOCAL IMAGE ----------
def load_local_image(path, size=None):
    try:
        img = Image.open(path).convert("RGBA")
        if size:
            img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print("Error loading:", path, e)
        fallback = Image.new("RGBA", size if size else (64,64), (180,180,180,255))
        return ImageTk.PhotoImage(fallback)

# ---------- MAIN GAME CLASS ----------
class MemoryGame:
    def __init__(self, root, level):
        self.root = root
        self.first = None
        self.second = None
        self.moves = 0
        self.buttons = []
        self.paused = False

        # cấu hình level: rows, cols, card_size, max_moves, time_limit
        if level == 1:  
            self.rows, self.cols, card_size, self.max_moves, self.time_left = 2, 2, 64, 4, 30
        elif level == 2:  
            self.rows, self.cols, card_size, self.max_moves, self.time_left = 4, 4, 58, 16, 60
        elif level == 3:  
            self.rows, self.cols, card_size, self.max_moves, self.time_left = 6, 6, 52, 46, 120

        total = self.rows * self.cols
        needed_icons = total // 2

        self.icons = [load_local_image(path, (card_size, card_size)) for path in ICON_PATHS[:needed_icons]]
        self.values = list(range(needed_icons)) * 2
        random.shuffle(self.values)

        for w in self.root.winfo_children():
            w.destroy()

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        # đặt background trong lúc chơi
        bg = load_local_image(BG_NORMAL, (screen_w, screen_h))
        bg_label = tk.Label(self.root, image=bg)
        bg_label.image = bg
        bg_label.place(x=0, y=0)

        # labels
        self.move_label = tk.Label(self.root, text=f"Số Lần Lật: 0 / {self.max_moves}", 
                                   font=("Arial", 14, "bold"), bg="#ffffff")
        self.move_label.pack(pady=5)

        self.time_label = tk.Label(self.root, text=f"Thời Gian: {self.time_left}s",
                                   font=("Arial", 14, "bold"), bg="#ffffff")
        self.time_label.pack(pady=5)

        # control buttons
        control_frame = tk.Frame(self.root, bg="#ffffff")
        control_frame.pack(pady=5)
        tk.Button(control_frame, text="Tạm Dừng", command=self.toggle_pause).pack(side="left", padx=5)
        tk.Button(control_frame, text="Thoát", command=self.quit_game, bg="lightcoral").pack(side="left", padx=5)

        # frame chứa các lá bài
        frame = tk.Frame(self.root, bg="#ffffff")
        frame.pack(expand=True)

        self.card_back = load_local_image(CARD_BACK, (card_size, card_size))

        index = 0
        for r in range(self.rows):
            row_buttons = []
            for c in range(self.cols):
                btn = tk.Button(frame,
                                image=self.card_back,
                                width=card_size, height=card_size,
                                command=lambda i=index: self.flip(i),
                                relief="ridge", borderwidth=1,
                                bg="lightblue")
                btn.grid(row=r, column=c, padx=1, pady=1)
                row_buttons.append(btn)
                index += 1
            self.buttons.append(row_buttons)

        # bắt đầu đếm thời gian
        self.update_timer()

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.move_label.config(text=f"Số Lần Lật: {self.moves} / {self.max_moves} (Tạm Dừng)")
        else:
            self.update_moves()

    def update_moves(self):
        self.move_label.config(text=f"Số Lần Lật: {self.moves} / {self.max_moves}")
        if self.moves > self.max_moves:
            self.lose_screen()

    def update_timer(self):
        if self.paused:
            self.root.after(1000, self.update_timer)
            return
        if self.time_left > 0:
            self.time_left -= 1
            mins, secs = divmod(self.time_left, 60)
            self.time_label.config(text=f"Thời Gian: {mins:02d}:{secs:02d}")
            self.root.after(1000, self.update_timer)
        else:
            self.lose_screen()

    def flip(self, index):
        if self.paused:
            return
        r = index // self.cols
        c = index % self.cols
        btn = self.buttons[r][c]
        if btn["state"] == "disabled":
            return
        btn.config(image=self.icons[self.values[index]], bg="yellow")
        btn.update()
        if not self.first:
            self.first = (index, btn)
        else:
            self.second = (index, btn)
            self.moves += 1
            self.update_moves()
            self.root.after(500, self.check_match)

    def check_match(self):
        if not self.first or not self.second:
            return
        i1, b1 = self.first
        i2, b2 = self.second
        if self.values[i1] == self.values[i2]:
            b1.config(state="disabled", bg="lightgreen")
            b2.config(state="disabled", bg="lightgreen")
        else:
            b1.config(image=self.card_back, bg="lightblue")
            b2.config(image=self.card_back, bg="lightblue")
        self.first = None
        self.second = None
        self.check_win()

    def check_win(self):
        for row in self.buttons:
            for btn in row:
                if btn["state"] != "disabled":
                    return
        self.win_screen()

    def win_screen(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.root.title("YOU WIN")
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        bg = load_local_image(BG_WIN, (screen_w, screen_h))
        bg_label = tk.Label(self.root, image=bg)
        bg_label.image = bg
        bg_label.place(x=0, y=0)
        tk.Label(self.root, text="🎉Chiến Thắng🎉", font=("Arial", 32, "bold"), bg="#ffffff").pack(pady=20)
        tk.Label(self.root, text=f"Số Lần Lật: {self.moves}", font=("Arial", 24), bg="#ffffff").pack(pady=10)
        tk.Button(self.root, text="Chơi Lại", font=("Arial", 20), command=lambda: start_menu(self.root)).pack(pady=10)
        tk.Button(self.root, text="Thoát", font=("Arial", 20), bg="lightcoral", command=self.root.destroy).pack(pady=10)

    def lose_screen(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.root.title("YOU LOSE")
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        bg = load_local_image(BG_NORMAL, (screen_w, screen_h))
        bg_label = tk.Label(self.root, image=bg)
        bg_label.image = bg
        bg_label.place(x=0, y=0)
        tk.Label(self.root, text="💀Thất Bại💀", font=("Arial", 32, "bold"), bg="#ffffff").pack(pady=20)
        tk.Label(self.root, text=f"Số Lần Lật: {self.moves} / {self.max_moves}", font=("Arial", 24), bg="#ffffff").pack(pady=10)
        tk.Label(self.root, text=f"Hết Thời Gian", font=("Arial", 24), bg="#ffffff").pack(pady=10)
        tk.Button(self.root, text="Thử Lại", font=("Arial", 20), command=lambda: start_menu(self.root)).pack(pady=10)
        tk.Button(self.root, text="Thoát", font=("Arial", 20), bg="lightcoral", command=self.root.destroy).pack(pady=10)

    def quit_game(self):
        start_menu(self.root)


def start_menu(root=None):
    if root is None:
        root = tk.Tk()
        root.title("Memory Game")
        root.attributes("-fullscreen", True)

    for w in root.winfo_children():
        w.destroy()

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    bg = load_local_image(BG_NORMAL, (screen_w, screen_h))
    bg_label = tk.Label(root, image=bg)
    bg_label.image = bg
    bg_label.place(x=0, y=0)

    tk.Label(root, text="MEMORY GAME", font=("Arial", 32, "bold"), bg="#ffffff").pack(pady=20)
    tk.Label(root, text="Lựa Chọn Cấp Độ", font=("Arial", 24, "bold"), bg="#ffffff").pack(pady=5)

    def start(level):
        MemoryGame(root, level)

    level_frame = tk.Frame(root, bg="#ffffff")
    level_frame.pack(pady=20)

    tk.Button(level_frame, text="Cấp Độ 1\n(2x2, 4 bước, 30s)", font=("Arial", 18, "bold"),
              command=lambda: start(1)).grid(row=0, column=0, padx=30, pady=10)
    tk.Button(level_frame, text="Cấp Độ 2\n(4x4, 16 bước, 60s)", font=("Arial", 18, "bold"),
              command=lambda: start(2)).grid(row=1, column=0, padx=30, pady=10)
    tk.Button(level_frame, text="Cấp Độ 3\n(6x6, 46 bước, 120s)", font=("Arial", 18, "bold"),
              command=lambda: start(3)).grid(row=2, column=0, padx=30, pady=10)

    tk.Button(root, text="Thoát", font=("Arial", 18),
              bg="lightcoral", command=root.destroy).pack(pady=30)

    root.mainloop()


# chạy game
start_menu()
