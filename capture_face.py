import cv2

# Replace with your IP Webcam stream
video_url = "http://192.168.1.5:8080/video"  # Replace with your stream

cap = cv2.VideoCapture(video_url)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("Phone Cam - Press Q to Capture", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.imwrite("captured_face.jpg", frame)
        print("📸 Face image saved as captured_face.jpg")
        break

cap.release()
cv2.destroyAllWindows()
