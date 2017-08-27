import cv2
import numpy as np
from os import system
import os
import time
import shutil, glob

# Create a VideoCapture object. The argument can either be the device index or
# the name of a video file. If one camera is connected pass 0. To select a
# second camera, pass 1, etc.
#cap = cv2.VideoCapture(1)

cap = cv2.VideoCapture("/home/elizabeth/Dropbox/SaveImageToAviEx_AVI-0000.avi")

# Check if camera opened successfully
if (cap.isOpened()== False): 
  print("Error opening video stream or file")

cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE);
# REad until video is completed
font = cv2.FONT_HERSHEY_SIMPLEX
k = 1; # set up a counter for the number of frames
frame_rate = cap.get(cv2.CAP_PROP_FPS) # get the frame rate of the video
print frame_rate
while(cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    time = k/frame_rate #get the time in seconds of the frame
    cv2.putText(frame,'Frame: %d' % k,(10,50), font,1,(255,255,255),2,cv2.LINE_AA)
    cv2.putText(frame,'Time: %f' % time,(10,100), font,1,(255,255,255),2,cv2.LINE_AA)

    # Display the resulting frame
    cv2.imshow('frame',frame)
    k = k+1 #increase frame count
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()