import cv2
import numpy as np
from os import system
import os
import time
import shutil, glob
import csv
import datetime

def nothing(x):
    pass
    
def selectROI(event, x, y, flags, param):
    global roi_pts
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(frame0,(x,y),10,(0,255,0),-1) # draws a green circle at the point you clicked
        roi_pts_new = [x,y]
        roi_pts.append(roi_pts_new)
        return roi_pts

def crop2roi(frame0,roi_pts,mask):
    # Crops the image to the region of interest based on the points that are selected by the user. Output is a grayscale image. Everything outside of the region of interest is set to black. Image is still the same size as the camera image.
    # Draws a closed polygon with yellow lines which connect the green points that were selected by the user.
    # cv2.namedWindow('image_roi',cv2.WINDOW_NORMAL)
    cv2.polylines(frame0,[roi_pts],True,(0,255,255))
    # cv2.imshow('image_roi',frame0)
    # cv2.waitKey(200)
    cv2.fillPoly(mask,[roi_pts],(255,255,255))
    # cv2.imshow('image_roi',mask)
    # cv2.waitKey(200)
    # cv2.destroyWindow('image_roi')

    # Convert image to grayscale
    # frame0_gray = cv2.cvtColor(clone_frame0,cv2.COLOR_BGR2GRAY)
    # # Invert colors in grayscale image opecv
    # frame0_gray_invert = cv2.bitwise_not(frame0_gray)
    result = cv2.bitwise_and(clone_frame0,clone_frame0,mask = mask)
    return result

def thresh(mask, roi_pts, frame0_roi):



    frame0_hsv = cv2.cvtColor(frame0_roi,cv2.COLOR_BGR2HSV)
    # define range of blue color in HSV
    lower_black = np.array([0,0,0])
    upper_black = np.array([180,255,30])
    mask2 = cv2.inRange(frame0_hsv, lower_black, upper_black)

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame0_roi,frame0_roi, mask= mask2)
    # cv2.namedWindow('threshold')
    # cv2.imshow('threshold',frame0_hsv)
    # cv2.waitKey(0)
    # cv2.imshow('threshold',mask2)
    # cv2.waitKey(0)
    # cv2.imshow('threshold',res)
    # cv2.waitKey(0)
    return mask2

def detectContours(frame0_roi,frame0_bin,contour_info,position_info,blackOnWhite):
    # bin_result is the binary image that is used for detection. Blobs / colonies are white on a black background
    # detector is the blob detector setup with specific parameters meant for the expected type of blobs
    
    if blackOnWhite == 1:
        # cv2.imshow('thresh_result',cv2.bitwise_not(frame0_bin,frame0_bin,mask = mask)), cv2.waitKey(0)
        find_contour_img = cv2.bitwise_not(frame0_bin,frame0_bin,mask = mask)
    else:
        # cv2.imshow('thresh_result',cv2.bitwise_and(frame0_bin,frame0_bin,mask = mask)), cv2.waitKey(0)
        find_contour_img = cv2.bitwise_and(frame0_bin,frame0_bin,mask = mask)
    

    im2, contours, hierarchy = cv2.findContours(find_contour_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    contour_info.append(contours)
    im_with_contours = cv2.drawContours(frame0_roi, contours, -1, (0,255,0),contour_type)
    # cv2.namedWindow('Contours', cv2.WINDOW_NORMAL)
    # cv2.imshow('Contours', im_with_contours), cv2.waitKey(0)
    # cv2.destroyWindow('Contours')
    contours = sorted(contours, key=cv2.contourArea, reverse = True)

    # The largest contour should be the robot, so only cqare about this one
    cnt = contours[0]
    area = cv2.contourArea(cnt)
    M = cv2.moments(cnt)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    # cv2.circle(im_with_contours, (cX, cY), 7, (255, 255, 255), -1)
    # cv2.imshow("Image", im_with_contours)
    # cv2.waitKey(0)
    temp_position_info = np.array([cX, cY])
    position_info.append(temp_position_info) 
    # loop over the contours. THis is if you cared about multiple contours
    # for cnt in contours:
    #     # c is a new contour that is grabbed from contours during each iteration
    #     area = cv2.contourArea(cnt)
    #     print area
    #     # compute the center of the contour
    #     M = cv2.moments(cnt)
    #     cX = int(M["m10"] / M["m00"])
    #     cY = int(M["m01"] / M["m00"])
     
    #     # draw the contour and center of the shape on the image
    #     cv2.drawContours(im_with_contours, [cnt], -1, (0, 255, 0), 2)
    #     cv2.circle(im_with_contours, (cX, cY), 7, (255, 255, 255), -1)
    #     cv2.putText(im_with_contours, "center", (cX - 20, cY - 20),
    #         cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
     
    #     # show the image
    #     cv2.imshow("Image", im_with_contours)
    #     cv2.waitKey(0)
    return contours, contour_info, position_info
########################################################################################################    
# Create a VideoCapture object. The argument can either be the device index or
# the name of a video file. If one camera is connected pass 0. To select a
# second camera, pass 1, etc.
#cap = cv2.VideoCapture(1)
filename = "SaveToAvi-Uncompressed-14434226-0000"
cap = cv2.VideoCapture("/home/elizabeth/Dropbox/%s.avi" % filename)

# Check if camera opened successfully
if (cap.isOpened()== False): 
  print("Error opening video stream or file")

cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE);
# REad until video is completed
font = cv2.FONT_HERSHEY_SIMPLEX
frame_rate = round(cap.get(cv2.CAP_PROP_FPS),2) # get the frame rate of the video
xdim = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) # get the frame width 
ydim = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # get the frame height
print "Image Width: %d pixels" % xdim
print "Image Height: %d pixels" % ydim
print "Frame Rate: %.2f fps" % frame_rate

