import cv2
import mediapipe as mp
import pyautogui
import time
import numpy as np
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
last_action_time = 0
action_delay = 1
logo = cv2.imread('logo.png', cv2.IMREAD_UNCHANGED)
if logo is None:
    print("Errore: logo.png non trovato.")
    exit()
logo_width = 100
scale = logo_width / logo.shape[1]
logo = cv2.resize(logo, (logo_width, int(logo.shape[0] * scale)), interpolation=cv2.INTER_AREA)
def overlay_logo(frame, logo, pos=(10,10)):
    if logo.shape[2] == 4:
        b,g,r,a = cv2.split(logo)
        overlay_color = cv2.merge((b,g,r))
        mask = cv2.merge((a,a,a))
        h, w = overlay_color.shape[:2]
        roi = frame[pos[1]:pos[1]+h, pos[0]:pos[0]+w]
        img1_bg = cv2.bitwise_and(roi, cv2.bitwise_not(mask))
        img2_fg = cv2.bitwise_and(overlay_color, mask)
        dst = cv2.add(img1_bg, img2_fg)
        frame[pos[1]:pos[1]+h, pos[0]:pos[0]+w] = dst
    else:
        h, w = logo.shape[:2]
        frame[pos[1]:pos[1]+h, pos[0]:pos[0]+w] = logo
def overlay_logo_with_shadow(frame, logo, pos=(10,10)):
    shadow_offset = 4
    shadow = np.zeros_like(logo)
    if logo.shape[2] == 4:
        shadow[..., :3] = 0
        shadow[..., 3] = logo[..., 3]
    else:
        shadow[:] = 0
    overlay_logo(frame, shadow, (pos[0] + shadow_offset, pos[1] + shadow_offset))
    overlay_logo(frame, logo, pos)
def is_thumb_up(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[4]
    thumb_ip = hand_landmarks.landmark[3]
    index_tip = hand_landmarks.landmark[8]
    index_pip = hand_landmarks.landmark[6]
    middle_tip = hand_landmarks.landmark[12]
    middle_pip = hand_landmarks.landmark[10]
    thumb_up = thumb_tip.y < thumb_ip.y
    index_closed = index_tip.y > index_pip.y
    middle_closed = middle_tip.y > middle_pip.y
    return thumb_up and index_closed and middle_closed
def is_thumb_down(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[4]
    thumb_ip = hand_landmarks.landmark[3]
    index_tip = hand_landmarks.landmark[8]
    index_pip = hand_landmarks.landmark[6]
    middle_tip = hand_landmarks.landmark[12]
    middle_pip = hand_landmarks.landmark[10]
    thumb_down = thumb_tip.y > thumb_ip.y
    index_closed = index_tip.y > index_pip.y
    middle_closed = middle_tip.y > middle_pip.y
    return thumb_down and index_closed and middle_closed
def is_palm_open(hand_landmarks):
    tips_ids = [8, 12, 16, 20]
    extended = 0
    for tip_id in tips_ids:
        tip = hand_landmarks.landmark[tip_id]
        pip = hand_landmarks.landmark[tip_id - 2]
        if tip.y < pip.y:
            extended += 1
    return extended == 4
def is_index_pointing(hand_landmarks):
    index_tip = hand_landmarks.landmark[8]
    index_pip = hand_landmarks.landmark[6]
    other_tips = [12, 16, 20]
    index_extended = index_tip.y < index_pip.y
    others_closed = all(hand_landmarks.landmark[tip].y > hand_landmarks.landmark[tip - 2].y for tip in other_tips)
    return index_extended and others_closed
def is_v_sign(hand_landmarks):
    index_tip = hand_landmarks.landmark[8]
    index_pip = hand_landmarks.landmark[6]
    middle_tip = hand_landmarks.landmark[12]
    middle_pip = hand_landmarks.landmark[10]
    ring_tip = hand_landmarks.landmark[16]
    ring_pip = hand_landmarks.landmark[14]
    pinky_tip = hand_landmarks.landmark[20]
    pinky_pip = hand_landmarks.landmark[18]
    index_extended = index_tip.y < index_pip.y
    middle_extended = middle_tip.y < middle_pip.y
    ring_closed = ring_tip.y > ring_pip.y
    pinky_closed = pinky_tip.y > pinky_pip.y
    return index_extended and middle_extended and ring_closed and pinky_closed
def is_fist(hand_landmarks):
    return all(hand_landmarks.landmark[tip].y > hand_landmarks.landmark[tip - 2].y for tip in [8, 12, 16, 20])
def draw_status_box(frame, text, color=(0,255,0)):
    h, w = frame.shape[:2]
    box_h = 60
    cv2.rectangle(frame, (8, h - box_h + 8), (w - 8, h - 8), (30, 30, 30), -1)
    cv2.rectangle(frame, (0, h - box_h), (w, h), color, -1)
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    text_x = (w - text_size[0]) // 2
    text_y = h - (box_h // 2) + (text_size[1] // 2)
    cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
def draw_tooltip(frame, text):
    cv2.rectangle(frame, (10, 10), (500, 50), (50, 50, 50), -1)
    cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75) as hands:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        current_time = time.time()
        action_text = ""
        action_color = (200, 200, 200)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0,255,255), thickness=2, circle_radius=3),
                    mp_drawing.DrawingSpec(color=(0,128,255), thickness=2))
                if is_thumb_up(hand_landmarks):
                    action_text = "Volume + (Pollice in su)"
                    action_color = (0, 255, 0)
                    if current_time - last_action_time > action_delay:
                        pyautogui.press('volumeup')
                        last_action_time = current_time
                elif is_thumb_down(hand_landmarks):
                    action_text = "Volume - (Pollice in giu')"
                    action_color = (0, 0, 255)
                    if current_time - last_action_time > action_delay:
                        pyautogui.press('volumedown')
                        last_action_time = current_time
                elif is_palm_open(hand_landmarks):
                    action_text = "Play/Pausa (Palmo aperto)"
                    action_color = (0, 255, 255)
                    if current_time - last_action_time > action_delay:
                        pyautogui.press('playpause')
                        last_action_time = current_time
                elif is_index_pointing(hand_landmarks):
                    action_text = "Avanti (Indice puntato)"
                    action_color = (0, 180, 255)
                    if current_time - last_action_time > action_delay:
                        pyautogui.press('right')
                        last_action_time = current_time
                elif is_v_sign(hand_landmarks):
                    action_text = "Indietro (V segno)"
                    action_color = (255, 0, 180)
                    if current_time - last_action_time > action_delay:
                        pyautogui.press('left')
                        last_action_time = current_time
                elif is_fist(hand_landmarks):
                    action_text = "Mute/Unmute (Pugno)"
                    action_color = (180, 0, 255)
                    if current_time - last_action_time > action_delay:
                        pyautogui.press('volumemute')
                        last_action_time = current_time
        draw_status_box(frame, action_text, action_color)
        h, w = frame.shape[:2]
        logo_h, logo_w = logo.shape[:2]
        overlay_logo_with_shadow(frame, logo, pos=(w - logo_w - 10, 10))
        cv2.imshow("Cerebrum Pulse - By VincenzoT", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
cap.release()
cv2.destroyAllWindows()
