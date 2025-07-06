import torch
import cv2
import numpy as np
import mss
import pygetwindow as gw
import ctypes
import win32gui
import time
import pyautogui
import pydirectinput
import tkinter as tk
from tkinter import simpledialog
import keyboard

# โหลดโมเดล

# กำหนดชื่อหน้าต่างเกม
window_title = "FiveM® by Cfx.re - WHAT UNIVERSAL Sponsored by [ HOSTIFY ]"

# ตำแหน่งกรอบตรวจจับภายในหน้าต่างเกม

# กำหนดคีย์ H
H = 0x23

# ฟังก์ชันส่งคีย์
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

def press_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def release_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def tap_key(hexKeyCode):
    press_key(hexKeyCode)
    time.sleep(0.05)
    release_key(hexKeyCode)

def start_scanning(event=None):
    global scanning
    scanning = True
    print("✅ เริ่มการสแกน")

def stop_scanning(event=None):
    global scanning
    scanning = False
    print("🛑 หยุดการสแกน")

# ตัวแปรตรวจสอบ
yolo_detected = True

def choose_items():
    def on_submit():
        selected = [item for item, var in zip(items, vars) if var.get()]
        if selected:
            global item_name, carname, selfname
            item_name = selected[0]  # เลือกอันแรกเป็นหลัก
            carname = f"{item_name}.png"
            selfname = f"scrap{item_name}.png"
            print(f"✅ เลือกไอเทมที่่จะเอาเข้ารถ: {item_name}")
        else:
            print("❌ ไม่ได้เลือกไอเทม")
        root.destroy()

    items = ["Gold", "Copper", "Iron", "scrapGold", "scrapCopper", "scrapIron"]

    root = tk.Tk()
    root.title("เลือกไอเทมที่่จะเอาเข้ารถ")
    vars = []

    for item in items:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(root, text=item, variable=var)
        chk.pack(anchor='w')
        vars.append(var)

    submit_btn = tk.Button(root, text="ตกลง", command=on_submit)
    submit_btn.pack(pady=10)

    root.mainloop()

item_name = "Copper"
carname = f"{item_name}.png"
selfname = f"scrap{item_name}.png"

def choose_and_update_item():
    item = choose_items()
    if item:
        global item_name, carname
        item_name = item
        carname = f"{item_name}.png"
        print(f"✅ เปลี่ยนไอเทมเป็น: {item_name}")

keyboard.add_hotkey('alt + 7', lambda: start_scanning())
keyboard.add_hotkey('alt + 8', lambda: stop_scanning())
keyboard.add_hotkey('alt + 9', choose_and_update_item)

scanning = False

choose_items()

# ✅ แก้ indentation และเงื่อนไข scanning ให้ถูกต้อง
while True:
    try:
        if scanning:
            # pyautogui.screenshot('zone_debug.png', region=(349, 307, 500, 450))
            pydirectinput.keyDown('e')   # กดปุ่ม e ค้าง
            time.sleep(2)                # รอ 2 วินาที
            pydirectinput.keyUp('e')
            time.sleep(0.1)
            # pyautogui.screenshot('zone_debug.png', region=(969, 309, 800, 550))
            # pyautogui.screenshot('zone_debug1.png', region=(188, 308, 800, 550))
            # pyautogui.screenshot('zone_debug.png', region=(190, 309, 800, 550))
            location = pyautogui.locateOnScreen(carname, confidence=0.9, region=(190, 309, 800, 550))
            center = pyautogui.center(location)
            pyautogui.moveTo(center.x, center.y)
            pydirectinput.click()
            pydirectinput.click()
            time.sleep(0.1)
            pydirectinput.moveTo(1037, 596)
            time.sleep(0.1)
            pydirectinput.click()
            time.sleep(0.1)
            pydirectinput.moveTo(959, 643)
            time.sleep(0.1)
            pydirectinput.click()
            pydirectinput.press('esc')
            time.sleep(0.1)
            pydirectinput.press('h')
            time.sleep(0.1)
            pydirectinput.moveTo(588, 483)
            time.sleep(0.1)
            pydirectinput.click()
            pydirectinput.click()
            time.sleep(3)
            # pyautogui.screenshot('zone_debug1.png', region=(798, 300, 800, 550))
            location = pyautogui.locateOnScreen(carname, confidence=0.9, region=(798, 300, 800, 550))
            center = pyautogui.center(location)
            pyautogui.moveTo(center.x, center.y)
            time.sleep(0.1)
            pydirectinput.click()
            pydirectinput.click()
            time.sleep(0.1)
            pydirectinput.moveTo(1037, 596)
            time.sleep(0.1)
            pydirectinput.click()
            time.sleep(0.1)
            pydirectinput.moveTo(959, 643)
            time.sleep(0.1)
            pydirectinput.click()
            pydirectinput.press('esc')
            pass  
        else:
            time.sleep(0.1)
    except Exception as e:
        print("Error:", e)
        time.sleep(1)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
