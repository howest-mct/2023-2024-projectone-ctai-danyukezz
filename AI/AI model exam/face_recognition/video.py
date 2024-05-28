# import cv2
# from ultralytics import YOLO

# # Function to take a screenshot from the camera feed
# def take_screenshot():
#     # Capture a frame from the camera feed
#     ret, frame = cap.read()

#     if ret:
#         # Save the frame as an image
#         cv2.imwrite('/Users/danyukezz/Desktop/1 year 2 semester/project one/2023-2024-projectone-ctai-danyukezz/AI model exam/face_recognition/screenshot.jpg', frame)
#     else:
#         print("Failed to capture frame from the camera feed")

# # Start the camera feed
# cap = cv2.VideoCapture(0)  # Change 0 to the appropriate camera index if needed

# # Load your trained model
# # model = YOLO("/Users/danyukezz/Desktop/1 year 2 semester/project one/2023-2024-projectone-ctai-danyukezz/AI model exam/face_recognition/runs/detect/train5/weights/best.pt")

# # Listen for key presses
# while True:
#     # Capture a frame from the camera feed
#     ret, frame = cap.read()
#     if ret:
#         cv2.imshow('Camera Feed', frame)

#     key = cv2.waitKey(1) & 0xFF
#     if key == ord(' '):  # Space key press
#         take_screenshot()
#         break
#     elif key == ord('q'):  # Q key press
#         break

# # Close the camera feed and all OpenCV windows
# cap.release()
# cv2.destroyAllWindows()
from ultralytics import YOLO

# Load your trained model
# model = YOLO("/Users/danyukezz/Desktop/1 year 2 semester/project one/2023-2024-projectone-ctai-danyukezz/AI model exam/face_recognition/runs/detect/train7/weights/best.pt")
model = YOLO("/Users/danyukezz/Desktop/1 year 2 semester/project one/2023-2024-projectone-ctai-danyukezz/AI/AI model exam/face_recognition/runs/detect/train7/weights/best.pt")
results = model.predict(source='0', show=True)

print(results)