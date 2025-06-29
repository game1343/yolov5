import cv2
import torch
import numpy as np
import pygetwindow as gw
import mss
import time
import ctypes
import win32gui
import win32con
from ctypes import wintypes
import keyboard
import threading
import pydirectinput
import pyautogui


try:
    window = gw.getWindowsWithTitle("FiveM")[0]
    hwnd = window._hWnd
    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    win32gui.SetForegroundWindow(hwnd)
    print("✔ FiveM ถูกดึงมาอยู่หน้าสุดแล้ว")
    time.sleep(1)
except IndexError:
    print("❌ ไม่พบหน้าต่างชื่อ 'FiveM' กรุณาเปิดเกมก่อน")
    exit()
except Exception as e:
    print("❌ ไม่สามารถตั้งหน้าต่างเป็นหน้าสุดได้:", e)


# --- โค้ดส่งคีย์ (ใช้ scan code) ---
SendInput = ctypes.windll.user32.SendInput
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

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    _anonymous_ = ("u",)
    _fields_ = [("type", ctypes.c_ulong),
                ("u", _INPUT)]

def move_mouse_relative(dx, dy):
    MOUSEEVENTF_MOVE = 0x0001
    inp = INPUT()
    inp.type = 0  # INPUT_MOUSE
    inp.mi = MOUSEINPUT(dx, dy, 0, MOUSEEVENTF_MOVE, 0, None)
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
    

# Scan codes ของปุ่มที่ใช้
W = 0x11
A = 0x1E
S = 0x1F
D = 0x20
SHIFT = 0x2A
E = 0x12
C = 0x2E

def listen_keys():
    global is_running
    while True:
        if keyboard.is_pressed('f5'):
            is_running = True
            print("✅ Start")
            time.sleep(0.3)  # กันกดรัว

        if keyboard.is_pressed('f6'):
            print("🛑 Stop")
            ReleaseKey(W)
            ReleaseKey(A)
            ReleaseKey(D)
            ReleaseKey(SHIFT)
            time.sleep(0.3)
            ReleaseKey(W)
            ReleaseKey(A)
            ReleaseKey(D)
            ReleaseKey(SHIFT)
            is_running = False

threading.Thread(target=listen_keys, daemon=True).start()
key_thread = threading.Thread(target=listen_keys, daemon=True)
key_thread.start()

def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

keys_pressed = set()

def press_keys(new_keys):
    global keys_pressed
    new_keys = set(new_keys)

    # ปล่อยปุ่มที่ไม่ได้ใช้อีกแล้ว
    for key in keys_pressed - new_keys:
        ReleaseKey(key)

    # กดเฉพาะปุ่มที่ยังไม่กด
    for key in new_keys - keys_pressed:
        PressKey(key)

    keys_pressed = new_keys

# --- โหลดโมเดล YOLO ---
model = torch.hub.load('ultralytics/yolov5', 'custom', path='runs/train/rock-detect2/weights/best.pt')
modelx = torch.hub.load('ultralytics/yolov5', 'custom', path='runs/train/full_alert_model5/weights/best.pt')

