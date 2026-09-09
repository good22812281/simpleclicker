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

# ---------- Казино  ----------
TOWER_TILES_PER_FLOOR = 3      # кирпичей на этаже (1 из них — ловушка)
TOWER_TOTAL_FLOORS = 8         # сколько этажей нужно пройти для полной победы
TOWER_FLOOR_MULTIPLIER = 1.45  # во сколько раз растёт множитель за пройденный этаж

# ---------- Квесты и статистика для них ----------
total_clicks = 0
total_earned = 0             # сколько очков всего заработано за игру
total_special_earned = 0     # сколько спец. валюты всего заработано за игру
upgrades_bought = 0
auto_upgrades_bought = 0
multiplier_bought = 0
fish_bought_count = 0
tower_games_played = 0
tower_wins = 0
max_tower_floor = 0
quests_completed = set()

QUESTS = [
    {"id": "clicks_100", "desc": "Сделай 100 кликов", "target": 100,
     "progress": lambda: total_clicks, "reward": 10},
    {"id": "earn_1000", "desc": "Заработай суммарно 1000 очков", "target": 1000,
     "progress": lambda: total_earned, "reward": 20},
    {"id": "power_5", "desc": "Купи 5 улучшений силы клика", "target": 5,
     "progress": lambda: upgrades_bought, "reward": 15},
    {"id": "auto_click", "desc": "Включи автокликер", "target": 1,
     "progress": lambda: 1 if passive_started else 0, "reward": 10},
    {"id": "fish_3", "desc": "Купи 3 рыбки в аквариум", "target": 3,
     "progress": lambda: fish_bought_count, "reward": 25},
    {"id": "tower_floor5", "desc": "Поднимись на 5 этаж в Башне", "target": 5,
     "progress": lambda: max_tower_floor, "reward": 30},
    {"id": "tower_win_3", "desc": "Забери выигрыш из Башни 3 раза", "target": 3,
     "progress": lambda: tower_wins, "reward": 40},
    {"id": "special_50", "desc": "Заработай суммарно 50 спец. валюты", "target": 50,
     "progress": lambda: total_special_earned, "reward": 20},
]

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
        "total_clicks": total_clicks,
        "total_earned": total_earned,
        "total_special_earned": total_special_earned,
        "upgrades_bought": upgrades_bought,
        "auto_upgrades_bought": auto_upgrades_bought,
        "multiplier_bought": multiplier_bought,
        "fish_bought_count": fish_bought_count,
        "tower_games_played": tower_games_played,
        "tower_wins": tower_wins,
        "max_tower_floor": max_tower_floor,
        "quests_completed": sorted(list(quests_completed)),
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
    global total_clicks, total_earned, total_special_earned
    global upgrades_bought, auto_upgrades_bought, multiplier_bought, fish_bought_count
    global tower_games_played, tower_wins, max_tower_floor, quests_completed

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
        total_clicks = data.get("total_clicks", 0)
        total_earned = data.get("total_earned", 0)
        total_special_earned = data.get("total_special_earned", 0)
        upgrades_bought = data.get("upgrades_bought", 0)
        auto_upgrades_bought = data.get("auto_upgrades_bought", 0)
        multiplier_bought = data.get("multiplier_bought", 0)
        fish_bought_count = data.get("fish_bought_count", 0)
        tower_games_played = data.get("tower_games_played", 0)
        tower_wins = data.get("tower_wins", 0)
        max_tower_floor = data.get("max_tower_floor", 0)
        quests_completed = set(data.get("quests_completed", []))
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

def gain_count(amount):
    """Изменяет счётчик очков и учитывает статистику для квестов."""
    global count, total_earned
    if amount > 0:
        total_earned += amount
    count += amount
    label.configure(text=f"Счетчик: {count}")
    update_background()

def gain_special(amount):
    """Изменяет спец. валюту и учитывает статистику для квестов."""
    global special_currency, total_special_earned
    if amount > 0:
        total_special_earned += amount
    special_currency += amount
    special_label.configure(text=f"Спец. валюта: {special_currency}")

def click():
    global total_clicks
    total_clicks += 1
    gain_count(click_power * click_multiplier)

