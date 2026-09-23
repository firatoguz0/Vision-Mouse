import cv2
import numpy as np
import mediapipe as mp
import pyautogui
import math
import time

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0  

screen_w, screen_h = pyautogui.size()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

hands = mp_hands.Hands(
    max_num_hands=1,
    model_complexity=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.5
)

frameR = 60  

locked = False
clicking = False
lock_start_time = 0
LOCK_TIMEOUT = 1.2

no_hand_frames = 0
NO_HAND_RESET = 10


class OneEuroFilter:
    """Yavaş harekette yumuşak, hızlı harekette anlık tepki veren filtre."""
    def __init__(self, mincutoff=1.0, beta=0.7, dcutoff=1.0):
        self.mincutoff = mincutoff
        self.beta = beta
        self.dcutoff = dcutoff
        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None

    def _alpha(self, cutoff, te):
        tau = 1.0 / (2 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / te)

    def filter(self, x, t=None):
        if t is None:
            t = time.time()
        if self.t_prev is None:
            self.t_prev = t
            self.x_prev = x
            return x

        te = max(t - self.t_prev, 1e-3)

        dx = (x - self.x_prev) / te
        a_d = self._alpha(self.dcutoff, te)
        dx_hat = a_d * dx + (1 - a_d) * self.dx_prev

        cutoff = self.mincutoff + self.beta * abs(dx_hat)
        a = self._alpha(cutoff, te)
        x_hat = a * x + (1 - a) * self.x_prev

        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t
        return x_hat

    def reset(self):
        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None


filter_x = OneEuroFilter()
filter_y = OneEuroFilter()

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img_h, img_w, _ = img.shape

    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    rgb_img.flags.writeable = False
    result = hands.process(rgb_img)
    rgb_img.flags.writeable = True

    if result.multi_hand_landmarks:
        no_hand_frames = 0

        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmarks = hand_landmarks.landmark

            index_x = int(landmarks[8].x * img_w)
            index_y = int(landmarks[8].y * img_h)

            thumb_x = int(landmarks[4].x * img_w)
            thumb_y = int(landmarks[4].y * img_h)

            wrist_x = int(landmarks[0].x * img_w)
            wrist_y = int(landmarks[0].y * img_h)
            mid_x = int(landmarks[9].x * img_w)
            mid_y = int(landmarks[9].y * img_h)
            hand_size = math.hypot(mid_x - wrist_x, mid_y - wrist_y)

            length = math.hypot(index_x - thumb_x, index_y - thumb_y)

            approach_threshold = hand_size * 0.6
            click_threshold    = hand_size * 0.4
            release_threshold  = hand_size * 0.75

            if not locked:
                raw_mouse_x = np.interp(index_x, (frameR, img_w - frameR), (0, screen_w))
                raw_mouse_y = np.interp(index_y, (frameR, img_h - frameR), (0, screen_h))

                curr_x = filter_x.filter(raw_mouse_x)
                curr_y = filter_y.filter(raw_mouse_y)

                curr_x = np.clip(curr_x, 0, screen_w - 1)
                curr_y = np.clip(curr_y, 0, screen_h - 1)

                pyautogui.moveTo(curr_x, curr_y)

                if length < approach_threshold:
                    locked = True
                    lock_start_time = time.time()

                cv2.circle(img, (index_x, index_y), 10, (255, 0, 255), cv2.FILLED)

            else:
                if length < click_threshold and not clicking:
                    pyautogui.click()
                    clicking = True

                if length > release_threshold:
                    locked = False
                    clicking = False
                elif time.time() - lock_start_time > LOCK_TIMEOUT:
                    locked = False
                    clicking = False

                color = (0, 255, 0) if clicking else (0, 255, 255)
                cv2.circle(img, (index_x, index_y), 12, color, cv2.FILLED)

    else:
        no_hand_frames += 1
        if no_hand_frames > NO_HAND_RESET:
            locked = False
            clicking = False
            filter_x.reset()
            filter_y.reset()

    cv2.imshow("Sanal Fare", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()