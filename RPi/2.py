import cv2
from ultralytics import YOLO
from PIL import Image
import csv
import random
import os
import subprocess
import numpy as np
from lcd import LCD
import time
lcd = LCD()
lcd.lcd_init()
lcd.clear()
lcd.send_string("Press SPACE to ", lcd.LCD_LINE_1)
lcd.send_string("take screenshot", lcd.LCD_LINE_2)
time.sleep(10)
lcd.clear()
# Initialize the YOLO models
model_detect = YOLO('/home/user/2023-2024-projectone-ctai-danyukezz/AI/AI model exam/face_recognition/runs/detect/train7/weights/best.pt')
model_classify = YOLO('/home/user/2023-2024-projectone-ctai-danyukezz/AI/AI model exam/face_recognition/runs/classify/train6')
cap = cv2.VideoCapture(0)
# Function to take a screenshot from the camera feed
def take_screenshot():
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("/home/user/2023-2024-projectone-ctai-danyukezz/AI/AI model exam/face_recognition/screenshot.jpg", frame)
        lcd.send_string("   SCREENSHOT   ", lcd.LCD_LINE_1)
        lcd.send_string("     TAKEN      ", lcd.LCD_LINE_2)
        time.sleep(3)
        lcd.clear()
    else:   
        print("Failed to capture frame from the camera feed")

def detect_and_crop_face():
    path = "/home/user/2023-2024-projectone-ctai-danyukezz/AI/AI model exam/face_recognition/screenshot.jpg"
    result = model_detect.predict(path)
    
    if not result:
        print("No detection results.")
        return None
    
    result = model_detect.predict(path)

    bounding_box = result[0].boxes[0]  

    x1, y1, x2, y2 = bounding_box.xyxy[0].tolist()

    original_image = Image.open(path)

    cropped_image = original_image.crop((x1, y1, x2, y2))

    cropped_image = cropped_image.resize((48,48), resample=Image.BILINEAR)

    # Convert the PIL Image to a NumPy array
    cropped_image_np = np.array(cropped_image)

    # Convert the image from RGB to BGR (if needed)
    cropped_image_np = cv2.cvtColor(cropped_image_np, cv2.COLOR_RGB2BGR)

    # Convert the BGR image to grayscale
    gray_image = cv2.cvtColor(cropped_image_np, cv2.COLOR_BGR2GRAY)

    # Convert the grayscale image back to PIL Image
    gray_image_pil = Image.fromarray(gray_image)

    # Save the grayscale image
    gray_image_pil.save("/home/user/2023-2024-projectone-ctai-danyukezz/AI/AI model exam/face_recognition/cropped_face.jpg")

def classify_emotion():
    lcd.send_string("Predicting...", lcd.LCD_LINE_1)
    time.sleep(3)
    lcd.clear()
    weights_path = "/home/user/2023-2024-projectone-ctai-danyukezz/AI/AI model exam/face_recognition/runs/classify/train5/weights/best.pt"
    # Initialize YOLO model with the weights file
    model = YOLO(weights_path)

    # Perform inference on the image
    predictions = model.predict("/home/user/2023-2024-projectone-ctai-danyukezz/AI/AI model exam/face_recognition/cropped_face.jpg")
    print(predictions)

    class_labels = ["angry", "happy", "neutral", "sad"]

    # Extract the class probabilities from the predictions
    prediction = predictions[0]  # Assuming a single prediction
    class_probs = prediction.probs

    # Find the index of the highest confidence score
    top1_index = class_probs.top1
    top1_confidence = class_probs.top1conf

    # Map the index to the corresponding class label
    predicted_emotion = class_labels[top1_index]
    lcd.send_string(f"Emotion: {predicted_emotion}", lcd.LCD_LINE_1)
    lcd.send_string(f"Confidence: {top1_confidence.item():.2f}", lcd.LCD_LINE_2)
    time.sleep(5)
    lcd.clear()
    
    return predicted_emotion, top1_confidence

def get_random_song_by_emotion(predicted_emotion):
    songs_by_emotion = {1: [], 2: [], 3: [], 4: []}
    with open('/home/user/2023-2024-projectone-ctai-danyukezz/AI/AI model exam/face_recognition/music.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            emotion = int(row['Emotion'])
            author = row['Author Name']
            song = row['Song Name']
            songs_by_emotion[emotion].append((author, song))

    # Map the predicted emotion to the corresponding emotion code
    if predicted_emotion == 'neutral':
        emotion_code = 1
    elif predicted_emotion == 'happy':
        emotion_code = 2
    elif predicted_emotion == 'sad':
        emotion_code = 3
    elif predicted_emotion == 'angry':
        emotion_code = 4

    # Get a random song from the list of songs corresponding to the predicted emotion
    random_author, random_song = random.choice(songs_by_emotion[emotion_code])
    print("Author:", random_author)
    print("Song:", random_song)

    lcd.send_string(random_author, lcd.LCD_LINE_1)
    lcd.send_string(random_song, lcd.LCD_LINE_2)
    time.sleep(3)
    lcd.clear()
    return random_song

def play_song(song_name):
    directory = "/home/user/2023-2024-projectone-ctai-danyukezz/AI/AI model exam/face_recognition/songs"  # Change this to your directory

    # List all files in the directory
    files_in_directory = os.listdir(directory)

    # Filter files that contain the song name as a substring
    matching_files = [file for file in files_in_directory if song_name.lower() in file.lower()]

    # Print the matching files
    if matching_files:
        file_path = os.path.join(directory, matching_files[0])
        print(f"Loading file: {file_path}")
        mp3_file = file_path
        
        # Command for ffmpeg to convert MP3 to WAV and output to stdout
        ffmpeg_command = [
            "ffmpeg", 
            "-i", mp3_file, 
            "-f", "wav", 
            "-"
        ]
        
        # Command for ffplay to read WAV audio from stdin
        ffplay_command = [
            "ffplay", 
            "-nodisp",  # Suppress video display
            "-"
        ]
        
        try:
            lcd.send_string("Playing a song:)", lcd.LCD_LINE_1)
            lcd.send_string("ENTER to stop", lcd.LCD_LINE_2)
            # Start ffmpeg subprocess to convert MP3 to WAV and output to stdout
            ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            
            # Start ffplay subprocess to read WAV audio from stdin
            ffplay_process = subprocess.Popen(ffplay_command, stdin=ffmpeg_process.stdout)
            
            # Wait for the user to exit by pressing Enter
            print("Press Enter to stop playback...")
            input() # Wait for a single character input (Enter key)
            lcd.clear()
            # Terminate ffplay process
            ffplay_process.terminate()
            
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")
    else:
        print(f"No matching files found for the song: {song_name}")

while True:
    ret, frame = cap.read()
    if ret:
        cv2.imshow('Camera Feed', frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '):
        lcd.clear()
        take_screenshot()
        time.sleep(3)
        detect_and_crop_face()
        time.sleep(3)
        predicted_emotion, confidence = classify_emotion()
        time.sleep(3)
        song_name = get_random_song_by_emotion(predicted_emotion)
        time.sleep(3)
        play_song(song_name)

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
lcd.clear()