def passive_income():
    gain_count(auto_power * auto_multiplier)
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
    global count, click_power, upgrade_cost, upgrades_bought
    if count >= upgrade_cost:
        count -= upgrade_cost
        click_power += 1
        upgrades_bought += 1
        upgrade_cost = int(upgrade_cost * 2.25)
        label.configure(text=f"Счетчик: {count}")
        upgrade_button.configure(text=f"Сила клика +1 (цена: {upgrade_cost})")
        power_label.configure(text=f"Сила клика: {click_power}")
        update_background()
    else:
        upgrade_button.configure(text=f"Не хватает очков (нужно {upgrade_cost})")

def buy_multiplier():
    global count, click_multiplier, multiplier_cost, multiplier_bought
    if count >= multiplier_cost:
        count -= multiplier_cost
        click_multiplier += 1
        multiplier_bought += 1
        multiplier_cost = int(multiplier_cost * 2.5)
        label.configure(text=f"Счетчик: {count}")
        multiplier_button.configure(text=f"Множитель x{click_multiplier} (цена: {multiplier_cost})")
        update_background()
    else:
        multiplier_button.configure(text=f"Не хватает очков (нужно {multiplier_cost})")

def buy_auto_upgrade():
    global count, auto_power, auto_upgrade_cost, auto_upgrades_bought
    if not passive_started:
        auto_upgrade_button.configure(text="Сначала купите автокликер")
        return

    if count >= auto_upgrade_cost:
        count -= auto_upgrade_cost
        auto_power += 1
        auto_upgrades_bought += 1
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
    gain_special(amount)

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
    global special_currency, fish_bought_count
    if special_currency >= FISH_PACK_COST:
        special_currency -= FISH_PACK_COST
        new_fish = get_random_fish()
        owned_fish.append(new_fish)
        fish_bought_count += 1

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
    global fish_boost_seconds_left

    if owned_fish:
        base = total_fish_income()
        multiplier = 2 if fish_boost_seconds_left > 0 else 1
        gain_count(base * multiplier)

    if fish_boost_seconds_left > 0:
        fish_boost_seconds_left -= 1

    if fish_income_label is not None:
        update_fish_income_label()

    root.after(1000, fish_income_tick)

# ---------- Меню и окна ----------
def open_menu():
    menu = ctk.CTkToplevel(root)
    menu.title("Меню")
    menu.geometry("300x370")

    # Доступ к мини-играм только с 6000 очков
    if count >= 6000:
        minigames_btn = ctk.CTkButton(
            menu, text="Мини-игры", command=lambda: open_minigames(menu)
        )
    else:
        minigames_btn = ctk.CTkButton(
            menu, text=f"Мини-игры (нужно 6000)", state="disabled"
        )
    minigames_btn.pack(pady=10)

    aquarium_btn = ctk.CTkButton(
        menu, text="Аквариум", command=lambda: open_aquarium(menu)
    )
    aquarium_btn.pack(pady=10)

    casino_btn = ctk.CTkButton(
        menu, text="Казино", command=lambda: open_casino(menu)
    )
    casino_btn.pack(pady=10)

    quests_btn = ctk.CTkButton(
        menu, text="Квесты", command=lambda: open_quests(menu)
    )
    quests_btn.pack(pady=10)

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
        # Находим индекс первой рыбы с таким именем
        for i, fish in enumerate(owned_fish):
            if fish["name"] == fish_name:
                rarity = fish["rarity"]
                price = SELL_PRICES.get(rarity, 5)
                # Удаляем рыбу
                del owned_fish[i]
                # Начисляем валюту
                gain_special(price)
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

# ---------- Казино: Третий лишний ----------
def open_casino(parent):
    casino = ctk.CTkToplevel(parent)
    casino.title("Казино")
    casino.geometry("320x260")

    title = ctk.CTkLabel(casino, text="🎰 Казино", font=("Arial", 20, "bold"))
    title.pack(pady=20)

    tower_btn = ctk.CTkButton(
        casino, text="Третий лишний", command=lambda: open_tower(casino), width=220, height=40
    )
    tower_btn.pack(pady=10)

    warn_label = ctk.CTkLabel(
        casino,
        text="Рискуй с умом! При проигрыше ставка сгорает полностью.",
        font=("Arial", 10),
        wraplength=270,
        text_color="#cccccc",
    )
    warn_label.pack(pady=15)

