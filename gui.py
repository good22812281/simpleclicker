import tkinter as tk

root = tk.Tk()
root.title("Кнопка")
root.geometry("1280x720")

img_25 = tk.PhotoImage(file="25.png")
img_50 = tk.PhotoImage(file="50.png")

count = 0

background_label = tk.Label(root)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
background_label.lower()

def click():
    global count
    count += 1
    label.config(text=f"Счетчик: {count}")

    if count >= 100:
        background_label.config(image=img_100)
    elif count >= 50:
        background_label.config(image=img_50)
    elif count >= 25:
        background_label.config(image=img_25)

label = tk.Label(root, text="Счетчик: 0", font=("Arial", 14), bg="white")
label.pack(pady=10)

btn = tk.Button(root, text="кнопочка", command=click)
btn.pack(pady=20)

root.mainloop()