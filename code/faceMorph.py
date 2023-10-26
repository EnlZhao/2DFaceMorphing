import argparse
import numpy as np
import cv2
import os

def build_delaunay(image, points) :
    """
    Gets delaunay 2D segmentation and return a list with the the triangles' indexes
    """
    rect = (0, 0, image.shape[1], image.shape[0])
    subdiv = cv2.Subdiv2D(rect)
    for point in points :
        subdiv.insert(point)

    triangleList = subdiv.getTriangleList()
    triangles = []
    for p in triangleList :
        vertexes = [0, 0, 0]
        for v in range(3) :
            vv = v * 2
            for i in range(len(points)) :
                if p[vv] == points[i][0] and p[vv+1] == points[i][1] :
                    vertexes[v] = i

        triangles.append(vertexes)

    return triangles

def readPoints(src_path) :
    """
    [Official code]:
    Read points from text file
    """
    face_points = []
    # Read face_points
    with open(src_path) as file :
        for lines in file :
            x, y = lines.split()
            face_points.append((int(x), int(y)))

    return face_points

def addAdditionalPoints(face_points, size) :
    """
    Append 8 additional points: corners and half way points to the face_points list
    """

    height = size[0]
    width = size[1]
    middle_height = height // 2
    middle_width = width // 2
    # Corners
    face_points.append((0, 0))
    face_points.append((0, height - 1))
    face_points.append((width - 1, 0))
    face_points.append((width - 1, height - 1))
    # Half way points
    face_points.append((0, middle_height))
    face_points.append((middle_width, 0))
    face_points.append((width - 1, middle_height))
    face_points.append((middle_width, height - 1))

    return face_points

def applyAffineTransform(src, src_Triangle, dst_Triangle, size) :
    """
    [Official code]:
    Apply affine transform calculated using src_Triangle and dst_Triangle to src and output an image of size.
    """
    # Given a pair of triangles, find the affine transform.
    warpMat = cv2.getAffineTransform(np.float32(src_Triangle), np.float32(dst_Triangle))
    
    # Apply the Affine Transform just found to the src image
    dst = cv2.warpAffine(src, warpMat, (size[0], size[1]), None, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101 )

    return dst

def morphTriangle(img1, img2, img, triangle1, triangle2, triangle, alpha) :
    """
    [Official code]:
    Wraps and alpha blends triangular regions from img1 and img2 to img
    """
    # Find bounding rectangle for each triangle
    rectangle1 = cv2.boundingRect(np.float32([triangle1]))
    rectangle2 = cv2.boundingRect(np.float32([triangle2]))
    rectangle = cv2.boundingRect(np.float32([triangle]))

    # Offset points by left top corner of the respective rectangles
    t1Rect, t2Rect, tRect = [], [], []

    for i in range(0, 3):
        tRect.append(((triangle[i][0] - rectangle[0]),(triangle[i][1] - rectangle[1])))
        t1Rect.append(((triangle1[i][0] - rectangle1[0]),(triangle1[i][1] - rectangle1[1])))
        t2Rect.append(((triangle2[i][0] - rectangle2[0]),(triangle2[i][1] - rectangle2[1])))

    # Get mask by filling triangle
    mask = np.zeros((rectangle[3], rectangle[2], 3), dtype = np.float32)
    cv2.fillConvexPoly(mask, np.int32(tRect), (1.0, 1.0, 1.0), 16, 0);

    # Apply warpImage to small rectangular patches
    img1Rect = img1[rectangle1[1]:rectangle1[1] + rectangle1[3], rectangle1[0]:rectangle1[0] + rectangle1[2]]
    img2Rect = img2[rectangle2[1]:rectangle2[1] + rectangle2[3], rectangle2[0]:rectangle2[0] + rectangle2[2]]

    size = (rectangle[2], rectangle[3])
    warpImage1 = applyAffineTransform(img1Rect, t1Rect, tRect, size)
    warpImage2 = applyAffineTransform(img2Rect, t2Rect, tRect, size)

    # Alpha blend rectangular patches
    imgRect = (1.0 - alpha) * warpImage1 + alpha * warpImage2

    # Copy triangular region of the rectangular patch to the output image
    img[rectangle[1]:rectangle[1]+rectangle[3], rectangle[0]:rectangle[0]+rectangle[2]] = img[rectangle[1]:rectangle[1]+rectangle[3], rectangle[0]:rectangle[0]+rectangle[2]] * ( 1 - mask ) + imgRect * mask

if __name__ == '__main__' :
    # Input arguments
    ap = argparse.ArgumentParser(prog='faceMorph')
    ap.add_argument("--image1", required=True, help="path to input image 1")
    ap.add_argument("--image2", required=True, help="path to input image 2")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--nframes", metavar="[> 0]", help="desired number of morphing frames")
    group.add_argument("--alpha", metavar="[0-100]", type=int, choices=range(0, 101), help="desired alpha morphing value")
    args = vars(ap.parse_args())

    # Output directory
    filename1 = args["image1"]
    filename2 = args["image2"]
    out_dir1, basename1 = os.path.split(filename1)
    out_dir2, basename2 = os.path.split(filename2)
    img_name1, extension1 = os.path.splitext(basename1)
    img_name2, extension2 = os.path.splitext(basename2)

    # Read images and Convert to float data type
    img1 = np.float32(cv2.imread(filename1))
    img2 = np.float32(cv2.imread(filename2))

    # Read array of corresponding points and Append 8 additional points
    face1_points = addAdditionalPoints(readPoints(out_dir1 + '/' + img_name1 + '.txt'), 
                                       img1.shape)
    face2_points = addAdditionalPoints(readPoints(out_dir2 + '/' + img_name2 + '.txt'), 
                                       img2.shape)

    # Delaunay points
    delaunay_group = build_delaunay(img1, face1_points)

    # Alpha values --- Number of intermediate morphing frames
    alpha_values = np.linspace(0, 100, int(args["nframes"]))

    # Main loop
    for (f, a) in enumerate(alpha_values) :
        alpha = float(a) / 100
        points = []         

        # Compute weighted average point coordinates
        for i in range(0, len(face1_points)):
            x = (1 - alpha) * face1_points[i][0] + alpha * face2_points[i][0]
            y = (1 - alpha) * face1_points[i][1] + alpha * face2_points[i][1]
            points.append((x, y))

        # Allocate space for final output
        imgMorph = np.zeros(img1.shape, dtype = img1.dtype)

        for vertex1, vertex2, vertex3 in delaunay_group :
            triangle1 = [face1_points[vertex1], face1_points[vertex2], face1_points[vertex3]]
            triangle2 = [face2_points[vertex1], face2_points[vertex2], face2_points[vertex3]]
            triangle  = [points[vertex1], points[vertex2], points[vertex3]]

            # Morph one triangle at a time.
            morphTriangle(img1, img2, imgMorph, triangle1, triangle2, triangle, alpha)

        # Save morphing frame
        index = str(f).zfill(4)

        cv2.imwrite( out_dir1 + '/morph-' + img_name1 + '-' + img_name2 + '-' + index + '.png', np.uint8(imgMorph) )

    print('\033[0;32mMorphing results exported in ' + out_dir1)
    print('\033[0;42mFace morphing Done!\033[0m')