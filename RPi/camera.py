import cv2

# Try different indices if 0 doesn't work
vid = cv2.VideoCapture(0)

if not vid.isOpened():
    print("Error: Could not open camera.")
    exit()

while True:
    # Capture the video frame by frame
    ret, frame = vid.read()

    if not ret:
        print("Error: Failed to capture image")
        break

    # Display the resulting frame
    cv2.imshow('frame', frame)

    # The 'q' button is set as the quitting button
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()