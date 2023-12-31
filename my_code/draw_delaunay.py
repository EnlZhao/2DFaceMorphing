import cv2
import random
import argparse
import os
import numpy as np
from faceMorph import readPoints

def in_rectangle(rect, point) :
    """
    Check if a point is inside a rectangle
    """
    if point[0] < rect[0] :
        return False
    elif point[1] < rect[1] :
        return False
    elif point[0] > rect[2] :
        return False
    elif point[1] > rect[3] :
        return False
    return True

def draw_point(img, point, color ) :
    """
    Draws a point on an image.
    """
    cv2.circle(img, point, 2, color, cv2.FILLED, cv2.LINE_AA, 0)

# Draw delaunay triangles
def draw_delaunay(img, subdiv, delaunay_color) :

    triangleList = subdiv.getTriangleList()
    size = img.shape
    r = (0, 0, size[1], size[0])

    for t in triangleList :
        pt1 = (int(t[0]), int(t[1]))
        pt2 = (int(t[2]), int(t[3]))
        pt3 = (int(t[4]), int(t[5]))
        
        if in_rectangle(r, pt1) and in_rectangle(r, pt2) and in_rectangle(r, pt3) :
            cv2.line(img, pt1, pt2, delaunay_color, 1, cv2.LINE_AA, 0)
            cv2.line(img, pt2, pt3, delaunay_color, 1, cv2.LINE_AA, 0)
            cv2.line(img, pt3, pt1, delaunay_color, 1, cv2.LINE_AA, 0)

def draw_voronoi(img, subdiv) :
    """
    Draw voronoi diagram
    """
    (facets, centers) = subdiv.getVoronoiFacetList([])

    for i in range(0, len(facets)):
        ifacet_arr = []
        for f in facets[i] :
            ifacet_arr.append(f)
        
        ifacet = np.array(ifacet_arr, np.int64)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        cv2.fillConvexPoly(img, ifacet, color, cv2.LINE_AA, 0)
        ifacets = np.array([ifacet])
        cv2.polylines(img, ifacets, True, (0, 0, 0), 1, cv2.LINE_AA, 0)
        cv2.circle(img, (int(centers[i][0]), int(centers[i][1])), 3, 
                   (0, 0, 0), cv2.FILLED, cv2.LINE_AA, 0)

if __name__ == '__main__':
    # Input arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, help="path to input image")
    args = vars(ap.parse_args())
    filename = args["image"]
    out_dir, basename = os.path.split(filename)
    name, extension = os.path.splitext(basename)
    
    # Define colors for drawing.
    delaunay_color = (255,255,255)
    points_color = (0, 0, 255)

    img = cv2.imread(filename)
    
    # Rectangle to be used with Subdiv2D
    rect = (0, 0, img.shape[1], img.shape[0])
    subdiv = cv2.Subdiv2D(rect)
    
    # Read in the points from a text file and insert them into a subdiv
    points = readPoints(out_dir + '/' + name + '.txt')
    for p in points :
        subdiv.insert(p)

    # Draw delaunay triangles
    draw_delaunay(img, subdiv, delaunay_color)

    # Draw points
    for p in points :
        draw_point(img, p, points_color)

    # Allocate space for voronoi Diagram
    img_voronoi = np.zeros(img.shape, dtype = img.dtype)

    # Draw voronoi diagram
    draw_voronoi(img_voronoi,subdiv)

    # Save results
    cv2.imwrite(out_dir + '/' + name + '-delaunay.jpg', img)
    cv2.imwrite(out_dir + '/' + name + '-voronoi.jpg', img_voronoi)

    print('\033[0;32mDraw Delaunay Triangles Done!\033[0m')