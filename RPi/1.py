from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt

# Load the trained model
model = YOLO('runs/detect/train4/weights/best.pt')

# Open a connection to the webcam (0 is the default camera, using DirectShow backend)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    # Resize frame if needed (optional)
    img_size = 640
    frame_resized = cv2.resize(frame, (img_size, img_size))

    # Evaluate the model on the current frame
    results = model.predict(source=frame_resized)

    # Print results to inspect the structure
    print(results)

    # Draw results on the frame
    for result in results:
        for i, box in enumerate(result.boxes.xyxy):
            x1, y1, x2, y2 = map(int, box[:4])
            class_id = int(result.boxes.cls[i])  # Assuming there's a 'cls' attribute for class ids
            class_label = model.names[class_id]
            cv2.rectangle(frame_resized, (x1, y1), (x2, y2), (255, 0, 0), 2)
            # Put class label above the bounding box
            cv2.putText(frame_resized, class_label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    # Convert BGR image to RGB for displaying with matplotlib
    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

    # Display the resulting frame using matplotlib
    ax.clear()
    ax.imshow(frame_rgb)
    plt.draw()
    plt.pause(0.001)

    # Break the loop on 'q' key press
    if plt.waitforbuttonpress(0.001):
        break

# When everything done, release the capture and close windows
cap.release()
plt.close()