def open_tower(parent):
    tower_win = ctk.CTkToplevel(parent)
    tower_win.title("Третий лишний")
    tower_win.geometry("440x620")

    state = {
        "active": False,
        "bet": 0,
        "currency": "count",   # "count" (очки) или "special" (спец. валюта)
        "floor": 0,
        "multiplier": 1.0,
    }

    header = ctk.CTkLabel(tower_win, text="третий лишний", font=("Arial", 20, "bold"))
    header.pack(pady=(15, 5))

    rules_label = ctk.CTkLabel(
        tower_win,
        text=(f"На каждом этаже {TOWER_TILES_PER_FLOOR} кирпича, один из них — ловушка.\n"
              f"Выбирай безопасный кирпич, чтобы подняться выше и увеличить множитель.\n"
              "В любой момент после первого этажа можно забрать выигрыш.\n"
              "Попал в ловушку — ставка сгорает полностью."),
        font=("Arial", 11), wraplength=400, justify="center"
    )
    rules_label.pack(pady=(0, 10))

    currency_var = tk.StringVar(value="count")

    currency_frame = ctk.CTkFrame(tower_win, fg_color="transparent")
    currency_frame.pack(pady=5)

    ctk.CTkLabel(currency_frame, text="Валюта ставки:").pack(side="left", padx=5)
    count_radio = ctk.CTkRadioButton(
        currency_frame, text="Очки", variable=currency_var, value="count"
    )
    count_radio.pack(side="left", padx=5)
    special_radio = ctk.CTkRadioButton(
        currency_frame, text="Спец. валюта", variable=currency_var, value="special"
    )
    special_radio.pack(side="left", padx=5)

    bet_frame = ctk.CTkFrame(tower_win, fg_color="transparent")
    bet_frame.pack(pady=5)
    ctk.CTkLabel(bet_frame, text="Ставка:").pack(side="left", padx=5)
    bet_entry = ctk.CTkEntry(bet_frame, width=100)
    bet_entry.pack(side="left", padx=5)
    bet_entry.insert(0, "10")

    status_label = ctk.CTkLabel(tower_win, text="Сделай ставку, чтобы начать", font=("Arial", 13, "bold"))
    status_label.pack(pady=10)

    floors_frame = ctk.CTkFrame(tower_win, fg_color="transparent")
    floors_frame.pack(pady=10)

    controls_frame = ctk.CTkFrame(tower_win, fg_color="transparent")
    controls_frame.pack(pady=10)

    def get_balance():
        return count if state["currency"] == "count" else special_currency

    def set_balance(new_value):
        if state["currency"] == "count":
            gain_count(new_value - count)
        else:
            gain_special(new_value - special_currency)

    def clear_floors():
        for w in floors_frame.winfo_children():
            w.destroy()

    def set_controls(start_visible, cashout_visible):
        for w in controls_frame.winfo_children():
            w.destroy()
        if start_visible:
            start_btn = ctk.CTkButton(controls_frame, text="Начать игру", command=start_game, width=200)
            start_btn.pack(pady=5)
        if cashout_visible:
            cashout_btn = ctk.CTkButton(
                controls_frame, text="Забрать выигрыш", command=cash_out,
                width=200, fg_color="#2e7d32", hover_color="#1b5e20"
            )
            cashout_btn.pack(pady=5)

    def start_game():
        global tower_games_played
        try:
            bet = int(float(bet_entry.get()))
        except ValueError:
            status_label.configure(text="Введи корректную сумму ставки")
            return

        state["currency"] = currency_var.get()
        balance = get_balance()

        if bet <= 0:
            status_label.configure(text="Ставка должна быть больше 0")
            return
        if bet > balance:
            status_label.configure(text="Недостаточно средств для такой ставки")
            return

        set_balance(balance - bet)
        state["active"] = True
        state["bet"] = bet
        state["floor"] = 0
        state["multiplier"] = 1.0
        tower_games_played += 1

        count_radio.configure(state="disabled")
        special_radio.configure(state="disabled")
        bet_entry.configure(state="disabled")

        status_label.configure(
            text=f"Ставка: {bet} | Множитель: x1.00 | Этаж: 0/{TOWER_TOTAL_FLOORS}"
        )
        set_controls(start_visible=False, cashout_visible=False)
        render_floor()

    def render_floor():
        global max_tower_floor
        clear_floors()

        if state["floor"] >= TOWER_TOTAL_FLOORS:
            finish_game(win=True, auto=True)
            return

        if state["floor"] > max_tower_floor:
            max_tower_floor = state["floor"]

        floor_label = ctk.CTkLabel(
            floors_frame,
            text=f"Этаж {state['floor'] + 1} из {TOWER_TOTAL_FLOORS} — выбери кирпич",
            font=("Arial", 12)
        )
        floor_label.pack(pady=5)

        tiles_row = ctk.CTkFrame(floors_frame, fg_color="transparent")
        tiles_row.pack(pady=5)

        bomb_idx = random.randrange(TOWER_TILES_PER_FLOOR)

        for i in range(TOWER_TILES_PER_FLOOR):
            btn = ctk.CTkButton(
                tiles_row, text="🧱", width=80, height=80, font=("Arial", 22),
                command=lambda i=i, b=bomb_idx: pick_tile(i, b)
            )
            btn.pack(side="left", padx=8)

        set_controls(start_visible=False, cashout_visible=state["floor"] > 0)

    def pick_tile(idx, bomb_idx):
        if not state["active"]:
            return

        if idx == bomb_idx:
            finish_game(win=False)
            return

        state["floor"] += 1
        state["multiplier"] *= TOWER_FLOOR_MULTIPLIER
        status_label.configure(
            text=(f"Ставка: {state['bet']} | Множитель: x{state['multiplier']:.2f} | "
                  f"Этаж: {state['floor']}/{TOWER_TOTAL_FLOORS}")
        )
        render_floor()

    def finish_game(win, auto=False):
        global tower_wins
        state["active"] = False
        clear_floors()

        if win:
            payout = int(state["bet"] * state["multiplier"])
            set_balance(get_balance() + payout)
            tower_wins += 1
            if auto:
                msg = f"🏆 Игра пройдена! Забрано {payout} (x{state['multiplier']:.2f})"
            else:
                msg = f"🎉 Ты забрал {payout}! (x{state['multiplier']:.2f})"
            status_label.configure(text=msg)
        else:
            status_label.configure(
                text=f"💥 Ловушка! Ставка {state['bet']} потеряна."
            )

        count_radio.configure(state="normal")
        special_radio.configure(state="normal")
        bet_entry.configure(state="normal")
        set_controls(start_visible=True, cashout_visible=False)

    def cash_out():
        if state["active"] and state["floor"] > 0:
            finish_game(win=True)

    set_controls(start_visible=True, cashout_visible=False)

