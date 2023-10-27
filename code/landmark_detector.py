import argparse
import dlib
import cv2
import os
from imutils import face_utils

# Input arguments
ap = argparse.ArgumentParser()
ap.add_argument("--image", required=True, help="path to input image")
args = vars(ap.parse_args())

filename = args["image"]
out_dir, basename = os.path.split(filename)
name, extension = os.path.splitext(basename)

print(f'Searching facial landmarks for image {filename}')

# initialize dlib's face detector (HOG-based) and then create the facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("code/shape_predictor_68_face_landmarks.dat")

# load the input image and convert it to grayscale
image = cv2.imread(filename)
image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# detect faces in the gray-scale image
print('Detecting faces...')
dets = detector(image_gray, 1)

# check if any faces have been detected
if len(dets) == 0 : 
    print('\033[0;31mWarning! no faces have been detected\033[0m')
    exit()

# initialize variables to keep track of the clearest face found so far
max_sharpness = -1
max_sharpness_shape = None
max_sharpness_rect = None

# loop over the detected faces
for (i, rect) in enumerate(dets):
    # detect the facial landmarks for the face region, 
    # and convert (x, y)-coordinates to a NumPy array
    shape = face_utils.shape_to_np(predictor(image_gray, rect))

    # calculate the sharpness of the current face
    sharpness = cv2.Laplacian(image_gray[rect.top():rect.bottom(), rect.left():rect.right()], cv2.CV_64F).var()

    # if this is the first face or if it's sharper than the previous ones, update the variables
    if sharpness > max_sharpness:
        max_sharpness = sharpness
        max_sharpness_shape = shape
        max_sharpness_rect = rect

# check if any faces have been found
if max_sharpness_shape is None:
    print('\033[0;31mWarning! no faces have been detected\033[0m')
    exit()

# draw the bounding box and face number for the clearest face
green = (0, 255, 0) 
(x, y, w, h) = face_utils.rect_to_bb(max_sharpness_rect)
cv2.rectangle(image, (x, y), (x + w, y + h), green, 2)
cv2.putText(image, "Clearest Face", (x - 10, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, green, 2)

# write the landmarks for the clearest face to a file
landmarks_file = out_dir + '/' + name + '.txt'      
f = open(landmarks_file, 'wb')
for (x, y) in max_sharpness_shape:
    f.write(str(x).encode("utf-8") + b' ' + str(y).encode("utf-8") + b'\n')
f.close()
print(f'\033[0;32mLandmarks exported to {landmarks_file}\033[0m')    

# show the output image with the face detections + facial landmarks
cv2.imwrite(out_dir + '/' + name + '_landmarks.jpg', image)

print(f'\033[0;32mImage with landmarks exported to {out_dir}/{name}_landmarks.jpg\033[0m')
print('\033[0;37;42mDetected Done!\033[0m')