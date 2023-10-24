import argparse
import numpy as np
import cv2
import sys
import os


def readPoints(src_path) :
    """
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
    h = size[0]
    w = size[1]
    h2 = int(size[0]/2)
    w2 = int(size[1]/2)

    face_points.append( (0    , 0    ) )
    face_points.append( (0    , h - 1) )
    face_points.append( (w - 1, 0    ) )
    face_points.append( (w - 1, h - 1) )

    face_points.append( (0    , h2   ) )
    face_points.append( (w2   , 0    ) )
    face_points.append( (w - 1, h2   ) )
    face_points.append( (w2   , h - 1) )

    return face_points

def applyAffineTransform(src, srcTriangle, dstTriangle, size) :
    """
    Apply affine transform calculated using srcTriangle and dstTriangle to src and output an image of size.
    """
    # Given a pair of triangles, find the affine transform.
    warpMat = cv2.getAffineTransform( np.float32(srcTriangle), np.float32(dstTriangle) )
    
    # Apply the Affine Transform just found to the src image
    dst = cv2.warpAffine(src, warpMat, (size[0], size[1]), None, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101 )

    return dst


def morphTriangle(img1, img2, img, t1, t2, t, alpha) :
    """
    Wraps and alpha blends triangular regions from img1 and img2 to img
    """
    # Find bounding rectangle for each triangle
    r1 = cv2.boundingRect(np.float32([t1]))
    r2 = cv2.boundingRect(np.float32([t2]))
    r = cv2.boundingRect(np.float32([t]))


    # Offset points by left top corner of the respective rectangles
    t1Rect = []
    t2Rect = []
    tRect = []

    for i in range(0, 3):
        tRect.append(((t[i][0] - r[0]),(t[i][1] - r[1])))
        t1Rect.append(((t1[i][0] - r1[0]),(t1[i][1] - r1[1])))
        t2Rect.append(((t2[i][0] - r2[0]),(t2[i][1] - r2[1])))


    # Get mask by filling triangle
    mask = np.zeros((r[3], r[2], 3), dtype = np.float32)
    cv2.fillConvexPoly(mask, np.int32(tRect), (1.0, 1.0, 1.0), 16, 0);

    # Apply warpImage to small rectangular patches
    img1Rect = img1[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]]
    img2Rect = img2[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]]

    size = (r[2], r[3])
    warpImage1 = applyAffineTransform(img1Rect, t1Rect, tRect, size)
    warpImage2 = applyAffineTransform(img2Rect, t2Rect, tRect, size)

    # Alpha blend rectangular patches
    imgRect = (1.0 - alpha) * warpImage1 + alpha * warpImage2

    # Copy triangular region of the rectangular patch to the output image
    img[r[1]:r[1]+r[3], r[0]:r[0]+r[2]] = img[r[1]:r[1]+r[3], r[0]:r[0]+r[2]] * ( 1 - mask ) + imgRect * mask

def build_delaunay(image, points) :
    """
    Gets delaunay 2D segmentation and return a list with the the triangles' indexes
    """
    rect = (0, 0, image.shape[1], image.shape[0])
    subdiv = cv2.Subdiv2D(rect);
    for p in points :
        subdiv.insert( p )

    triangleList = subdiv.getTriangleList();
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
    name1, extension1 = os.path.splitext(basename1)
    name2, extension2 = os.path.splitext(basename2)

    # Read images
    img1 = cv2.imread(filename1)
    img2 = cv2.imread(filename2)
    
    # Convert Mat to float data type
    img1 = np.float32(img1)
    img2 = np.float32(img2)

    # Read array of corresponding points and Append 8 additional points
    points = []
    face_points1 = addAdditionalPoints(readPoints(out_dir1 + '/' + name1 + '.txt'), 
                                       img1.shape)
    face_points2 = addAdditionalPoints(readPoints(out_dir2 + '/' + name2 + '.txt'), 
                                       img2.shape)

    # Delaunay points
    delaunay = build_delaunay(img1, face_points1)

    # Alpha values
    alpha_values = []

    if args["nframes"] :
        # Number of intermediate frames (morphing frames)
        alpha_values = np.linspace(0, 100, int(args["nframes"]))

    else: 
        # Single alpha morph blending
        alpha_values = [ float(args["alpha"]) ]

    # Main loop
    for (f, a) in enumerate(alpha_values) :

        alpha = float(a) / 100
        
        points = []         

        # Compute weighted average point coordinates
        for i in range(0, len(face_points1)):
            x = ( 1 - alpha ) * face_points1[i][0] + alpha * face_points2[i][0]
            y = ( 1 - alpha ) * face_points1[i][1] + alpha * face_points2[i][1]
            points.append((x,y))

        # Allocate space for final output
        imgMorph = np.zeros(img1.shape, dtype = img1.dtype)

        for v1, v2, v3 in delaunay :
            t1 = [face_points1[v1], face_points1[v2], face_points1[v3]]
            t2 = [face_points2[v1], face_points2[v2], face_points2[v3]]
            t  = [ points[v1],  points[v2],  points[v3]]

            # Morph one triangle at a time.
            morphTriangle(img1, img2, imgMorph, t1, t2, t, alpha)

        # Save morphing frame
        index = []
        if args["nframes"] :
            index = str(f).zfill(4)
        else : index = 'a' + str(int(a)).zfill(4)

        cv2.imwrite( out_dir1 + '/morph-' + name1 + '-' + name2 + '-' + index + '.png', np.uint8(imgMorph) )

    print('\033[1;32mMorphing results exported in ' + out_dir1)
    print('\033[1;42mFace morphing Done!\033[0m')