def set_always_on_top(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

# window_title = "FiveM® by Cfx.re - WHAT CITY 3.0 Sponsored by [ HOSTIFY ]"
window_title = "FiveM® by Cfx.re - WHAT UNIVERSAL Sponsored by [ HOSTIFY ]"


# cv2.namedWindow("Rock Detector", cv2.WINDOW_NORMAL)
# cv2.resizeWindow("Rock Detector", 320, 240)
# cv2.setWindowProperty("Rock Detector", cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)

def press_key_e():
    PressKey(E)
    time.sleep(0.1)
    ReleaseKey(E)



def get_game_screen():
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        print("ไม่พบหน้าต่างเกม")
        return None, None
    window = windows[0]
    left, top = window.left, window.top
    width, height = window.width, window.height

    # กำหนดให้ตัดด้านบน 20% ของภาพ
    crop_top_percent = 0.25
    crop_top = int(height * crop_top_percent)
    cropped_height = height - crop_top

    with mss.mss() as sct:
        monitor = {"top": top + crop_top, "left": left, "width": width, "height": cropped_height}
        sct_img = sct.grab(monitor)
        frame = np.array(sct_img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        return frame, (left, top + crop_top, width, cropped_height)


lock_duration = 10.0
last_lock_time = None
locked_rock = None
is_running = False

def keep_pressing_e():
    global is_running
    while True:
        if is_running:
            press_key_e()
            time.sleep(0.1)  # กด E ทุก 1 วินาที (ปรับได้)
        else:
            time.sleep(0.1)

e_thread = threading.Thread(target=keep_pressing_e, daemon=True)
e_thread.start()

def choose_item():
    choices = ["Gold", "Copper", "Iron"]
    print("เลือกไอเทมที่ต้องการ: Gold / Copper / Iron")
    choice = input("พิมพ์ชื่อไอเทม: ").strip()
    if choice in choices:
        return choice
    else:
        print("❌ เลือกไม่ถูกต้อง หรือไม่มีในรายการ")
        return None


# ตัวอย่างเรียกใช้งาน
item = choose_item()

if item is None:
    print("❌ หยุดการทำงานเนื่องจากไม่ได้เลือกไอเทมที่ถูกต้อง")
    exit()
item_name = item  # หรือ "Copper" หรือ "Iron"

# สร้างชื่อไฟล์ภาพแบบไดนามิก
selfname = f"scrap{item_name}.png"
print(selfname)

def choose_and_update_item():
    global item_name, selfname
    item = choose_item()
    if item:
        item_name = item
        selfname = f"scrap{item_name}.png"
        print(f"✅ เปลี่ยนไอเทมเป็น: {selfname}")
    else:
        print("❌ ไม่ได้เปลี่ยนไอเทม")

keyboard.add_hotkey('f10', choose_and_update_item)

x_min, y_min = 10, 680 
x_max, y_max = 300, 750

while True:
    if not is_running:
        time.sleep(0.1)
        continue
# แสดงผลภาพ
    frame, region = get_game_screen()
    if frame is None:
        print("can't find screen")
        time.sleep(1)
        continue
    alert_crop = frame[y_min:y_max, x_min:x_max]  # พื้นที่เฉพาะที่ UI เตือนจะอยู่
    resultModelx = modelx(alert_crop[:, :, ::-1])
    alert_detections  = resultModelx.xyxy[0]
    for *box, conf, cls_id in alert_detections :
        # if conf < 0.5:  
        #     continue
        x1, y1, x2, y2 = map(int, box)
        label = f"{modelx.names[int(cls_id)]} {conf:.2f}"
        # วาดกรอบ
        cv2.rectangle(alert_crop, (x1, y1), (x2, y2), (0, 0, 255), 2)
        # วาดข้อความ
        cv2.putText(alert_crop, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        # แสดงผลลัพธ์หลังวาด
    cv2.imshow("modelx", alert_crop)
    set_always_on_top("modelx")
    cv2.waitKey(1)

    alert_detected = any(conf > 0.3 for *_, conf, _ in alert_detections )

    if alert_detected:
        print("🔴 พบการแจ้งเตือนในหน้าจอ (modelx)")
        for *box, conf, cls in alert_detections :
            print(f"🟡 เจอ {modelx.names[int(cls)]} มั่นใจ {conf:.2f}")
        is_running = False
        ReleaseKey(W)
        ReleaseKey(A)
        ReleaseKey(D)
        ReleaseKey(SHIFT)
        time.sleep(0.5)
        ReleaseKey(W)
        ReleaseKey(A)
        ReleaseKey(D)
        ReleaseKey(SHIFT)
        time.sleep(1)
        pydirectinput.press('h')
        pydirectinput.moveTo(589, 474)
        pydirectinput.click()
        time.sleep(0.2)
        pydirectinput.click()
        time.sleep(0.2)
        pydirectinput.click()
        time.sleep(0.2)
        pydirectinput.click()
        time.sleep(4)
        try:
            location = pyautogui.locateOnScreen(selfname, confidence=0.8, region=(808, 310, 900, 600))
            if location is None:
                print(f"❌ ไม่พบภาพ {selfname} แม้จะลด confidence")
                # pyautogui.screenshot("debug_area.png", region=(808, 310, 900, 600))
                is_running = False
                continue
            center = pyautogui.center(location)
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด locateOnScreen: {e}")
            time.sleep(1)
            pydirectinput.press('f5')
            # pyautogui.screenshot("debug_error.png", region=(808, 310, 900, 600))
            continue
        pyautogui.moveTo(center.x, center.y)
        pydirectinput.mouseDown()
        time.sleep(0.2)
        pydirectinput.moveTo(561, 574)
        pydirectinput.mouseUp()
        time.sleep(0.2)
        pydirectinput.moveTo(1032, 594)
        pydirectinput.click()
        pydirectinput.moveTo(952, 646)
        pydirectinput.click()
        pydirectinput.press('esc')
        pydirectinput.press('f5')
        # pyautogui.screenshot('zone_debug.png', region=(808, 310, 900, 600))
        continue

    results = model(frame)
    rock_detections = results.xyxy[0]

    alert_detected = any(conf > 0.7 for *_, conf, _ in rock_detections)

    rocks = []
    center_x = frame.shape[1] // 2
    center_y = int(frame.shape[0] * 0.85)

    # คัดกรองเฉพาะวัตถุที่มั่นใจเกิน 0.6 แล้วเก็บข้อมูล
    for *box, conf, cls in rock_detections:
        # if conf < 0.6:
        #     continue
        x1, y1, x2, y2 = map(int, box)
        mid_x = (x1 + x2) // 2
        mid_y = (y1 + y2) // 2
        dist = ((mid_x - center_x)**2 + (mid_y - center_y)**2) ** 0.5
        rocks.append((x1, y1, x2, y2, conf, int(cls), dist, mid_x, mid_y))

    # เลือกหินที่ใกล้จุดกลางจอที่สุด
    locked_rock = min(rocks, key=lambda r: r[6]) if rocks else None

    # วาดกรอบ ตรวจจับ และเส้นลาก
    for (x1, y1, x2, y2, conf, cls_id, dist, mid_x, mid_y) in rocks:
        color = (0, 255, 0) if locked_rock and (x1, y1, x2, y2) == locked_rock[:4] else (255, 0, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label = f"Rock {conf:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.line(frame, (center_x, center_y), (mid_x, mid_y), (0, 255, 255), 1)

    # จุดกึ่งกลางจอ
    cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

    # จุดและเส้นหนาไปยังหินที่ล็อก
    # if locked_rock:
    #     _, _, _, _, _, _, _, mid_x, mid_y = locked_rock
    #     cv2.circle(frame, (mid_x, mid_y), 7, (0, 255, 255), -1)
    #     cv2.line(frame, (center_x, center_y), (mid_x, mid_y), (0, 255, 255), 3)

    # # ระบบควบคุมทิศทางเคลื่อนไปหาหิน
    # ReleaseKey(W)
    # ReleaseKey(A)
    # ReleaseKey(D)
    # ReleaseKey(SHIFT)

    # if locked_rock:
    #     _, _, _, _, _, _, _, mid_x, mid_y = locked_rock
    #     offset_x = mid_x - center_x

    #     if offset_x > 230:
    #         PressKey(D)
    #         PressKey(W)
    #         PressKey(SHIFT)
    #     elif offset_x < -230:
    #         PressKey(A)
    #         PressKey(W)
    #         PressKey(SHIFT)
    #     else:
    #         PressKey(W)
    #         PressKey(SHIFT)
    # else:
    #     move_mouse_relative(2000, 0)

    if locked_rock:
        _, _, _, _, _, _, _, mid_x, mid_y = locked_rock
        offset_x = mid_x - center_x

        # ปล่อยทุกปุ่มก่อนเพื่อกันค้าง
        ReleaseKey(W)
        ReleaseKey(A)
        ReleaseKey(D)
        ReleaseKey(SHIFT)

        # ระยะไกลมาก – หันตัวก่อน
        if offset_x > 400:
            PressKey(D)
            PressKey(SHIFT)
        elif offset_x < -400:
            PressKey(A)
            PressKey(SHIFT)

        # ระยะกลาง – เดินเฉียงเข้าไป
        elif offset_x > 230:
            PressKey(W)
            PressKey(D)
            PressKey(SHIFT)
        elif offset_x < -230:
            PressKey(W)
            PressKey(A)
            PressKey(SHIFT)

        # ใกล้ – เดินตรงเข้าไป
        else:
            PressKey(W)
            PressKey(SHIFT)
    else:
        ReleaseKey(W)
        ReleaseKey(A)
        ReleaseKey(D)
        ReleaseKey(SHIFT)
        move_mouse_relative(2000, 0)
        time.sleep(1)
        PressKey(S)
        PressKey(D)
        PressKey(SHIFT)
        time.sleep(1.5)


    # small_frame = cv2.resize(frame, (320, 240))
    # cv2.imshow("Rock Detector", small_frame)
    # set_always_on_top("Rock Detector")