# ---------- Квесты ----------
def open_quests(parent):
    quests_win = ctk.CTkToplevel(parent)
    quests_win.title("Квесты")
    quests_win.geometry("440x520")

    header = ctk.CTkLabel(quests_win, text="📜 Квесты", font=("Arial", 18, "bold"))
    header.pack(pady=10)

    scroll = ctk.CTkScrollableFrame(quests_win, width=400, height=420)
    scroll.pack(padx=10, pady=10, fill="both", expand=True)

    def claim(quest):
        quests_completed.add(quest["id"])
        gain_special(quest["reward"])
        refresh()

    def refresh():
        for w in scroll.winfo_children():
            w.destroy()

        for q in QUESTS:
            row = ctk.CTkFrame(scroll, fg_color="#2b2b2b", corner_radius=8)
            row.pack(fill="x", pady=5, padx=5)

            progress = min(q["progress"](), q["target"])
            desc_label = ctk.CTkLabel(
                row, text=q["desc"], font=("Arial", 12, "bold"), anchor="w", wraplength=320
            )
            desc_label.pack(anchor="w", padx=10, pady=(8, 0))

            info_label = ctk.CTkLabel(
                row,
                text=f"Прогресс: {progress}/{q['target']}  •  Награда: {q['reward']} спец. валюты",
                font=("Arial", 10), anchor="w"
            )
            info_label.pack(anchor="w", padx=10, pady=(0, 8))

            if q["id"] in quests_completed:
                ctk.CTkLabel(
                    row, text="✅ Выполнено", font=("Arial", 11, "bold"), text_color="#4CD964"
                ).pack(anchor="e", padx=10, pady=(0, 8))
            elif progress >= q["target"]:
                ctk.CTkButton(
                    row, text="Забрать награду", width=170,
                    command=lambda quest=q: claim(quest)
                ).pack(anchor="e", padx=10, pady=(0, 8))
            else:
                ctk.CTkLabel(
                    row, text="В процессе...", font=("Arial", 10), text_color="#888888"
                ).pack(anchor="e", padx=10, pady=(0, 8))

    refresh()

    refresh_btn = ctk.CTkButton(quests_win, text="Обновить", command=refresh, width=150)
    refresh_btn.pack(pady=5)

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