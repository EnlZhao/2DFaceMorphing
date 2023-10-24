import cv2
import numpy as np
import random
import argparse
import os

# Check if a point is inside a rectangle
def rect_contains(rect, point) :

    if point[0] < rect[0] :
        return False
    elif point[1] < rect[1] :
        return False
    elif point[0] > rect[2] :
        return False
    elif point[1] > rect[3] :
        return False
    return True

# Draw a point
def draw_point(img, p, color ) :
    cv2.circle( img, p, 2, color, cv2.FILLED, cv2.LINE_AA, 0 )


# Draw delaunay triangles
def draw_delaunay(img, subdiv, delaunay_color ) :

    triangleList = subdiv.getTriangleList();
    size = img.shape
    r = (0, 0, size[1], size[0])

    for t in triangleList :
        
        pt1 = (t[0], t[1])
        pt2 = (t[2], t[3])
        pt3 = (t[4], t[5])
        
        if rect_contains(r, pt1) and rect_contains(r, pt2) and rect_contains(r, pt3) :
        
            cv2.line(img, pt1, pt2, delaunay_color, 1, cv2.LINE_AA, 0)
            cv2.line(img, pt2, pt3, delaunay_color, 1, cv2.LINE_AA, 0)
            cv2.line(img, pt3, pt1, delaunay_color, 1, cv2.LINE_AA, 0)

# Draw voronoi diagram
def draw_voronoi(img, subdiv) :

    ( facets, centers) = subdiv.getVoronoiFacetList([])

    # for i in xrange(0,len(facets)) :
    for i in range(0, len(facets)):
        ifacet_arr = []
        for f in facets[i] :
            ifacet_arr.append(f)
        
        ifacet = np.array(ifacet_arr, np.int)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        cv2.fillConvexPoly(img, ifacet, color, cv2.LINE_AA, 0);
        ifacets = np.array([ifacet])
        cv2.polylines(img, ifacets, True, (0, 0, 0), 1, cv2.LINE_AA, 0)
        cv2.circle(img, (centers[i][0], centers[i][1]), 3, (0, 0, 0), cv2.FILLED, cv2.LINE_AA, 0)


if __name__ == '__main__':

    # Input arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="path to input image")
    args = vars(ap.parse_args())
    filename = args["image"]
    out_dir, basename = os.path.split(filename)
    name, extension = os.path.splitext(basename)

    # Define window names
    win_delaunay = "Delaunay Triangulation"
    win_voronoi = "Voronoi Diagram"

    # Turn on animation while drawing triangles
    animate = False
    
    # Define colors for drawing.
    delaunay_color = (255,255,255)
    points_color = (0, 0, 255)

    # Read in the image.
    img = cv2.imread(filename);
    
    # Keep a copy around
    img_orig = img.copy();
    
    # Rectangle to be used with Subdiv2D
    size = img.shape
    rect = (0, 0, size[1], size[0])
    
    # Create an instance of Subdiv2D
    subdiv = cv2.Subdiv2D(rect);

    # Create an array of points.
    points = [];
    
    # Read in the points from a text file
    points_filename = out_dir + '/' + name + '.txt'
    with open(points_filename) as file :
        for line in file :
            x, y = line.split()
            points.append((int(x), int(y)))

    # Insert points into subdiv
    for p in points :
        subdiv.insert(p)
        
        # Show animation
        if animate :
            img_copy = img_orig.copy()
            # Draw delaunay triangles
            draw_delaunay( img_copy, subdiv, (255, 255, 255) );
            cv2.imshow(win_delaunay, img_copy)
            cv2.waitKey(100)

    # Draw delaunay triangles
    draw_delaunay( img, subdiv, (255, 255, 255) );

    # Draw points
    for p in points :
        draw_point(img, p, (0,0,255))

    # Saves delaunay points
    delaunay_file = out_dir + '/' + name + '_triangles.txt'
    f = open(delaunay_file, 'wb')
    f.truncate(0)
    triangleList = subdiv.getTriangleList();

    for t in triangleList :
        if rect_contains(rect, (t[0], t[1])): 
            f.write(str(int(t[0])).encode("utf-8") + b' ' + str(int(t[1])).encode("utf-8") + b'\n')
        if rect_contains(rect, (t[2], t[3])): 
            f.write(str(int(t[2])).encode("utf-8") + b' ' + str(int(t[3])).encode("utf-8") + b'\n')
        if rect_contains(rect, (t[4], t[5])): 
            f.write(str(int(t[4])).encode("utf-8") + b' ' + str(int(t[5])).encode("utf-8") + b'\n')

    # Allocate space for voronoi Diagram
    img_voronoi = np.zeros(img.shape, dtype = img.dtype)

    # Draw voronoi diagram
    draw_voronoi(img_voronoi,subdiv)

    # Show results
    cv2.imshow(win_delaunay,img)
    cv2.imshow(win_voronoi,img_voronoi)
    #cv2.waitKey(0)

    # Save results
    cv2.imwrite(out_dir + '/' + name + '_delaunay.jpg', img)
    cv2.imwrite(out_dir + '/' + name + '_voronoi.jpg', img_voronoi)
    print('\033[0;32mresults exported to ' + points_filename)
    print('\033[0;42mBuild Delaunay Triangles Done!\033[0m')





