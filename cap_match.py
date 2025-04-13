import cv2
import face_recognition
import mysql.connector
import numpy as np
import base64
import sys
import time
import threading
import os

# ========== Terminal Style ==========
GREEN = "\033[92m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Function to slowly print text with animation
def slow_print(text, delay=0.04):
    for char in text:
        sys.stdout.write(GREEN + char + RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# ========== Animation Effects ==========
def spinner(message, stop_event):
    chars = "|/-\\"
    idx = 0
    while not stop_event.is_set():
        print(f"\r{GREEN}[{chars[idx % len(chars)]}] {message}{RESET}", end='', flush=True)
        time.sleep(0.1)
        idx += 1
    print("\r" + " " * (len(message) + 6) + "\r", end='')

def fake_scan(text="🔍 SCANNING..."):
    slow_print(text)
    for i in range(3):
        slow_print("." * (i + 1), delay=0.3)

# ========== Step 1: Capture Face ==========

def capture_face_image():
    video_url = "http://192.168.1.4:8080/video"  # Replace with your phone stream
    cap = cv2.VideoCapture(video_url)

    print("[INFO] Streaming from phone... Press Q to capture face.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            continue

        cv2.imshow("Phone Cam - Press Q to Capture", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.imwrite("captured_face.jpg", frame)
            print("📸 Face image saved as captured_face.jpg")
            break

    cap.release()
    cv2.destroyAllWindows()

# ========== Step 2: Match Face ==========
def match_face_with_db():
    slow_print("🧠 ANALYZING FACE...")
    stop_event = threading.Event()
    t = threading.Thread(target=spinner, args=("Encoding facial data", stop_event))
    t.start()

    image = face_recognition.load_image_file("captured_face.jpg")
    encodings = face_recognition.face_encodings(image)

    stop_event.set()
    t.join()

    if not encodings:
        slow_print("❌ ERROR: No face detected.")
        return

    unknown_encoding = encodings[0]

    stop_event = threading.Event()
    t = threading.Thread(target=spinner, args=("Connecting to SQL Database", stop_event))
    t.start()

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12",  # <-- Replace with your actual password
            database="face_db"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT name, instagram, face_encoding FROM users")
        records = cursor.fetchall()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        stop_event.set()
        t.join()
        slow_print(f"❌ DATABASE ERROR: {err}")
        return

    stop_event.set()
    t.join()
    fake_scan()

    for name, insta, enc in records:
        try:
            known_encoding = np.frombuffer(base64.b64decode(enc), dtype=np.float64)
            match = face_recognition.compare_faces([known_encoding], unknown_encoding)[0]
            if match:
                slow_print("✅ MATCH IDENTIFIED!")
                slow_print(f"👤 NAME: {name}")
                slow_print(f"📸 INSTAGRAM: @{insta}")
                return
        except Exception as e:
            print(GREEN + f"[!] ERROR WITH USER DATA: {e}" + RESET)

    slow_print("❌ NO MATCH FOUND IN DATABASE.")

# ========== MAIN ==========
if __name__ == "__main__":
    os.system("clear")  # Clear the terminal screen
    slow_print("🚀 Starting Face Detection & Instagram Lookup Process...")

    time.sleep(1)  # Delay for the first loading message
    capture_face_image()  # Capture face from webcam
    match_face_with_db()  # Match the captured face with database
