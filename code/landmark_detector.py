from imutils import face_utils
import argparse
import dlib
import cv2
import os

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("--image", required=True, help="path to input image")
args = vars(ap.parse_args())

filename = args["image"]
out_dir, basename = os.path.split(filename)
name, extension = os.path.splitext(basename)
print('Searching facial landmarks for image ' + filename)
# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("code/shape_predictor_68_face_landmarks.dat")

# load the input image, resize it, and convert it to grayscale
image = cv2.imread(filename)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# detect faces in the grayscale image
print('Detecting faces...')
rects = detector(gray, 1)

# loop over the face detections
for (i, rect) in enumerate(rects):

    print('Recovering face parts for person #' + str(i))
    # determine the facial landmarks for the face region, then
    # convert the facial landmark (x, y)-coordinates to a NumPy
    # array
    shape = predictor(gray, rect)
    shape = face_utils.shape_to_np(shape)

    # convert dlib's rectangle to a OpenCV-style bounding box
    # [i.e., (x, y, w, h)], then draw the face bounding box
    (x, y, w, h) = face_utils.rect_to_bb(rect)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # show the face number
    cv2.putText(image, "Face #{}".format(i + 1), (x - 10, y - 10),
    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # loop over the (x, y)-coordinates for the facial landmarks
    # and draw them on the image
    for (x, y) in shape:
        cv2.circle(image, (x, y), 1, (0, 0, 255), -1)

    # loop over the (x, y)-coordinates for the facial landmarks
    # and write them on a file
    landmarks_file = out_dir + '/' + name + '.txt'      # overwrites landmarks for images with multiple faces
    f = open(landmarks_file, 'wb')
    f.truncate(0)                                       # cleaning
    for (x, y) in shape:
        f.write(str(x).encode("utf-8") + b' ' + str(y).encode("utf-8") + b'\n')
    
    f.close()
    print('\033[0;32mLandmarks exported to ' + landmarks_file)    


cv2.imwrite(out_dir + '/' + name + '_landmarks.jpg', image)

if len(rects) == 0 : 
    print("\033[0;31mWarning! no faces have been detected\033[0m")
else : 
    print('\033[0;42mDetected Done!\033[0m')

