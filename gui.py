import customtkinter as ctk
import tkinter as tk
import random
from PIL import Image
import json
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ---------- Глобальные настройки и состояние ----------
SAVE_FILE = "clicker_save.json"

root = ctk.CTk()
root.title("Кликер")
root.geometry("1580x720")
root.resizable(False, False)

BACKGROUNDS = [
    {"threshold": 50, "file": "25.png", "name": "чирно"},
    {"threshold": 500, "file": "50.png", "name": "хонг-мейлинг"},
    {"threshold": 1000, "file": "100.png", "name": "пачули"},
    {"threshold": 2000, "file": "2000.png", "name": "рейму"},
    {"threshold": 6000, "file": "60001.png", "name": "мариса"},
    {"threshold": 10000, "file": "100001.png", "name": "коиси"},
    {"threshold": 25000, "file": "250001.png", "name": "сатори"},
    {"threshold": 60000, "file": "600001.png", "name": "сакуя"},
    {"threshold": 100000, "file": "100000.png", "name": "ююко"},
    {"threshold": 200000, "file": "200000.png", "name": "окуу"},
]

for bg in BACKGROUNDS:
    try:
        pil_image = Image.open(bg["file"])
        bg["image"] = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(1280, 720))
    except FileNotFoundError:
        bg["image"] = None

# ---------- Переменные состояния ----------
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
fish_food_eaten = 0  # сколько кормов съедено рыбками всего

# ---------- Рыбки ----------
FISH_TYPES = [
    {"name": "Гуппи",              "rarity": "Обычная",      "weight": 45, "income": 1,  "color": "#B0C4DE"},
    {"name": "Неон",                "rarity": "Обычная",      "weight": 45, "income": 1,  "color": "#7FDBFF"},
    {"name": "Золотая рыбка",       "rarity": "Необычная",    "weight": 22, "income": 3,  "color": "#FFD700"},
    {"name": "Скалярия",            "rarity": "Необычная",    "weight": 22, "income": 3,  "color": "#FF8C69"},
    {"name": "Дискус",              "rarity": "Редкая",       "weight": 10, "income": 8,  "color": "#FF6B6B"},
    {"name": "Рыба-бабочка",        "rarity": "Редкая",       "weight": 10, "income": 8,  "color": "#9B59B6"},
    {"name": "Рыба-ангел",          "rarity": "Эпическая",    "weight": 4,  "income": 20, "color": "#F39C12"},
    {"name": "Дракон кои",          "rarity": "Легендарная",  "weight": 1,  "income": 50, "color": "#FF1744"},
]
RARITY_TEXT_COLOR = {
    "Обычная": "#B0B0B0",
    "Необычная": "#4CD964",
    "Редкая": "#4A90E2",
    "Эпическая": "#B455F0",
    "Легендарная": "#FFB300",
}
FISH_PACK_COST = 20
FISH_BOOST_DURATION = 20

SELL_PRICES = {
    "Обычная": 5,
    "Необычная": 10,
    "Редкая": 25,
    "Эпическая": 60,
    "Легендарная": 150,
}
owned_fish = []            # список купленных рыбок
fish_boost_seconds_left = 0
fish_income_label = None
aquarium_status_var = {"window": None, "canvas": None}

# ---------- Функции сохранения и загрузки ----------
def save_game():
    data = {
        "count": count,
        "passive_started": passive_started,
        "click_power": click_power,
        "upgrade_cost": upgrade_cost,
        "click_multiplier": click_multiplier,
        "multiplier_cost": multiplier_cost,
        "auto_power": auto_power,
        "auto_upgrade_cost": auto_upgrade_cost,
        "manual_bg_selected": manual_bg_selected,
        "special_currency": special_currency,
        "auto_interval": auto_interval,
        "speed_cost": speed_cost,
        "auto_multiplier": auto_multiplier,
        "auto_multiplier_cost": auto_multiplier_cost,
        "unlocked": sorted(list(unlocked)),
        "owned_fish": owned_fish,
        "fish_food_eaten": fish_food_eaten,
    }
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

