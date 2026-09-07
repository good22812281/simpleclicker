import customtkinter as ctk
import tkinter as tk
import random
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


root = ctk.CTk()
root.title("Кликер")
root.geometry("1580x720")
root.resizable(False, False)

BACKGROUNDS = [
    {"threshold": 50, "file": "25.png", "name": "чирно"},
    {"threshold": 500, "file": "50.png", "name": "хонг-мейлинг"},
    {"threshold": 1000, "file": "100.png", "name": "пачули"},
    {"threshold": 2000, "file": "2000.png", "name": "рейму"},
    {"threshold": 6000, "file": "6000.png", "name": "мариса"},
    {"threshold": 10000, "file": "10000.png", "name": "коиси"},
    {"threshold": 25000, "file": "25000.png", "name": "сатори"},
    {"threshold": 60000, "file": "60000.png", "name": "сакуя"},
]

for bg in BACKGROUNDS:
    try:
        pil_image = Image.open(bg["file"])
        bg["image"] = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(1280, 720))
    except FileNotFoundError:
        bg["image"] = None

unlocked = set()

count = 0
passive_started = False
click_power = 1
upgrade_cost = 50
click_multiplier = 1
multiplier_cost = 1000
auto_power = 1
auto_upgrade_cost = 100
manual_bg_selected = False
special_currency = 0
auto_interval = 1000
speed_cost = 5
auto_multiplier = 1
auto_multiplier_cost = 10

sidebar = ctk.CTkFrame(root, width=300, height=720, corner_radius=0)
sidebar.place(x=0, y=0)


background_label = ctk.CTkLabel(root, text="", width=1280, height=720)
background_label.place(x=300, y=0)

def update_background():
    global manual_bg_selected

    for bg in BACKGROUNDS:
        if count >= bg["threshold"] and bg["threshold"] not in unlocked:
            unlocked.add(bg["threshold"])

    if manual_bg_selected:
        return

    current = None
    for bg in sorted(BACKGROUNDS, key=lambda b: b["threshold"], reverse=True):
        if count >= bg["threshold"]:
            current = bg["image"]
            break

    if current:
        background_label.configure(image=current)
    else:
        background_label.configure(image="")

def click():
    global count
    count += click_power * click_multiplier
    label.configure(text=f"Счетчик: {count}")
    update_background()

def passive_income():
    global count
    count += auto_power * auto_multiplier
    label.configure(text=f"Счетчик: {count}")
    update_background()
    root.after(auto_interval, passive_income)


def buy_auto():
    global passive_started
    if count >= 100:
        if not passive_started:
            passive_started = True
            passive_income()
            buy_button.configure(text="Автокликер включен!")
    else:
        buy_button.configure(text="Не хватает очков, нужно 100")

def buy_upgrade():
    global count, click_power, upgrade_cost
    if count >= upgrade_cost:
        count -= upgrade_cost
        click_power += 1
        upgrade_cost = int(upgrade_cost * 2.25)
        label.configure(text=f"Счетчик: {count}")
        upgrade_button.configure(text=f"Сила клика +1 (цена: {upgrade_cost})")
        power_label.configure(text=f"Сила клика: {click_power}")
        update_background()
    else:
        upgrade_button.configure(text=f"Не хватает очков (нужно {upgrade_cost})")

def buy_multiplier():
    global count, click_multiplier, multiplier_cost
    if count >= multiplier_cost:
        count -= multiplier_cost
        click_multiplier += 1
        multiplier_cost = int(multiplier_cost * 2.5)
        label.configure(text=f"Счетчик: {count}")
        multiplier_button.configure(text=f"Множитель x{click_multiplier} (цена: {multiplier_cost})")
        update_background()
    else:
        multiplier_button.configure(text=f"Не хватает очков (нужно {multiplier_cost})")

def buy_auto_upgrade():
    global count, auto_power, auto_upgrade_cost
    if not passive_started:
        auto_upgrade_button.configure(text="Сначала купите автокликер")
        return

    if count >= auto_upgrade_cost:
        count -= auto_upgrade_cost
        auto_power += 1
        auto_upgrade_cost = int(auto_upgrade_cost * 2.5)
        label.configure(text=f"Счетчик: {count}")
        auto_upgrade_button.configure(text=f"Автодоход +1 (цена: {auto_upgrade_cost})")
        auto_power_label.configure(text=f"Доход автокликера: {auto_power}/сек")
        update_background()
    else:
        auto_upgrade_button.configure(text=f"Не хватает очков (нужно {auto_upgrade_cost})")

