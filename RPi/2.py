import cv2
from ultralytics import YOLO
from PIL import Image
import csv
import random
import os
import subprocess
import numpy as np
from lcd import LCD
from RPi import GPIO
import time
import signal
from rgb import Rgb
import gradio as gr

GPIO.setmode(GPIO.BCM)
is_playing = False
button = 25
prev_button = 1
count_pressed = 0
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize the YOLO models
model_detect = YOLO('/home/user/2023-2024-projectone-ctai-danyukezz/AI/AI model exam/face_recognition/runs/detect/train7/weights/best.pt')
model_classify = YOLO('/home/user/2023-2024-projectone-ctai-danyukezz/AI/AI model exam/face_recognition/runs/classify/train7/weights/best.pt')
cap = cv2.VideoCapture(0)

def get_spaces(spaces):
      string = ''
      for i in range(16 - spaces):
         string += ' '
      return string

# Function to take a screenshot from the camera feed
def take_screenshot():
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("/home/user/2023-2024-projectone-ctai-danyukezz/AI/AI model exam/face_recognition/screenshot.jpg", frame)
        lcd.send_string("   SCREENSHOT   ", lcd.LCD_LINE_1)
        lcd.send_string("     TAKEN      ", lcd.LCD_LINE_2)
    else:   
        print("Failed to capture frame from the camera feed")

def detect_and_crop_face():
    lcd.clear()
    lcd.send_string("Preprocessing   ", lcd.LCD_LINE_1)
    lcd.send_string("And predicting..", lcd.LCD_LINE_2)
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

    # cropped_image = cropped_image.resize((48,48), resample=Image.BILINEAR)

    # Convert the PIL Image to a NumPy array
    cropped_image_np = np.array(cropped_image)

    cropped_image_np = cv2.cvtColor(cropped_image_np, cv2.COLOR_RGB2BGR)

    # Convert the BGR image to grayscale
    gray_image = cv2.cvtColor(cropped_image_np, cv2.COLOR_BGR2GRAY)

    # Convert the grayscale image back to PIL Image
    gray_image_pil = Image.fromarray(gray_image)

    # Save the grayscale image
    gray_image_pil.save("/home/user/2023-2024-projectone-ctai-danyukezz/AI/AI model exam/face_recognition/cropped_face.jpg")

def classify_emotion():
    weights_path = "/home/user/2023-2024-projectone-ctai-danyukezz/AI/AI model exam/face_recognition/runs/classify/train7/weights/best.pt"
    model = YOLO(weights_path)

    predictions = model.predict("/home/user/2023-2024-projectone-ctai-danyukezz/AI/AI model exam/face_recognition/cropped_face.jpg")
    print(predictions)

    class_labels = ["angry", "happy", "neutral", "sad"]
    
    prediction = predictions[0]  # Assuming a single prediction
    class_probs = prediction.probs

    # Find the index of the highest confidence score
    top1_index = class_probs.top1
    top1_confidence = class_probs.top1conf
    lcd.clear()
    # Map the index to the corresponding class label
    predicted_emotion = class_labels[top1_index]
    top1_confidence = F"{top1_confidence.item():.2f}"
    lcd.send_string(("Emotion: " + predicted_emotion), lcd.LCD_LINE_1)
    lcd.send_string(("Confidence: " + top1_confidence), lcd.LCD_LINE_2)
    if predicted_emotion == 'neutral':
        rgb.control_rgb(248,222,0)
    elif predicted_emotion == 'happy':
        rgb.control_rgb(0,255,0)
    elif predicted_emotion == 'sad':
        rgb.control_rgb(0,0,255)
    elif predicted_emotion == 'angry':
        rgb.control_rgb(255,0,0)
    time.sleep(3)
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
    lcd.clear()
    lcd.send_string(random_author, lcd.LCD_LINE_1)
    lcd.send_string(random_song, lcd.LCD_LINE_2)
    time.sleep(3)
    return random_song

ffplay_process = None
ffmpeg_process = None
finished = False
stopped = False

