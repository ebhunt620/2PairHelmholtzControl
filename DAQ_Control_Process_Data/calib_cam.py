from os import system
import time
import os
import shutil, glob
import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2

# Elizabeth E. Hunter
# ebeattie (at) seas (dot) upenn (dot) edu
# University of Pennsylvania
# This program outputs a 3x3 camera calibration matrix.

# squareSize of physical checkerboard in mm
# squareSize = 3 # small board
squareSize = 36.4 # big board

print "Press 1 to Begin Camera Calibration with Capture of 10 images. Move camera to different positions while keeping the checkerboard flat on the table. If you do not want to capture images, press 0"
cv2.waitKey(0)
do_calib = int(raw_input("Choose 0 or 1: "))
# Take a series of at least 10 images
nimgs = 10
dst_root = "/home/elizabeth/Code/DAQ_Control_Video/cam_calib_imgs"
if do_calib == 1:
	src_root = "/home/elizabeth/Code/DAQ_Control_Video"
	for x in xrange(nimgs):
		print "Capturing Image %d/%d" % (x+1, nimgs)
		dst_filename = "cam_cal_img_%d.jpg" % (x)

		# Capture Image of Checkerboard Pattern on camera
		system("~/spinnaker_1_0_0_295_amd64/bin/Acquisition_v2")
		src_filename = "Acquisition-14434226-0.jpg"
		os.rename(src_filename, dst_filename)
		src_dir = os.path.join(src_root, dst_filename)
		dst_dir = os.path.join(dst_root, dst_filename)
		shutil.move(src_dir, dst_dir)
		print "Saving Image as %s. Press Any Key to Take the next picture." % dst_filename
		c = int(raw_input("Press 1 to Continue and 0 to Quit: "))
		if c == 1:
			continue
		elif c == 0:
			break
	else:
		print "Finished capturing %d images" % (nimgs)


# Size of checkerboard pattern in images
# patternSize = (9,7) # small board
patternSize = (9,6) # big board 

# prepare physical checkerboard object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*9,3), np.float32)

objp[:,:2] = np.mgrid[0:9*squareSize:squareSize, 0:6*squareSize:squareSize].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
h, w = 0, 0
images = glob.glob(os.path.join(dst_root,'*.jpg'))

for fname in images:
	img = cv2.imread(fname)
	h, w = img.shape[:2]
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
	ret, corners = cv2.findChessboardCorners(gray, patternSize, None)

    # If found, add object points, image points (after refining them)
	if ret == True:
		# termination criteria
		criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
		corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
		imgpoints.append(corners2)
		objpoints.append(objp)
		# Draw and display the corners
		img = cv2.drawChessboardCorners(img, patternSize, corners2,ret)
		cv2.imshow('img',img)
		cv2.waitKey(500)
	if not ret:
		print "chessboard not found in image %s" %fname
	

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
# Save Transformations to file
np.savetxt('Kintrins_cam.txt',mtx,delimiter=',')
cv2.destroyAllWindows()

print "RMS:", ret
print "camera matrix:\n", mtx
print "distortion coefficients: ",dist.ravel() 
# Calculate reprojection error
mean_error = 0
tot_error = 0

fig_reproj = plt.figure('Reprojection')
for i in xrange(len(objpoints)):

    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
    tot_error = tot_error + error
    temp_imgpoints = imgpoints[i].reshape(-1,2)
    temp_imgpoints2 = imgpoints2.reshape(-1,2)
    img = cv2.imread(images[i])
    plt.imshow(img, cmap = 'gray'),plt.title('Reprojection')
    plt.plot(temp_imgpoints[:,0],temp_imgpoints[:,1],'ro')
    plt.plot(temp_imgpoints2[:,0],temp_imgpoints2[:,1],'go')
    plt.show()


mean_error = tot_error / len(objpoints)
print "Mean reprojection error is: %d pixels", (mean_error)