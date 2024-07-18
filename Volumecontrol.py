import cv2
import time
import math
import numpy as np
import handmod as hm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initialize hand detector
detector = hm.handDetector(detectionCon=0.7)

# Initialize volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

cap = cv2.VideoCapture(0)  

pTime = 0

while True:
    success, img = cap.read()
    if not success:
        break
    
    img = detector.findHands(img)
    lmlist, bbox = detector.findPosition(img, draw=False)
    
    if len(lmlist) != 0:
        if detector.isStopGesture():
            # If stop gesture is detected, skip volume control and hide hands
            cv2.putText(img, "Stop Gesture Detected", (50, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
        else:
            x1, y1 = lmlist[4][1], lmlist[4][2]
            x2, y2 = lmlist[8][1], lmlist[8][2]
            length = math.hypot(x2 - x1, y2 - y1)
            
            # Convert length to volume level
            vol = np.interp(length, [50, 300], [minVol, maxVol])
            volBar = np.interp(length, [50, 300], [400, 150])
            volPer = np.interp(length, [50, 300], [0, 100])
            
            # Set volume
            volume.SetMasterVolumeLevel(vol, None)
            
            # Drawing
            cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
            cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
    
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
    
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


























cap.release()






















cv2.destroyAllWindows()
