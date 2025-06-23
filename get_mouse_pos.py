import pyautogui
import time

print("ขยับเมาส์ไปตำแหน่งที่ต้องการ คลิก")
time.sleep(5)

while True:
    x, y = pyautogui.position()
    print(f"Mouse position: ({x}, {y})")
    time.sleep(0.5)