# grab the first frame of the video and select region of interest and threshold for processing

cap.set(cv2.CAP_PROP_POS_FRAMES,0);
ret, frame0 = cap.read() # Read the frame
clone_frame0 = frame0.copy() # Copy the frame
frame_no = cap.get(cv2.CAP_PROP_POS_FRAMES)
cv2.putText(frame0,'Frame: %d' % frame_no,(10,50), font,1,(255,255,255),2,cv2.LINE_AA)
cv2.imshow('frame', frame0)
cv2.waitKey(0)



# Select Region of interest for image processing
print "Select Region of Interest for Image Processing.\n Press Escape Upon Selection Completion."
roi_pts = [] # create this as a list first
cv2.namedWindow('Select Image ROI',cv2.WINDOW_NORMAL)
cv2.setMouseCallback('Select Image ROI',selectROI)
while(1):
    cv2.imshow('Select Image ROI',frame0)
    if cv2.waitKey(20) & 0xFF == 27:
        break
cv2.destroyWindow('Select Image ROI')
# print 'ROI Point Selection: %s' % roi_pts

# Add option to save this matrix and load for identical video setups

# Create a black image, a window, and bind the function to the window
mask = np.zeros((ydim,xdim), dtype = np.uint8)
# Convert list into numpy array
roi_pts = np.array(roi_pts, np.int32)
roi_pts = roi_pts.reshape(-1,1,2)
# Crop the image to the specified region of interest - the  background should be black
frame0_roi = crop2roi(frame0,roi_pts,mask)
# cv2.imshow('frame',frame0_roi)
# cv2.waitKey(0)
mask2 = thresh(mask, roi_pts, frame0)
# print "Select Desired Threshold Level for Blob Detection and Press Escape Upon Completion."
# # Select threhold to convert image to binary
# cv2.namedWindow('SelectThreshold', cv2.WINDOW_NORMAL)
# cv2.createTrackbar('BinaryThreshold','SelectThreshold',127, 255, nothing) #Name of trackbar, window, original slider position, maximum slider value, function that updates
# cv2.namedWindow('ResultThreshold',cv2.WINDOW_NORMAL)
# # cv2.moveWindow('ResultThreshold',0,0)
# while(1):
#     cv2.imshow('SelectThreshold',frame0_roi)
#     if cv2.waitKey(20) & 0xFF == 27:
#         break
#     # get current position of trackbar
#     thresh_val = cv2.getTrackbarPos('BinaryThreshold','SelectThreshold')
#     retval1,frame0_bin = cv2.threshold(frame0_roi,thresh_val,255,cv2.THRESH_BINARY)
#     # bin_result is the thresholded image converted to binary. Blobs are white and background is black
#     cv2.imshow('ResultThreshold',frame0_bin)
#     #cv2.waitKey(0)