def load_game():
    global count, passive_started, click_power, upgrade_cost
    global click_multiplier, multiplier_cost, auto_power, auto_upgrade_cost
    global manual_bg_selected, special_currency, auto_interval, speed_cost
    global auto_multiplier, auto_multiplier_cost, unlocked, owned_fish, fish_food_eaten

    if not os.path.exists(SAVE_FILE):
        return

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        count = data.get("count", 0)
        passive_started = data.get("passive_started", False)
        click_power = data.get("click_power", 1)
        upgrade_cost = data.get("upgrade_cost", 50)
        click_multiplier = data.get("click_multiplier", 1)
        multiplier_cost = data.get("multiplier_cost", 1000)
        auto_power = data.get("auto_power", 1)
        auto_upgrade_cost = data.get("auto_upgrade_cost", 100)
        manual_bg_selected = data.get("manual_bg_selected", False)
        special_currency = data.get("special_currency", 0)
        auto_interval = data.get("auto_interval", 1000)
        speed_cost = data.get("speed_cost", 5)
        auto_multiplier = data.get("auto_multiplier", 1)
        auto_multiplier_cost = data.get("auto_multiplier_cost", 10)
        unlocked = set(data.get("unlocked", []))
        owned_fish = data.get("owned_fish", [])
        fish_food_eaten = data.get("fish_food_eaten", 0)
    except Exception as e:
        print(f"Ошибка загрузки: {e}")

def auto_save():
    save_game()
    root.after(30000, auto_save)  # каждые 30 секунд

def on_close():
    save_game()
    root.destroy()

# ---------- Инициализация UI ----------
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

    # Создаем горизонтальный прокручиваемый контейнер
    scroll_frame = ctk.CTkScrollableFrame(selector, orientation="horizontal", height=100, width=950)
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

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
                scroll_frame,
                text=bg["name"],
                command=lambda img=bg["image"]: choose(img)
            ).pack(side="left", padx=10, pady=20)
        else:
            ctk.CTkButton(
                scroll_frame,
                text=f"??? (нужно {bg['threshold']})",
                state="disabled"
            ).pack(side="left", padx=10, pady=20)

    ctk.CTkButton(scroll_frame, text="Авто (по очкам)", command=reset_auto).pack(side="left", padx=10, pady=20)

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

# ---------- Логика рыбок ----------
def total_fish_income():
    return sum(f["income"] for f in owned_fish)

def update_fish_income_label():
    total = total_fish_income()
    if fish_boost_seconds_left > 0:
        fish_income_label.configure(
            text=f"Доход рыбок: {total * 2}/сек (буст x2, {fish_boost_seconds_left}с)"
        )
    else:
        fish_income_label.configure(text=f"Доход рыбок: {total}/сек")

def get_random_fish():
    weights = [f["weight"] for f in FISH_TYPES]
    chosen = random.choices(FISH_TYPES, weights=weights, k=1)[0]
    return dict(chosen)

def buy_fish_pack():
    global special_currency
    if special_currency >= FISH_PACK_COST:
        special_currency -= FISH_PACK_COST
        new_fish = get_random_fish()
        owned_fish.append(new_fish)

        special_label.configure(text=f"Спец. валюта: {special_currency}")
        fish_pack_label.configure(
            text=f"Выпала: {new_fish['name']} ({new_fish['rarity']}, +{new_fish['income']}/сек)!"
        )
        update_fish_income_label()
    else:
        fish_pack_label.configure(text=f"Не хватает спец. валюты (нужно {FISH_PACK_COST})")

def activate_fish_boost():
    global fish_boost_seconds_left
    fish_boost_seconds_left = FISH_BOOST_DURATION

def fish_income_tick():
    global count, fish_boost_seconds_left

    if owned_fish:
        base = total_fish_income()
        multiplier = 2 if fish_boost_seconds_left > 0 else 1
        count += base * multiplier
        label.configure(text=f"Счетчик: {count}")
        update_background()

    if fish_boost_seconds_left > 0:
        fish_boost_seconds_left -= 1

    if fish_income_label is not None:
        update_fish_income_label()

    root.after(1000, fish_income_tick)

