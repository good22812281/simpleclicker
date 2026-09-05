import tkinter as tk

root = tk.Tk()
root.title("Кликер")
root.geometry("1280x720")

# Чтобы добавить новый фон — просто добавьте новую строку сюда:
BACKGROUNDS = [
    {"threshold": 50, "file": "25.png", "name": "чирно"},
    {"threshold": 500, "file": "50.png", "name": "хонг-мейлинг"},
    {"threshold": 1000, "file": "100.png", "name": "пачули"},
    {"threshold": 2000, "file": "2000.png", "name": "рейму"},
    {"threshold": 6000, "file": "6000.png", "name": "мариса"},
    {"threshold": 10000, "file": "10000.png", "name": "коиси"},
]

for bg in BACKGROUNDS:
    bg["image"] = tk.PhotoImage(file=bg["file"])

unlocked = set()

count = 0
passive_started = False
click_power = 1000
upgrade_cost = 50
click_multiplier = 1
multiplier_cost = 1000
auto_power = 1
auto_upgrade_cost = 100
manual_bg_selected = False

background_label = tk.Label(root)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
background_label.lower()

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
        background_label.config(image=current)

def click():
    global count
    count += click_power * click_multiplier
    label.config(text=f"Счетчик: {count}")
    update_background()

def passive_income():
    global count
    count += auto_power
    label.config(text=f"Счетчик: {count}")
    update_background()
    root.after(1000, passive_income)

def buy_auto():
    global passive_started
    if count >= 100:
        if not passive_started:
            passive_started = True
            passive_income()
            buy_button.config(text="Автокликер куплен!")
    else:
        buy_button.config(text="Не хватает очков, нужно 100")

def buy_upgrade():
    global count, click_power, upgrade_cost
    if count >= upgrade_cost:
        count -= upgrade_cost
        click_power += 1
        upgrade_cost = int(upgrade_cost * 2.25)
        label.config(text=f"Счетчик: {count}")
        upgrade_button.config(text=f"Сила клика +1 (цена: {upgrade_cost})")
        power_label.config(text=f"Сила клика: {click_power}")
        update_background()
    else:
        upgrade_button.config(text=f"Не хватает очков (нужно {upgrade_cost})")

def buy_multiplier():
    global count, click_multiplier, multiplier_cost
    if count >= multiplier_cost:
        count -= multiplier_cost
        click_multiplier += 1
        multiplier_cost = int(multiplier_cost * 2.5)
        label.config(text=f"Счетчик: {count}")
        multiplier_button.config(text=f"Множитель x{click_multiplier} (цена: {multiplier_cost})")
        update_background()
    else:
        multiplier_button.config(text=f"Не хватает очков (нужно {multiplier_cost})")

def buy_auto_upgrade():
    global count, auto_power, auto_upgrade_cost
    if not passive_started:
        auto_upgrade_button.config(text="Сначала купите автокликер")
        return

    if count >= auto_upgrade_cost:
        count -= auto_upgrade_cost
        auto_power += 1
        auto_upgrade_cost = int(auto_upgrade_cost * 2.5)
        label.config(text=f"Счетчик: {count}")
        auto_upgrade_button.config(text=f"Автодоход +1 (цена: {auto_upgrade_cost})")
        auto_power_label.config(text=f"Доход автокликера: {auto_power}/сек")
        update_background()
    else:
        auto_upgrade_button.config(text=f"Не хватает очков (нужно {auto_upgrade_cost})")

def open_bg_selector():
    selector = tk.Toplevel(root)
    selector.title("Выбор фона")
    selector.geometry("1000x150")

    def choose(img):
        global manual_bg_selected
        manual_bg_selected = True
        background_label.config(image=img)

    def reset_auto():
        global manual_bg_selected
        manual_bg_selected = False
        update_background()

    for bg in BACKGROUNDS:
        if bg["threshold"] in unlocked:
            tk.Button(
                selector,
                text=bg["name"],
                command=lambda img=bg["image"]: choose(img)
            ).pack(side="left", padx=10, pady=20)
        else:
            tk.Button(
                selector,
                text=f"??? (нужно {bg['threshold']})",
                state="disabled"
            ).pack(side="left", padx=10, pady=20)

    tk.Button(selector, text="Авто (по очкам)", command=reset_auto).pack(side="left", padx=10, pady=20)

LEFT_MARGIN = 20

label = tk.Label(root, text="Счетчик: 0", font=("Arial", 14), bg="white")
label.place(x=LEFT_MARGIN, y=20)

power_label = tk.Label(root, text="Сила клика: 1", font=("Arial", 12), bg="white")
power_label.place(x=LEFT_MARGIN, y=50)

auto_power_label = tk.Label(root, text="Доход автокликера: 1/сек", font=("Arial", 12), bg="white")
auto_power_label.place(x=LEFT_MARGIN, y=75)

btn = tk.Button(root, text="кнопочка", command=click)
btn.place(x=LEFT_MARGIN, y=110)

buy_button = tk.Button(root, text="купить автокликер?", command=buy_auto)
buy_button.place(x=LEFT_MARGIN, y=150)

upgrade_button = tk.Button(root, text=f"Сила клика +1 (цена: {upgrade_cost})", command=buy_upgrade)
upgrade_button.place(x=LEFT_MARGIN, y=190)

auto_upgrade_button = tk.Button(root, text=f"Автодоход +1 (цена: {auto_upgrade_cost})", command=buy_auto_upgrade)
auto_upgrade_button.place(x=LEFT_MARGIN, y=230)

multiplier_button = tk.Button(root, text=f"Множитель x{click_multiplier} (цена: {multiplier_cost})", command=buy_multiplier)
multiplier_button.place(x=LEFT_MARGIN, y=270)

selector_button = tk.Button(root, text="Выбрать фон", command=open_bg_selector)
selector_button.place(x=LEFT_MARGIN, y=310)

root.mainloop()