# cv2.destroyWindow('SelectThreshold')
# cv2.destroyWindow('ResultThreshold')

###########################################################################################
print "Initializing Image Processing..."
# Specify the type of contour
contour_type = 3 # use 3 for edges and -1 for filled
# Set up a detector (default params for now)
blackOnWhite = 0
# Blob info is a master list of all the descriptors of the blobs. Each element of the list corresponds to each frame in sequence (i.e. blob_info[0] is an array of descriptors in frame 1). blob_info[i] is an array of descriptors. Each row corresponds to a different blob. First column is x position, second column is y position, and third column is size of blob.
position_info = [] # initialize empty list
contour_info =[] # initialize empty list to hold contour info

contours, contour_info, position_info = detectContours(frame0_roi,mask2,contour_info,position_info,blackOnWhite)
center = position_info[0]
cv2.circle(clone_frame0, (center[0], center[1]), 7, (0, 255, 0), -1)
cv2.imshow('frame', clone_frame0)
print "Ensure Center of Robot was Detected in First Frame of Video.\n Press Enter to Continue. Re-run program to re-select ROI."
cv2.waitKey(0)

# reset position_info and contour_info arrays
position_info = []
contour_info = []
num_frames = []
time_stamp = []
cap.set(cv2.CAP_PROP_POS_FRAMES,0);

enchilada = raw_input("Do you want to process all video frames? [y/n]: ")

if enchilada.startswith('y'):
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
else:
    frame_count = int(raw_input("Enter the index of the last frame you want to process: "))

save_vid = raw_input("Do you to save the processed video? [y/n]")
if save_vid.startswith('y'):
    fourcc = cv2.VideoWriter_fourcc('F', 'M', 'P', '4')
    out = cv2.VideoWriter('%s_processed.mp4' % filename,fourcc, frame_rate, (xdim,ydim), 1)

i = 0 # set up frame counter
print "Processing Video..."
while(cap.isOpened()):
    time = cap.get(cv2.CAP_PROP_POS_MSEC)/1000 # current position of the video file in seconds
    k = cap.get(cv2.CAP_PROP_POS_FRAMES)
    num_frames.append(k)
    time_stamp.append(round(time,2))

    # Capture frame-by-frame
    ret, frame = cap.read()

    clone_frame = frame.copy() # Copy the frame
    frame_roi = crop2roi(frame,roi_pts,mask)
    mask2 = thresh(mask, roi_pts, frame)
    contours, contour_info, position_info = detectContours(frame_roi,mask2,contour_info,position_info,blackOnWhite)

    center = position_info[int(k)]
    cv2.putText(clone_frame,'Frame: %d' % k,(10,50), font,1,(255,255,255),2,cv2.LINE_AA)
    cv2.putText(clone_frame,'Time: %.2f' % time,(10,100), font,1,(255,255,255),2,cv2.LINE_AA)
    cv2.circle(clone_frame, (center[0], center[1]), 7, (0, 255, 0), -1)

    # Display the resulting frame
    cv2.imshow('frame',clone_frame)
    if save_vid.startswith('y'):
        out.write(clone_frame)

    i = i+1 #increase frame count
    if i == frame_count:
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
print("{0} out of {1} frames were processed.".format(len(num_frames), frame_count))
print "Saving Data..."
K = np.loadtxt('/home/elizabeth/Code/DAQ_Control_Video/Kintrins_cam.txt',delimiter=',')
now = datetime.datetime.now()

f = open("%s.csv" % filename, "wb")
writer = csv.writer(f)
writer.writerows([["Date",now.strftime("%Y/%m/%d")]])
writer.writerows([["Sample",filename]])
writer.writerows([["Frame Rate",frame_rate]])
writer.writerows([["Average Velocity", 0, "pixels/s"]])
writer.writerows([["Average Velocity", 0, "mm/s"]])
writer.writerows([["Camera Matrix",K]])
writer.writerows([["Frame_No", "Time", "px","py"]])
print frame_count
for k in range(frame_count):
    px = position_info[k][0]
    py = position_info[k][1]
    t = time_stamp[k]
    writer.writerows([[k, t, px, py]])
f.close()


# When everything done, release the capture and the 
if save_vid.startswith('y'):
    out.release()
cap.release()
cv2.destroyAllWindows()