# ---------- Меню и окна ----------
def open_menu():
    menu = ctk.CTkToplevel(root)
    menu.title("Меню")
    menu.geometry("300x250")


    # Доступ к мини-играм только с 6000 очков
    if count >= 6000:
        minigames_btn = ctk.CTkButton(
            menu, text="Мини-игры", command=lambda: open_minigames(menu)
        )
    else:
        minigames_btn = ctk.CTkButton(
            menu, text=f"Мини-игры (нужно 6000)", state="disabled"
        )
    minigames_btn.pack(pady=15)

    aquarium_btn = ctk.CTkButton(
        menu, text="Аквариум", command=lambda: open_aquarium(menu)
    )
    aquarium_btn.pack(pady=15)

def open_shop(parent):
    shop = ctk.CTkToplevel(parent)
    shop.title("Магазин")
    shop.geometry("360x600")


    global speed_shop_label, speed_buy_btn, auto_mult_label, auto_mult_btn
    global fish_pack_label

    speed_shop_label = ctk.CTkLabel(shop, text=f"Интервал автоклика: {auto_interval}мс", font=("Arial", 12))
    speed_shop_label.pack(pady=10)

    speed_buy_btn = ctk.CTkButton(shop, text=f"Ускорить (цена: {speed_cost})", command=buy_speed)
    speed_buy_btn.pack(pady=10)

    auto_mult_label = ctk.CTkLabel(shop, text=f"Множитель автодохода: x{auto_multiplier}", font=("Arial", 12))
    auto_mult_label.pack(pady=10)

    auto_mult_btn = ctk.CTkButton(shop, text=f"Увеличить множитель (цена: {auto_multiplier_cost})", command=buy_auto_multiplier)
    auto_mult_btn.pack(pady=10)

    separator = ctk.CTkLabel(shop, text="— Аквариум —", font=("Arial", 14, "bold"))
    separator.pack(pady=(20, 5))

    fish_pack_label = ctk.CTkLabel(
        shop,
        text=f"Рыбок: {len(owned_fish)} (доход {total_fish_income()}/сек)",
        font=("Arial", 12)
    )
    fish_pack_label.pack(pady=10)

    fish_pack_btn = ctk.CTkButton(
        shop, text=f"Пакет с рыбкой (цена: {FISH_PACK_COST})", command=buy_fish_pack
    )
    fish_pack_btn.pack(pady=10)

    # --- Секция продажи рыбок ---
    sell_separator = ctk.CTkLabel(shop, text="— Продажа рыбок —", font=("Arial", 14, "bold"))
    sell_separator.pack(pady=(20, 5))

    # Контейнер для списка продажи
    sell_frame = ctk.CTkFrame(shop, fg_color="transparent")
    sell_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def update_sell_frame():
        # Очищаем текущее содержимое
        for widget in sell_frame.winfo_children():
            widget.destroy()

        if not owned_fish:
            empty_label = ctk.CTkLabel(sell_frame, text="Нет рыбок для продажи", font=("Arial", 11))
            empty_label.pack(pady=10)
            return

        # Собираем уникальные виды рыб и их количество
        fish_counts = {}
        for fish in owned_fish:
            name = fish["name"]
            if name not in fish_counts:
                fish_counts[name] = {"data": fish, "count": 0}
            fish_counts[name]["count"] += 1

        # Создаём элементы для каждого вида
        for name, info in fish_counts.items():
            fish_data = info["data"]
            rarity = fish_data["rarity"]
            price = SELL_PRICES.get(rarity, 5)
            count = info["count"]

            row = ctk.CTkFrame(sell_frame, fg_color="#2b2b2b", corner_radius=6)
            row.pack(fill="x", pady=3)

            # Текст: Название (редкость) xКоличество
            text = f"{name} ({rarity}) x{count}"
            label = ctk.CTkLabel(row, text=text, font=("Arial", 10), width=180, anchor="w")
            label.pack(side="left", padx=5, pady=2)

            # Кнопка продажи
            sell_btn = ctk.CTkButton(
                row,
                text=f"Продать за {price}",
                width=100,
                height=24,
                font=("Arial", 10),
                command=lambda n=name: sell_one_fish(n)
            )
            sell_btn.pack(side="right", padx=5, pady=2)

    def sell_one_fish(fish_name):
        global special_currency
        # Находим индекс первой рыбы с таким именем
        for i, fish in enumerate(owned_fish):
            if fish["name"] == fish_name:
                rarity = fish["rarity"]
                price = SELL_PRICES.get(rarity, 5)
                # Удаляем рыбу
                del owned_fish[i]
                # Начисляем валюту
                special_currency += price
                special_label.configure(text=f"Спец. валюта: {special_currency}")
                # Обновляем лейблы
                fish_pack_label.configure(
                    text=f"Рыбок: {len(owned_fish)} (доход {total_fish_income()}/сек)"
                )
                update_fish_income_label()
                # Обновляем список продажи
                update_sell_frame()
                break

    update_sell_frame()

