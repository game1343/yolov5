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

def choose_item():
    root = tk.Tk()
    root.withdraw()  # ซ่อนหน้าต่างหลัก

    choices = ["Gold", "Copper", "Iron", "scrapGold", "scrapCopper", "scrapIron"]
    choice = simpledialog.askstring("เลือกไอเทม", f"พิมพ์ชื่อไอเทมที่ต้องการ:\nGold  Copper  Iron  scrapGold  scrapCopper  scrapIron")

    root.destroy()
    if choice and choice in choices:
        return choice
    else:
        print("เลือกไอเทมไม่ถูกต้อง หรือยกเลิก")
        return None

# 🔻 ลบการเรียก choose_item() ตรงนี้ออก
# item = choose_item()
# item_name = item

# ✅ ตั้งค่าเริ่มต้นไว้ก่อน
item_name = "Copper"
carname = f"{item_name}.png"
selfname = f"scrap{item_name}.png"

def choose_and_update_item():
    item = choose_item()
    if item:
        global item_name, carname
        item_name = item
        carname = f"{item_name}.png"
        print(f"✅ เปลี่ยนไอเทมเป็น: {item_name}")

# ใช้ filename ใน locateOnScreen()

# ... โค้ดเดิมทั้งหมดของคุณด้านบนไม่ต้องแก้ ...

keyboard.add_hotkey('/', lambda: start_scanning())
keyboard.add_hotkey('*', lambda: stop_scanning())
keyboard.add_hotkey('+', choose_and_update_item)

scanning = False

# ✅ แก้ indentation และเงื่อนไข scanning ให้ถูกต้อง
while True:
    try:
        if scanning:
            # pyautogui.screenshot('zone_debug.png', region=(349, 307, 500, 450))
            pydirectinput.keyDown('e')   # กดปุ่ม e ค้าง
            time.sleep(2)                # รอ 2 วินาที
            pydirectinput.keyUp('e')
            time.sleep(0.05)
            # pyautogui.screenshot('zone_debug.png', region=(969, 309, 800, 550))
            # pyautogui.screenshot('zone_debug1.png', region=(188, 308, 800, 550))
            location = pyautogui.locateOnScreen(carname, confidence=0.8, region=(969, 309, 800, 550))
            center = pyautogui.center(location)
            pyautogui.moveTo(center.x, center.y)
            pydirectinput.click()
            pydirectinput.click()
            time.sleep(0.05)
            pydirectinput.moveTo(1037, 596)
            time.sleep(0.05)
            pydirectinput.click()
            time.sleep(0.05)
            pydirectinput.moveTo(959, 643)
            time.sleep(0.05)
            pydirectinput.click()
            pydirectinput.press('esc')
            time.sleep(0.05)
            pydirectinput.press('h')
            time.sleep(0.05)
            pydirectinput.moveTo(588, 483)
            time.sleep(0.05)
            pydirectinput.click()
            pydirectinput.click()
            time.sleep(3)
            location = pyautogui.locateOnScreen(carname, confidence=0.8, region=(349, 307, 500, 450))
            center = pyautogui.center(location)
            pyautogui.moveTo(center.x, center.y)
            time.sleep(0.05)
            pydirectinput.click()
            pydirectinput.click()
            time.sleep(0.05)
            pydirectinput.moveTo(1037, 596)
            time.sleep(0.05)
            pydirectinput.click()
            time.sleep(0.05)
            pydirectinput.moveTo(959, 643)
            time.sleep(0.05)
            pydirectinput.click()
            pydirectinput.press('esc')
            # time.sleep(0.1)
                
            # pydirectinput.click()
            # pydirectinput.click()
            # time.sleep(3)

            # location = pyautogui.locateOnScreen(carname, confidence=0.8, region=(808, 310, 800, 500))
            # if location:
            #     center = pyautogui.center(location)
            #     pyautogui.moveTo(center.x, center.y)
            #     pydirectinput.mouseDown()
            #     time.sleep(0.2)
            #     pydirectinput.moveTo(561, 574)
            #     pydirectinput.mouseUp()
            #     time.sleep(0.05)
            #     pydirectinput.moveTo(1032, 594)
            #     pydirectinput.click()
            #     time.sleep(0.05)
            #     pydirectinput.moveTo(952, 646)
            #     pydirectinput.click()
            #     time.sleep(0.05)

            # location = pyautogui.locateOnScreen(selfname, confidence=0.8, region=(349, 307, 500, 450))
            # if location:
            #     center = pyautogui.center(location)
            #     pyautogui.moveTo(center.x, center.y)
            #     pydirectinput.mouseDown()
            #     time.sleep(0.2)
            #     pydirectinput.moveTo(1179, 571)
            #     pydirectinput.mouseUp()
            #     time.sleep(0.1)
            #     pydirectinput.moveTo(1148, 553)
            #     pydirectinput.mouseUp()
            #     pydirectinput.moveTo(1032, 594)
            #     pydirectinput.click()
            #     pydirectinput.moveTo(952, 646)
            #     pydirectinput.click()
            #     pydirectinput.press('esc')
            #     time.sleep(0.05)
            #     pydirectinput.press('e')
            #     time.sleep(1)
            #     pydirectinput.moveTo(899, 639)
            #     pydirectinput.click()
            #     time.sleep(0.5)
            #     pydirectinput.press('enter')

    except Exception as e:
        print("Error:", e)
        time.sleep(1)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
