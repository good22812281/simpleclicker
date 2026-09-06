import customtkinter as ctk
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
    count += auto_power
    label.configure(text=f"Счетчик: {count}")
    update_background()
    root.after(1000, passive_income)

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


PADDING_X = 20

label = ctk.CTkLabel(sidebar, text="Счетчик: 0", font=("Arial", 16, "bold"))
label.place(x=PADDING_X, y=20)

power_label = ctk.CTkLabel(sidebar, text="Сила клика: 1", font=("Arial", 12))
power_label.place(x=PADDING_X, y=55)

auto_power_label = ctk.CTkLabel(sidebar, text="Доход автокликера: 1/сек", font=("Arial", 12))
auto_power_label.place(x=PADDING_X, y=80)

btn = ctk.CTkButton(sidebar, text="Кнопочка", command=click, width=260)
btn.place(x=PADDING_X, y=120)

buy_button = ctk.CTkButton(sidebar, text="Включить автокликер?", command=buy_auto, width=260)
buy_button.place(x=PADDING_X, y=165)

upgrade_button = ctk.CTkButton(sidebar, text=f"Сила клика +1 (цена: {upgrade_cost})", command=buy_upgrade, width=260)
upgrade_button.place(x=PADDING_X, y=210)

auto_upgrade_button = ctk.CTkButton(sidebar, text=f"Автодоход +1 (цена: {auto_upgrade_cost})", command=buy_auto_upgrade, width=260)
auto_upgrade_button.place(x=PADDING_X, y=255)

multiplier_button = ctk.CTkButton(sidebar, text=f"Множитель x{click_multiplier} (цена: {multiplier_cost})", command=buy_multiplier, width=260)
multiplier_button.place(x=PADDING_X, y=300)

selector_button = ctk.CTkButton(sidebar, text="Выбрать фон", command=open_bg_selector, width=260)
selector_button.place(x=PADDING_X, y=345)

root.mainloop()