def open_minigames(parent):
    minigames = ctk.CTkToplevel(parent)
    minigames.title("Мини-игры")
    minigames.geometry("300x220")


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
    game_window.geometry("420x500")


    CELL = 20
    WIDTH = 400
    HEIGHT = 400

    canvas = tk.Canvas(game_window, width=WIDTH, height=HEIGHT, bg="black")
    canvas.pack(pady=10)

    # Счетчик съеденных яблок и текущая награда
    score = 0
    reward = 1  # награда за следующее яблоко

    # Лейбл для отображения счета и награды
    info_label = ctk.CTkLabel(game_window, text=f"Яблок: {score} | Награда: {reward}", font=("Arial", 12))
    info_label.pack(pady=(0, 5))

    snake = [(100, 100), (80, 100), (60, 100)]
    direction = "Right"
    food = (200, 200)
    game_over = False

    def update_info_label():
        info_label.configure(text=f"Яблок: {score} | Награда: {1 + (score // 5)}")

    def draw():
        canvas.delete("all")
        for x, y in snake:
            canvas.create_rectangle(x, y, x + CELL, y + CELL, fill="green")
        fx, fy = food
        canvas.create_rectangle(fx, fy, fx + CELL, fy + CELL, fill="red")
        if game_over:
            canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Game Over", fill="white", font=("Arial", 24))

    def move():
        nonlocal snake, food, game_over, score, reward
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
            # Награда увеличивается на 1 каждые 5 съеденных яблок
            reward = 1 + (score // 5)
            add_special_currency(reward)
            score += 1
            update_info_label()
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

# ---------- Аквариум ----------
def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def _lerp_color(c1, c2, t):
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"

def _size_for_rarity(rarity):
    return {
        "Обычная": 10,
        "Необычная": 12,
        "Редкая": 14,
        "Эпическая": 17,
        "Легендарная": 21,
    }.get(rarity, 10)

def open_aquarium(parent):
    aquarium = ctk.CTkToplevel(parent)
    aquarium.title("Аквариум")
    aquarium.geometry("560x560")


    WIDTH = 520
    HEIGHT = 420
    TOP_COLOR = "#0f2f4a"
    BOTTOM_COLOR = "#04121f"
    SAND_HEIGHT = 26

    canvas = tk.Canvas(aquarium, width=WIDTH, height=HEIGHT, bg=TOP_COLOR, highlightthickness=0)
    canvas.pack(pady=10)

    info_label = ctk.CTkLabel(
        aquarium,
        text="Клик по воде — упадёт корм. Рыбка съест его и включит буст x2 на пассивный доход рыбок",
        font=("Arial", 11),
        wraplength=520,
    )
    info_label.pack(pady=(0, 5))

    if not owned_fish:
        empty_label = ctk.CTkLabel(
            aquarium,
            text="Тут пока пусто! Купи пакет с рыбкой в Магазине (Мини-игры → Магазин) за 20 спец. валюты.",
            font=("Arial", 13),
        )
        empty_label.pack(pady=10)
        canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=TOP_COLOR, outline="")
        return

    BAND_HEIGHT = 20
    bands = []
    n_bands = HEIGHT // BAND_HEIGHT + 1
    for i in range(n_bands):
        t = i / max(1, n_bands - 1)
        bands.append(_lerp_color(TOP_COLOR, BOTTOM_COLOR, t))

    plant_positions = [40, 110, 410, 480]

    fish_sprites = []
    for data in owned_fish:
        fish_sprites.append({
            "data": data,
            "x": random.randint(30, WIDTH - 30),
            "y": random.randint(40, HEIGHT - SAND_HEIGHT - 20),
            "dx": random.choice([-0.6, -0.4, 0.4, 0.6]),
            "dy": random.choice([-0.15, 0.15]),
            "size": _size_for_rarity(data["rarity"]),
        })

    bubbles = []
    for _ in range(12):
        bubbles.append({
            "x": random.randint(10, WIDTH - 10),
            "y": random.randint(0, HEIGHT),
            "r": random.randint(2, 4),
            "speed": random.uniform(0.3, 0.8),
        })

    food_list = []

    def drop_food(event):
        if event.y > HEIGHT - SAND_HEIGHT:
            return
        food_list.append({"x": event.x, "y": event.y})

    canvas.bind("<Button-1>", drop_food)

    def closest_food(fish):
        if not food_list:
            return None
        return min(food_list, key=lambda f: (f["x"] - fish["x"]) ** 2 + (f["y"] - fish["y"]) ** 2)

    def draw_fish(fish):
        x, y = fish["x"], fish["y"]
        size = fish["size"]
        color = fish["data"]["color"]
        facing_right = fish["dx"] >= 0

        if fish["data"]["rarity"] in ("Эпическая", "Легендарная"):
            canvas.create_oval(
                x - size - 5, y - size / 1.6 - 5, x + size + 5, y + size / 1.6 + 5,
                outline=color, width=1
            )

        tail_dir = -1 if facing_right else 1
        canvas.create_polygon(
            x + tail_dir * size, y,
            x + tail_dir * (size + 8), y - size / 2,
            x + tail_dir * (size + 8), y + size / 2,
            fill=color, outline=""
        )
        canvas.create_oval(
            x - size, y - size / 1.6, x + size, y + size / 1.6,
            fill=color, outline=""
        )
        eye_x = x + (size / 1.8 if facing_right else -size / 1.8)
        canvas.create_oval(eye_x - 2, y - 2, eye_x + 2, y + 2, fill="black", outline="")

    def draw_scene():
        canvas.delete("all")

        for i, color in enumerate(bands):
            canvas.create_rectangle(0, i * BAND_HEIGHT, WIDTH, (i + 1) * BAND_HEIGHT, fill=color, outline="")

        for b in bubbles:
            canvas.create_oval(
                b["x"] - b["r"], b["y"] - b["r"], b["x"] + b["r"], b["y"] + b["r"],
                outline="#a8d8f0", width=1
            )

        canvas.create_rectangle(0, HEIGHT - SAND_HEIGHT, WIDTH, HEIGHT, fill="#c2a878", outline="")

        for px in plant_positions:
            canvas.create_polygon(
                px, HEIGHT - SAND_HEIGHT,
                px - 8, HEIGHT - SAND_HEIGHT - 45,
                px, HEIGHT - SAND_HEIGHT - 60,
                px + 8, HEIGHT - SAND_HEIGHT - 45,
                fill="#2e7d4f", outline=""
            )

        for f in food_list:
            canvas.create_oval(f["x"] - 3, f["y"] - 3, f["x"] + 3, f["y"] + 3, fill="#e6c27a", outline="")

        for fish in fish_sprites:
            draw_fish(fish)

        if fish_boost_seconds_left > 0:
            canvas.create_text(
                WIDTH // 2, 16,
                text=f"⚡ Буст x2 активен: {fish_boost_seconds_left}с",
                fill="#ffd54f", font=("Arial", 13, "bold")
            )
        else:
            total = total_fish_income()
            canvas.create_text(
                WIDTH // 2, 16,
                text=f"Доход рыбок: {total}/сек — покорми их для буста!",
                fill="#dbeeff", font=("Arial", 11)
            )

    def update_aquarium():
        global fish_food_eaten

        if not aquarium.winfo_exists():
            return

        for b in bubbles:
            b["y"] -= b["speed"]
            if b["y"] < -5:
                b["y"] = HEIGHT + random.randint(0, 20)
                b["x"] = random.randint(10, WIDTH - 10)

        for fish in fish_sprites:
            target = closest_food(fish)

            if target is not None:
                dx = target["x"] - fish["x"]
                dy = target["y"] - fish["y"]
                dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
                speed = 1.2
                fish["dx"] = speed * dx / dist
                fish["dy"] = speed * dy / dist

                if dist < 12:
                    if target in food_list:
                        food_list.remove(target)
                    activate_fish_boost()
                    # Увеличиваем счётчик съеденных кормов
                    fish_food_eaten += 1
                    # Каждые 5 съеденных кормов даём 5 спец. валюты
                    if fish_food_eaten % 5 == 0:
                        add_special_currency(5)
            else:
                if random.random() < 0.02:
                    fish["dx"] = random.choice([-0.6, -0.4, 0.4, 0.6])
                if random.random() < 0.02:
                    fish["dy"] = random.choice([-0.15, 0.15])

            fish["x"] += fish["dx"]
            fish["y"] += fish["dy"]

            if fish["x"] < 20 or fish["x"] > WIDTH - 20:
                fish["dx"] *= -1
                fish["x"] = max(20, min(WIDTH - 20, fish["x"]))
            if fish["y"] < 25 or fish["y"] > HEIGHT - SAND_HEIGHT - 10:
                fish["dy"] *= -1
                fish["y"] = max(25, min(HEIGHT - SAND_HEIGHT - 10, fish["y"]))

        draw_scene()
        aquarium.after(50, update_aquarium)

    update_aquarium()

