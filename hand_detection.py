import cv2
import mediapipe as mp
import paho.mqtt.client as mqtt


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

def count_fingers(hand_landmarks, handedness):
    if handedness == "Right":
        finger_tips = [4, 8, 12, 16, 20]
        pip_joints = [3, 7, 11, 15, 19]
    else : 
        finger_tips = [ 8, 12, 16, 20, 4]
        pip_joints = [7, 11, 15, 19, 3]
        
    count = 0
    
    if hand_landmarks.landmark[finger_tips[0]].x < hand_landmarks.landmark[pip_joints[0]].x:
        count += 1
        
    for i in range(1,5):
        if hand_landmarks.landmark[finger_tips[i]].y < hand_landmarks.landmark[pip_joints[i]].y:
            count += 1
    
    return count

def on_connect(client, userdata, flags, rc):
    print("Connected with result code" + str(rc))
    

client = mqtt.Client()
client.on_connect = on_connect
client.connect("broker.hivemq.com", 1883, 60)
 
cap = cv2.VideoCapture(0)
previous_count = 0

with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while cap.isOpened():
        ret, frame = cap.read()

        frame = cv2.flip(frame, 1)

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(image)

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks, handedness_info in zip(results.multi_hand_landmarks, results.multi_handedness):
                handedness = handedness_info.classification[0].label
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                count = count_fingers(hand_landmarks, handedness)
                
                if count != previous_count:
                    print("Value", count)
                    client.publish("topicname", str(count))
                previous_count = count

        cv2.imshow('Hand Detection', image)

        key = cv2.waitKey(10)
        if key == 27:
            break

cap.release()
cv2.destroyAllWindows()
