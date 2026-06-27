import tkinter as tk
import random
import string

class CleanCard(tk.Canvas):
    def __init__(self, parent, text, font_size, command, bg_color, hover_color, radius=14, **kwargs):
        super().__init__(parent, borderwidth=0, highlightthickness=0, cursor="hand2", **kwargs)
        self.command = command
        self.text = text
        self.font_size = font_size
        self.default_bg = bg_color
        self.hover_bg = hover_color
        self.current_bg = bg_color
        self.radius = radius
        self.state = "normal"
        
        self.bind("<Configure>", self._draw)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _draw(self, event=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 10 or h < 10:
            return
            
        r = min(self.radius, w//2, h//2)
        
        self.rect = self.create_polygon(
            r, 0, w-r, 0, w, 0, w, r, w, h-r, w, h, w-r, h, 
            r, h, 0, h, 0, h-r, 0, r, 0, 0,
            smooth=True, fill=self.current_bg, outline=""
        )
        
        self.text_item = self.create_text(
            w//2, h//2, text=self.text, fill="#5a6578", 
            font=("Avenir", self.font_size, "bold")
        )

    def _on_enter(self, event):
        if self.state == "normal":
            self.current_bg = self.hover_bg
            self.itemconfig(self.rect, fill=self.hover_bg)

    def _on_leave(self, event):
        if self.state == "normal":
            self.current_bg = self.default_bg
            self.itemconfig(self.rect, fill=self.default_bg)

    def _on_click(self, event):
        if self.state == "normal":
            self.command()

    def set_color(self, fill_color, text_color="#ffffff"):
        self.default_bg = fill_color
        self.hover_bg = fill_color
        self.current_bg = fill_color
        self.itemconfig(self.rect, fill=fill_color, outline="")
        self.itemconfig(self.text_item, fill=text_color)

    def disable(self):
        self.state = "disabled"
        self.config(cursor="")


class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Odd One Out")
        
        self.root.resizable(False, False)
        
        self.bg_color = "#ffffff"       
        self.btn_color = "#f6fbfc"      
        self.btn_hover = "#e4edf2"      
        self.accent_green = "#2ecc71"   
        self.accent_red = "#e74c3c"     
        
        self.root.configure(bg=self.bg_color)
        self.current_level = 1
        
        self.header_frame = tk.Frame(root, bg=self.bg_color, pady=20)
        self.header_frame.pack(fill=tk.X)
        
        self.level_label = tk.Label(
            self.header_frame, 
            text=f"LEVEL {self.current_level}", 
            font=("Avenir", 11, "bold"), 
            fg="#a0aec0", 
            bg=self.bg_color
        )
        self.level_label.pack()
        
        self.status_label = tk.Label(
            self.header_frame, 
            text="Find the imposter", 
            font=("Avenir", 16, "bold"), 
            fg="#2d3748", 
            bg=self.bg_color,
            pady=4
        )
        self.status_label.pack()
        
        self.frame = tk.Frame(root, bg=self.bg_color)
        self.frame.pack(padx=35, pady=5)
        
        self.load_next_level()

    def generate_symbols(self):
        presets = {
            1: ("O", "0"),
            2: ("E", "F"),
            3: ("M", "N"),
            4: ("rn", "m")
        }
        if self.current_level in presets:
            return presets[self.current_level]
        
        pool = string.ascii_uppercase if random.choice([True, False]) else string.ascii_lowercase
        char1, char2 = random.sample(pool, 2)
        return char1, char2

    def load_next_level(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        self.grid_size = min(3 + (self.current_level - 1) // 1, 9)
        self.normal_symbol, self.imposter_symbol = self.generate_symbols()
        
        self.level_label.config(text=f"LEVEL {self.current_level}")
        self.status_label.config(text="Find the imposter", fg="#2d3748")
        
        self.imposter_row = random.randint(0, self.grid_size - 1)
        self.imposter_col = random.randint(0, self.grid_size - 1)
        
        if self.grid_size <= 3:
            card_size, font_size, padding, radius = 80, 20, 8, 14
        elif self.grid_size <= 4:
            card_size, font_size, padding, radius = 70, 18, 6, 12
        elif self.grid_size <= 5:
            card_size, font_size, padding, radius = 60, 16, 5, 10
        elif self.grid_size <= 6:
            card_size, font_size, padding, radius = 52, 14, 4, 8
        elif self.grid_size <= 7:
            card_size, font_size, padding, radius = 45, 12, 3, 7
        else:
            card_size, font_size, padding, radius = 38, 11, 3, 6

        self.buttons = []
        
        for r in range(self.grid_size):
            row_buttons = []
            for c in range(self.grid_size):
                symbol = self.imposter_symbol if (r == self.imposter_row and c == self.imposter_col) else self.normal_symbol
                
                btn = CleanCard(
                    self.frame, 
                    text=symbol,
                    font_size=font_size,
                    command=lambda row=r, col=c: self.check_guess(row, col),
                    bg_color=self.btn_color,
                    hover_color=self.btn_hover,
                    width=card_size,
                    height=card_size,
                    radius=radius,
                    bg=self.bg_color
                )
                btn.grid(row=r, column=c, padx=padding, pady=padding)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

    def check_guess(self, clicked_row, clicked_col):
        target_btn = self.buttons[clicked_row][clicked_col]
        
        if clicked_row == self.imposter_row and clicked_col == self.imposter_col:
            self.status_label.config(text="Level Up!", fg=self.accent_green)
            target_btn.set_color(self.accent_green, text_color="#ffffff")
            
            for row in self.buttons:
                for btn in row:
                    btn.disable()
            
            self.current_level += 1
            self.root.after(1000, self.load_next_level)
        else:
            self.status_label.config(text="Try Again", fg=self.accent_red)
            target_btn.set_color(self.accent_red, text_color="#ffffff")
            target_btn.disable()

root = tk.Tk()
game = GameApp(root)
root.mainloop()