def buy_auto_multiplier():
    global special_currency, auto_multiplier, auto_multiplier_cost

    if special_currency >= auto_multiplier_cost:
        special_currency -= auto_multiplier_cost
        auto_multiplier += 1
        auto_multiplier_cost = int(auto_multiplier_cost * 1.8)

        special_label.configure(text=f"Спец. валюта: {special_currency}")
        auto_mult_label.configure(text=f"Множитель автодохода: x{auto_multiplier}")
        auto_mult_btn.configure(text=f"Увеличить множитель (цена: {auto_multiplier_cost})")
    else:
        auto_mult_label.configure(text=f"Не хватает спец. валюты (нужно {auto_multiplier_cost})")

def open_bg_selector():
    selector = ctk.CTkToplevel(root)
    selector.title("Выбор фона")
    selector.geometry("1000x150")
    selector.attributes("-topmost", True)

    def choose(img):
        global manual_bg_selected
        manual_bg_selected = True
        background_label.configure(image=img)

    def reset_auto():
        global manual_bg_selected
        manual_bg_selected = False
        update_background()

    for bg in BACKGROUNDS:
        if bg["threshold"] in unlocked:
            ctk.CTkButton(
                selector,
                text=bg["name"],
                command=lambda img=bg["image"]: choose(img)
            ).pack(side="left", padx=10, pady=20)
        else:
            ctk.CTkButton(
                selector,
                text=f"??? (нужно {bg['threshold']})",
                state="disabled"
            ).pack(side="left", padx=10, pady=20)

    ctk.CTkButton(selector, text="Авто (по очкам)", command=reset_auto).pack(side="left", padx=10, pady=20)

def buy_speed():
    global special_currency, auto_interval, speed_cost
    if auto_interval <= 100:
        speed_shop_label.configure(text="Максимальная скорость достигнута!")
        return

    if special_currency >= speed_cost:
        special_currency -= speed_cost
        auto_interval = max(100, auto_interval - 100)
        speed_cost += 1
        special_label.configure(text=f"Спец. валюта: {special_currency}")
        speed_shop_label.configure(text=f"Интервал автоклика: {auto_interval}мс")
        speed_buy_btn.configure(text=f"Ускорить (цена: {speed_cost})")
    else:
        speed_shop_label.configure(text=f"Не хватает спец. валюты (нужно {speed_cost})")

def add_special_currency(amount):
    global special_currency
    special_currency += amount
    special_label.configure(text=f"Спец. валюта: {special_currency}")


def open_menu():
    menu = ctk.CTkToplevel(root)
    menu.title("Меню")
    menu.geometry("300x200")
    menu.attributes("-topmost", True)

    minigames_btn = ctk.CTkButton(
        menu, text="Мини-игры", command=lambda: open_minigames(menu)
    )
    minigames_btn.pack(pady=20)

def open_shop(parent):
    shop = ctk.CTkToplevel(parent)
    shop.title("Магазин")
    shop.geometry("350x260")
    shop.attributes("-topmost", True)

    global speed_shop_label, speed_buy_btn, auto_mult_label, auto_mult_btn

    speed_shop_label = ctk.CTkLabel(shop, text=f"Интервал автоклика: {auto_interval}мс", font=("Arial", 12))
    speed_shop_label.pack(pady=10)

    speed_buy_btn = ctk.CTkButton(shop, text=f"Ускорить (цена: {speed_cost})", command=buy_speed)
    speed_buy_btn.pack(pady=10)

    auto_mult_label = ctk.CTkLabel(shop, text=f"Множитель автодохода: x{auto_multiplier}", font=("Arial", 12))
    auto_mult_label.pack(pady=10)

    auto_mult_btn = ctk.CTkButton(shop, text=f"Увеличить множитель (цена: {auto_multiplier_cost})", command=buy_auto_multiplier)
    auto_mult_btn.pack(pady=10)