# ---------- Построение основного интерфейса ----------
PADDING_X = 20

label = ctk.CTkLabel(sidebar, text="Счетчик: 0", font=("Arial", 16, "bold"))
label.place(x=PADDING_X, y=20)

power_label = ctk.CTkLabel(sidebar, text="Сила клика: 1", font=("Arial", 12))
power_label.place(x=PADDING_X, y=55)

auto_power_label = ctk.CTkLabel(sidebar, text="Доход автокликера: 1/сек", font=("Arial", 12))
auto_power_label.place(x=PADDING_X, y=80)

fish_income_label = ctk.CTkLabel(sidebar, text="Доход рыбок: 0/сек", font=("Arial", 12))
fish_income_label.place(x=PADDING_X, y=105)

special_label = ctk.CTkLabel(sidebar, text="Спец. валюта: 0", font=("Arial", 12))
special_label.place(x=PADDING_X, y=130)

btn = ctk.CTkButton(sidebar, text="Кнопочка", command=click, width=260)
btn.place(x=PADDING_X, y=170)

buy_button = ctk.CTkButton(sidebar, text="Включить автокликер?", command=buy_auto, width=260)
buy_button.place(x=PADDING_X, y=215)

upgrade_button = ctk.CTkButton(sidebar, text=f"Сила клика +1 (цена: {upgrade_cost})", command=buy_upgrade, width=260)
upgrade_button.place(x=PADDING_X, y=260)

