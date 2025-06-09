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
import pyautogui
import win32api
import keyboard
import threading

try:
    window = gw.getWindowsWithTitle("FiveM")[0]
    window.activate()
    print("✔ FiveM ถูกดึงมาอยู่หน้าสุดแล้ว")
    time.sleep(1)
except IndexError:
    print("❌ ไม่พบหน้าต่างชื่อ 'FiveM' กรุณาเปิดเกมก่อน")
    exit()

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

# --- โหลดโมเดล YOLO ---
model = torch.hub.load('ultralytics/yolov5', 'custom', path='runs/train/rock-detect2/weights/best.pt')

def set_always_on_top(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

# window_title = "FiveM® by Cfx.re - WHAT CITY 3.0 Sponsored by [ HOSTIFY ]"
window_title = "FiveM® by Cfx.re - WHAT UNIVERSAL Sponsored by [ HOSTIFY ]"


cv2.namedWindow("Rock Detector", cv2.WINDOW_NORMAL)

def press_key_e():
    PressKey(E)
    time.sleep(0.1)
    ReleaseKey(E)

# def get_game_screen():
#     windows = gw.getWindowsWithTitle(window_title)
#     if not windows:
#         print("ไม่พบหน้าต่างเกม")
#         return None, None
#     window = windows[0]
#     left, top = window.left, window.top
#     width, height = window.width, window.height
#     cropped_height = int(height * 0.8)
#     with mss.mss() as sct:
#         monitor = {"top": top, "left": left, "width": width, "height": height}
#         sct_img = sct.grab(monitor)
#         frame = np.array(sct_img)
#         frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
#         return frame, (left, top, width, height)

def get_game_screen():
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        print("ไม่พบหน้าต่างเกม")
        return None, None
    window = windows[0]
    left, top = window.left, window.top
    width, height = window.width, window.height

    # กำหนดให้ตัดด้านบน 20% ของภาพ
    crop_top_percent = 0.2
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

while True:
    if not is_running:
        time.sleep(0.1)
        continue

    frame, region = get_game_screen()
    if frame is None:
        time.sleep(1)
        continue

    results = model(frame)

    rocks = []
    center_x = frame.shape[1] // 2
    # center_y = frame.shape[0] // 2
    center_y = int(frame.shape[0] * 0.85)

    for *box, conf, cls in results.xyxy[0]:
        x1, y1, x2, y2 = map(int, box)
        mid_x = (x1 + x2) // 2
        mid_y = (y1 + y2) // 2
        dist = ((mid_x - center_x)**2 + (mid_y - center_y)**2) ** 0.5
        rocks.append((x1, y1, x2, y2, conf, int(cls), dist, mid_x, mid_y))

    current_time = time.time()

    if locked_rock:
        # ตรวจสอบว่าหินเดิมยังอยู่หรือไม่ (ในระยะ 30 พิกเซล)
        still_exists = False
        for rock in rocks:
            lx1, ly1, lx2, ly2, lconf, lcls, ldist, lmx, lmy = locked_rock
            x1, y1, x2, y2, conf, cls_id, dist, mid_x, mid_y = rock
            if cls_id == lcls and abs(mid_x - lmx) < 30 and abs(mid_y - lmy) < 30:
                locked_rock = rock  # อัปเดตตำแหน่งหินเดิม
                still_exists = True
                break
        
        if still_exists:
            # ถ้าเกิน 10 วินาทีแล้ว ให้ล้างล็อก เพื่อจะได้เลือกหินใหม่ในรอบถัดไป
            if last_lock_time and (current_time - last_lock_time > lock_duration):
                locked_rock = None
                last_lock_time = None
        else:
            # หินหายไปก่อนครบเวลา ให้ล้างล็อกทันที
            locked_rock = None
            last_lock_time = None

    if not locked_rock and rocks:
        locked_rock = min(rocks, key=lambda r: r[6])
        last_lock_time = current_time

    # ... ส่วนโค้ดที่เหลือไม่เปลี่ยน ...


    # --- วาดกรอบหินทั้งหมดที่เจอ
    for (x1, y1, x2, y2, conf, cls_id, dist, mid_x, mid_y) in rocks:
        color = (0, 255, 0) if locked_rock and (x1, y1, x2, y2) == locked_rock[:4] else (255, 0, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label = f"Rock {conf:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # --- วาดจุดกึ่งกลางจอ (สีแดง)
    cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

    # --- วาดเส้นหรือทิศทางการเดินไปหาหินที่ล็อก
    if locked_rock:
        _, _, _, _, _, _, _, mid_x, mid_y = locked_rock
        cv2.circle(frame, (mid_x, mid_y), 5, (0, 255, 255), -1)
        cv2.line(frame, (center_x, center_y), (mid_x, mid_y), (0, 255, 255), 2)
        # วาดลูกศรหัวเส้น (ง่ายๆ) 
        # (อาจจะเพิ่มลูกศรสวยๆได้อีก แต่ขอแบบนี้ก่อน)

    # --- คำสั่งเดิน (เหมือนเดิม) ---
    if locked_rock:
        _, _, _, _, _, _, _, mid_x, mid_y = locked_rock
        offset_x = mid_x - center_x
        offset_y = mid_y - center_y
        press_key_e()

        ReleaseKey(W)
        ReleaseKey(A)
        ReleaseKey(D)
        ReleaseKey(SHIFT)

        
        if offset_x > 250:
            PressKey(D)
            PressKey(W)
            PressKey(SHIFT)
        elif offset_x < -250:
            PressKey(A)
            PressKey(W)
            PressKey(SHIFT)
        else:
            PressKey(W)
            PressKey(SHIFT)
    else:
        press_key_e()
        ReleaseKey(W)
        ReleaseKey(A)
        ReleaseKey(D)
        ReleaseKey(SHIFT)
        time.sleep(0.5)
        PressKey(D)
        PressKey(SHIFT)
        time.sleep(2)
        ReleaseKey(D)
        ReleaseKey(SHIFT)

        # time.sleep(2)
        
        # time.sleep(0.3)
        # ReleaseKey(C)
        # time.sleep(5)
        # move_mouse(10, 0)


        # ถ้าไม่เจอหิน ปล่อยคีย์ทั้งหมด (ผมแก้เป็น Release แทน Press)
        

    # --- แสดงผลภาพพร้อมกรอบและเส้น ---
    # height = frame.shape[0]
    # cut_top = int(height * 0.2)
    # cropped_frame = frame[cut_top:, :, :]
    small_frame = cv2.resize(frame, (640, 360))
    cv2.imshow("Rock Detector", small_frame)
    set_always_on_top("Rock Detector")
    # กด 'q' เพื่อออกจากลูป
    key = cv2.waitKey(1) & 0xFF
    if key == 27 or key == ord('q'):  # 27 คือ ESC key
        print("ปิดโปรแกรมโดยผู้ใช้")
        break

cv2.destroyAllWindows()