def open_minigames(parent):
    minigames = ctk.CTkToplevel(parent)
    minigames.title("Мини-игры")
    minigames.geometry("300x250")
    minigames.attributes("-topmost", True)

    snake_btn = ctk.CTkButton(
        minigames, text="Змейка", command=lambda: open_snake(minigames)
    )
    snake_btn.pack(pady=10)

    shop_btn = ctk.CTkButton(
        minigames, text="Магазин", command=lambda: open_shop(minigames)
    )
    shop_btn.pack(pady=10)

def open_snake(parent):
    game_window = ctk.CTkToplevel(parent)
    game_window.title("Змейка")
    game_window.geometry("420x460")
    game_window.attributes("-topmost", True)

    CELL = 20
    WIDTH = 400
    HEIGHT = 400

    canvas = tk.Canvas(game_window, width=WIDTH, height=HEIGHT, bg="black")
    canvas.pack(pady=10)

    snake = [(100, 100), (80, 100), (60, 100)]
    direction = "Right"
    food = (200, 200)
    game_over = False

    def draw():
        canvas.delete("all")
        for x, y in snake:
            canvas.create_rectangle(x, y, x + CELL, y + CELL, fill="green")
        fx, fy = food
        canvas.create_rectangle(fx, fy, fx + CELL, fy + CELL, fill="red")
        if game_over:
            canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Game Over", fill="white", font=("Arial", 24))

    def move():
        nonlocal snake, food, game_over
        if game_over:
            return

        head_x, head_y = snake[0]
        if direction == "Right":
            new_head = (head_x + CELL, head_y)
        elif direction == "Left":
            new_head = (head_x - CELL, head_y)
        elif direction == "Up":
            new_head = (head_x, head_y - CELL)
        else:
            new_head = (head_x, head_y + CELL)

        if (new_head[0] < 0 or new_head[0] >= WIDTH or
            new_head[1] < 0 or new_head[1] >= HEIGHT or
            new_head in snake):
            game_over = True
            draw()
            return

        snake.insert(0, new_head)

        if new_head == food:
            add_special_currency(1)
            food = (
                random.randrange(0, WIDTH, CELL),
                random.randrange(0, HEIGHT, CELL)
            )
        else:
            snake.pop()

        draw()
        game_window.after(150, move)

    def change_direction(event):
        nonlocal direction
        key = event.keysym
        opposite = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if key in ["Up", "Down", "Left", "Right"] and key != opposite.get(direction):
            direction = key

    game_window.bind("<KeyPress>", change_direction)
    game_window.focus_set()

    draw()
    move()


PADDING_X = 20

label = ctk.CTkLabel(sidebar, text="Счетчик: 0", font=("Arial", 16, "bold"))
label.place(x=PADDING_X, y=20)

power_label = ctk.CTkLabel(sidebar, text="Сила клика: 1", font=("Arial", 12))
power_label.place(x=PADDING_X, y=55)

auto_power_label = ctk.CTkLabel(sidebar, text="Доход автокликера: 1/сек", font=("Arial", 12))
auto_power_label.place(x=PADDING_X, y=80)

special_label = ctk.CTkLabel(sidebar, text="Спец. валюта: 0", font=("Arial", 12))
special_label.place(x=PADDING_X, y=105)

btn = ctk.CTkButton(sidebar, text="Кнопочка", command=click, width=260)
btn.place(x=PADDING_X, y=145)

buy_button = ctk.CTkButton(sidebar, text="Включить автокликер?", command=buy_auto, width=260)
buy_button.place(x=PADDING_X, y=190)

upgrade_button = ctk.CTkButton(sidebar, text=f"Сила клика +1 (цена: {upgrade_cost})", command=buy_upgrade, width=260)
upgrade_button.place(x=PADDING_X, y=235)

auto_upgrade_button = ctk.CTkButton(sidebar, text=f"Автодоход +1 (цена: {auto_upgrade_cost})", command=buy_auto_upgrade, width=260)
auto_upgrade_button.place(x=PADDING_X, y=280)

multiplier_button = ctk.CTkButton(sidebar, text=f"Множитель x{click_multiplier} (цена: {multiplier_cost})", command=buy_multiplier, width=260)
multiplier_button.place(x=PADDING_X, y=325)

selector_button = ctk.CTkButton(sidebar, text="Выбрать фон", command=open_bg_selector, width=260)
selector_button.place(x=PADDING_X, y=370)

menu_button = ctk.CTkButton(sidebar, text="Меню", command=open_menu, width=260)
menu_button.place(x=PADDING_X, y=415)

root.mainloop()