def play_song(song_name):
    global ffplay_process, ffmpeg_process, finished, message_displayed, stopped, is_playing
    stopped = False
    lcd.clear()
    lcd.send_string("Preparing to    ", lcd.LCD_LINE_1)
    lcd.send_string("Play a song:)   ", lcd.LCD_LINE_2)
    time.sleep(3)
    lcd.clear()
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
            "-nodisp",
            "-autoexit",  # Automatically exit when done
            "-"
        ]
        
        try:
            is_playing = True
            lcd.send_string("Press Q to stop ", lcd.LCD_LINE_1)
            lcd.send_string("Button to pause ", lcd.LCD_LINE_2)
            # Start ffmpeg subprocess to convert MP3 to WAV and output to stdout
            ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            
            # Start ffplay subprocess to read WAV audio from stdin
            ffplay_process = subprocess.Popen(ffplay_command, stdin=ffmpeg_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            while True:
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') and not sleep_mode:
                    lcd.clear()
                    lcd.send_string("Song is stopped", lcd.LCD_LINE_1)
                    lcd.send_string("Starting again ", lcd.LCD_LINE_2)
                    ffplay_process.terminate()
                    ffmpeg_process.terminate()
                    finished = True
                    message_displayed = False
                    stopped = True
                    is_playing = False
                    rgb.control_rgb(0, 0, 0)
                    time.sleep(3)
                    break
                
                if key == ord('q') and sleep_mode:
                    lcd.clear()
                    lcd.send_string("Song is stopped", lcd.LCD_LINE_1)
                    lcd.send_string("Button to start", lcd.LCD_LINE_2)
                    ffplay_process.terminate()
                    ffmpeg_process.terminate()
                    finished = True
                    message_displayed = False
                    stopped = True
                    is_playing = False
                    rgb.control_rgb(0, 0, 0)
                    time.sleep(3)
                    break

                if sleep_mode and ffplay_process.poll() is None:
                    ffplay_process.send_signal(signal.SIGSTOP)

                elif not sleep_mode and ffplay_process.poll() is None:
                    ffplay_process.send_signal(signal.SIGCONT)

                if ffmpeg_process.poll() is not None and not sleep_mode and stopped == False:
                    lcd.clear()
                    lcd.send_string("Song is finished", lcd.LCD_LINE_1)
                    lcd.send_string("Starting again  ", lcd.LCD_LINE_2)
                    ffplay_process.terminate()
                    ffmpeg_process.terminate()
                    finished = True
                    message_displayed = False
                    is_playing = False
                    rgb.control_rgb(0, 0, 0)
                    time.sleep(3)
                    break
                elif ffmpeg_process.poll() is not None and sleep_mode and stopped == False:
                    lcd.clear()
                    lcd.send_string("Song is finished", lcd.LCD_LINE_1)
                    lcd.send_string("Button to start ", lcd.LCD_LINE_2)
                    ffplay_process.terminate()
                    ffmpeg_process.terminate()
                    finished = True
                    message_displayed = False
                    is_playing = False
                    rgb.control_rgb(0, 0, 0)
                    time.sleep(3)
                    break
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")
    else:
        print(f"No matching files found for the song: {song_name}")

message_displayed = False
sleep_mode = True

def button1_callback(pin_number):
    global sleep_mode, message_displayed, ffplay_process
    current_button_state = GPIO.input(button)
    
    if current_button_state == GPIO.LOW and is_playing == False:
        lcd.clear()
        lcd.send_string(' Sleep mode OFF ', lcd.LCD_LINE_1)
        sleep_mode = False
        message_displayed = False

    elif current_button_state == GPIO.LOW and is_playing == True:
        lcd.clear()
        lcd.send_string('Song is playing ', lcd.LCD_LINE_1)
        lcd.send_string('Button to pause ', lcd.LCD_LINE_2)
        sleep_mode = False
        message_displayed = False

    if current_button_state == GPIO.HIGH and is_playing == False:
        lcd.clear()
        lcd.send_string(' Sleep mode ON  ', lcd.LCD_LINE_1)
        rgb.control_rgb(0,0,0)
        sleep_mode = True
        message_displayed = False

    elif current_button_state == GPIO.HIGH and is_playing == True:
        lcd.clear()
        lcd.send_string('Song is paused! ', lcd.LCD_LINE_1)
        lcd.send_string('Button - unpause', lcd.LCD_LINE_2)
        sleep_mode = True
        message_displayed = False

GPIO.add_event_detect(button, GPIO.BOTH, callback=button1_callback, bouncetime=300)

try:
    rgb = Rgb()
    rgb.setup()
    lcd = LCD()
    lcd.lcd_init()
    lcd.send_string("Ready to start! ", lcd.LCD_LINE_1)
    lcd.send_string("Press a button ", lcd.LCD_LINE_2)
    while True:
        key = cv2.waitKey(1) & 0xFF
        if not sleep_mode:
            if not message_displayed:
                time.sleep(3)
                lcd.clear()
                lcd.send_string("Press SPACE to ", lcd.LCD_LINE_1)
                lcd.send_string("take screenshot", lcd.LCD_LINE_2)
                message_displayed = True  # Ensure message is displayed only once
            ret, frame = cap.read()
            if ret and not sleep_mode:
                cv2.imshow('Camera Feed', frame)
            if key == ord(' '):
                if sleep_mode == False:
                    lcd.clear()
                    take_screenshot()
                    time.sleep(3)
                if sleep_mode == False:
                    detect_and_crop_face()
                    time.sleep(3)
                if sleep_mode == False:
                    predicted_emotion, confidence = classify_emotion()
                    time.sleep(1)
                if sleep_mode == False:
                    song_name = get_random_song_by_emotion(predicted_emotion)
                    time.sleep(1)
                if sleep_mode == False:
                    play_song(song_name)
        else:
            key = 1
            time.sleep(0.1)  # Shorter sleep interval for better responsiveness
except KeyboardInterrupt:
    pass
finally:
    lcd.clear()
    cap.release()
    cv2.destroyAllWindows()
    rgb.control_rgb(0, 0, 0)