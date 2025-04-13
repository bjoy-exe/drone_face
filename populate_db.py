import face_recognition
import mysql.connector
import base64
import os
import numpy as np

# === CONFIG ===
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "12"  # <-- Use the password you set
DB_NAME = "face_db"

# === CONNECT TO DATABASE ===
try:
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()
    print("✅ Connected to MySQL.")
except mysql.connector.Error as err:
    print(f"❌ MySQL connection error: {err}")
    exit()

# === USER IMAGES ===
users = {
    "Alice": ("@alice_insta", "faces/user1.jpg"),
    "Bob": ("@bobby_lens", "faces/user2.jpg"),
    "Charlie": ("@charlie_ig", "faces/user3.jpg"),
    "Diana": ("@diana_snap", "faces/user4.jpg"),
    "Eve": ("@eve_pix", "faces/user5.jpg"),
    "bijoy":("bjoy.exe", "faces/user6.jpg"), 
    "vishnu":("dark._.bro", "faces/user7.jpg")
}

# === INSERT USER ENCODINGS ===
for name, (insta, img_path) in users.items():
    if not os.path.exists(img_path):
        print(f"❌ Image not found: {img_path}")
        continue

    image = face_recognition.load_image_file(img_path)
    encodings = face_recognition.face_encodings(image)

    if not encodings:
        print(f"⚠️ No face found in {img_path}, skipping.")
        continue

    encoding = encodings[0]
    encoding_str = base64.b64encode(encoding.tobytes()).decode('utf-8')

    try:
        cursor.execute("INSERT INTO users (name, instagram, face_encoding) VALUES (%s, %s, %s)",
                       (name, insta, encoding_str))
        print(f"✅ Inserted {name} into database.")
    except mysql.connector.Error as err:
        print(f"❌ Failed to insert {name}: {err}")

# === CLEANUP ===
conn.commit()
cursor.close()
conn.close()
print("✅ All done. Database populated.")

