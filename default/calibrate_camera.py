import numpy as np
import cv2 as cv
import glob

WIDTH = 6
HEIGHT = 8
 
# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
 
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((WIDTH*HEIGHT,3), np.float32)
objp[:,:2] = np.mgrid[0:6,0:8].T.reshape(-1,2)
 
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.


images = glob.glob('*.jpg')
 
for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (WIDTH,HEIGHT), None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        print(f"Good (File: {fname})")
    else:
        print(f"Bad (File: {fname})")
        continue

    corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
    imgpoints.append(corners2)

    # Draw and display the corners
    cv.drawChessboardCorners(img, (WIDTH,HEIGHT), corners2, ret)
    cv.imshow('img', img)
    cv.waitKey(500)

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None, None, None, 0, criteria) # type: ignore

print(f"{mtx}")
with open("intrinsics.txt", "w") as file:
    file.write(f"{mtx[0][0]}, {mtx[0][2]}, {mtx[1][1]}, {mtx[1][2]}")
# [fx, 0, cx]
# [0, fy, cy]
# [0, 0, 1]
 
cv.destroyAllWindows()