auto_upgrade_button = ctk.CTkButton(sidebar, text=f"Автодоход +1 (цена: {auto_upgrade_cost})", command=buy_auto_upgrade, width=260)
auto_upgrade_button.place(x=PADDING_X, y=305)

multiplier_button = ctk.CTkButton(sidebar, text=f"Множитель x{click_multiplier} (цена: {multiplier_cost})", command=buy_multiplier, width=260)
multiplier_button.place(x=PADDING_X, y=350)

selector_button = ctk.CTkButton(sidebar, text="Выбрать фон", command=open_bg_selector, width=260)
selector_button.place(x=PADDING_X, y=395)

menu_button = ctk.CTkButton(sidebar, text="Меню", command=open_menu, width=260)
menu_button.place(x=PADDING_X, y=440)

# ---------- Загрузка сохранения и обновление UI ----------
load_game()

# Обновляем все элементы интерфейса после загрузки
label.configure(text=f"Счетчик: {count}")
power_label.configure(text=f"Сила клика: {click_power}")
auto_power_label.configure(text=f"Доход автокликера: {auto_power}/сек")
special_label.configure(text=f"Спец. валюта: {special_currency}")
upgrade_button.configure(text=f"Сила клика +1 (цена: {upgrade_cost})")
auto_upgrade_button.configure(text=f"Автодоход +1 (цена: {auto_upgrade_cost})")
multiplier_button.configure(text=f"Множитель x{click_multiplier} (цена: {multiplier_cost})")
if passive_started:
    buy_button.configure(text="Автокликер включен!")
else:
    buy_button.configure(text="Включить автокликер?")
update_fish_income_label()
update_background()

# Если автокликер был включен, запускаем пассивный доход
if passive_started:
    passive_income()

# Запускаем цикл дохода от рыбок
fish_income_tick()

# Автосохранение каждые 30 секунд
root.after(30000, auto_save)

# Сохранение при закрытии
root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()