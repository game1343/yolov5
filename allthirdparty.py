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
model = torch.hub.load('ultralytics/yolov5', 'custom', path='runs/train/procopper2/weights/best.pt')
print(model.names)

# กำหนดชื่อหน้าต่างเกม
window_title = "FiveM® by Cfx.re - WHAT UNIVERSAL Sponsored by [ HOSTIFY ]"

# ตำแหน่งกรอบตรวจจับภายในหน้าต่างเกม
x_min, y_min = 1550, 960
x_max, y_max = 1900, 1070

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
            print(f"✅ เลือกไอเทม: {item_name}")
        else:
            print("❌ ไม่ได้เลือกไอเทม")
        root.destroy()

    items = ["Gold", "Copper", "Iron", "scrapGold", "scrapCopper", "scrapIron"]

    root = tk.Tk()
    root.title("เลือกไอเทมที่ต้องการโพ")
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

# ใช้ filename ใน locateOnScreen()

keyboard.add_hotkey('f5', lambda: start_scanning())
keyboard.add_hotkey('f6', lambda: stop_scanning())
keyboard.add_hotkey('f10', choose_and_update_item)

scanning = False

choose_items()

with mss.mss() as sct:
    while True:
        try:
            if keyboard.is_pressed('f5'):
                start_scanning()
                time.sleep(0.3)  # กันกดซ้ำ
            if keyboard.is_pressed('f6'):
                stop_scanning()
                time.sleep(0.3)
            if keyboard.is_pressed('f10'):
                choose_and_update_item()
                time.sleep(0.3)
            if not scanning:
                time.sleep(0.1)
                continue
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd == 0:
                print("ไม่พบหน้าต่างเกม")
                time.sleep(1)
                continue

            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            window_img = np.array(sct.grab({
                "left": left,
                "top": top,
                "width": right - left,
                "height": bottom - top
            }))
            frame = cv2.cvtColor(window_img, cv2.COLOR_BGRA2BGR)

            # ตัดเฉพาะบริเวณกรอบภายในหน้าต่างเกม
            cropped = frame[y_min:y_max, x_min:x_max]

            # ตรวจ YOLO
            results = model(cropped[:, :, ::-1])
            detections = results.xyxy[0].cpu().numpy()

            if len(detections) == 0 and yolo_detected:
                # pyautogui.screenshot('zone_debug.png', region=(349, 307, 500, 450))
                tap_key(H)
                time.sleep(0.1)  # รอ 3 วิ เตรียมหน้าต่างเกม
                pydirectinput.moveTo(589, 474)
                pydirectinput.click()
                pydirectinput.click()
                time.sleep(3)
                # print(carname)
                location = pyautogui.locateOnScreen(carname, confidence=0.8, region=(808, 310, 800, 550))
                center = pyautogui.center(location)
                pyautogui.moveTo(center.x, center.y)
                pydirectinput.mouseDown()
                time.sleep(0.2)
                pydirectinput.moveTo(561, 574)
                pydirectinput.mouseUp()
                time.sleep(0.1)
                pydirectinput.moveTo(1032, 594)
                pydirectinput.click()
                time.sleep(0.1)
                pydirectinput.moveTo(952, 646)
                pydirectinput.click()
                time.sleep(1)
                # print(selfname)
                location = pyautogui.locateOnScreen(selfname, confidence=0.8, region=(349, 307, 500, 450))
                center = pyautogui.center(location)
                pyautogui.moveTo(center.x, center.y)
                pydirectinput.mouseDown()
                time.sleep(0.2)
                pydirectinput.moveTo(1179, 571)
                pydirectinput.mouseUp()
                time.sleep(0.1)
                pydirectinput.moveTo(1148, 553)
                pydirectinput.mouseUp()
                pydirectinput.moveTo(1032, 594)
                pydirectinput.click()
                pydirectinput.moveTo(952, 646)
                pydirectinput.click()
                pydirectinput.press('esc')
                time.sleep(0.1)
                pydirectinput.press('e')
                time.sleep(1)
                pydirectinput.moveTo(899, 639)
                pydirectinput.click()
                time.sleep(0.5)
                pydirectinput.press('enter')
                yolo_detected = False
            elif len(detections) > 0:
                yolo_detected = True
            

        except Exception as e:
            print("Error:", e)
            time.sleep(1)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
