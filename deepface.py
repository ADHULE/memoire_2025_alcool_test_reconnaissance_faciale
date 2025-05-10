from deepface import DeepFace
import cv2
import threading
import time  # For potential debugging

# Configuration
CAMERA_INDEX = 0  # Usually 0 for the default webcam
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
REFERENCE_IMAGE_PATH = "systeme_adhule.jpg"
VERIFICATION_INTERVAL = 15  # Check every N frames
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 2
FONT_COLOR_MATCH = (0, 255, 0)  # Green
FONT_COLOR_NO_MATCH = (0, 0, 255)  # Red
FONT_THICKNESS = 3
TEXT_POSITION = (20, FRAME_HEIGHT - 30)  # Adjust position as needed

# Load the reference image once
try:
    reference_img = cv2.imread(REFERENCE_IMAGE_PATH)
    if reference_img is None:
        raise FileNotFoundError(f"Error: Could not load reference image from {REFERENCE_IMAGE_PATH}")
except FileNotFoundError as e:
    print(e)
    exit()

face_match = False
counter = 0

def check_face(frame):
    global face_match
    try:
        result = DeepFace.verify(frame, reference_img.copy(), enforce_detection=True)
        if isinstance(result, dict) and result.get("verified"):
            face_match = True
        else:
            face_match = False
    except ValueError as e:
        face_match = False
        print(f"ValueError during face verification: {e}")
    except Exception as e:
        face_match = False
        print(f"An unexpected error occurred during face verification: {e}")

# Initialize the camera
camera = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()

while True:
    ret, frame = camera.read()

    if not ret:
        print("Error: Could not read frame from camera.")
        break

    if counter % VERIFICATION_INTERVAL == 0:
        try:
            threading.Thread(target=check_face, args=(frame.copy(),)).start()
        except RuntimeError as e:
            print(f"Error starting thread: {e}")

    if face_match:
        cv2.putText(frame, "MATCH", TEXT_POSITION, FONT, FONT_SCALE, FONT_COLOR_MATCH, FONT_THICKNESS)
    else:
        cv2.putText(frame, "NO MATCH", TEXT_POSITION, FONT, FONT_SCALE, FONT_COLOR_NO_MATCH, FONT_THICKNESS)

    cv2.imshow("Video", frame)

    key = cv2.waitKey(1)
    if key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()