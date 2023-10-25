# Face Morphing

![](./example/harry-hermione.gif)

This code generates a morphing effect between two faces.		
1. Facial landmarks recognition in both faces ([Dlib](http://dlib.net)).	
2. Triangular [Delaunay](https://en.wikipedia.org/wiki/Delaunay_triangulation) segmentation.	
3. [Affine transformation](https://en.wikipedia.org/wiki/Affine_transformation) between the Delaunay triangles of both faces.
4. [Alpha blending](https://en.wikipedia.org/wiki/Alpha_compositing#Alpha_blending) on the paired triangles with a given transparency.	

Steps 3 and 4 are iterated for different values of alpha to generate a bunch of morphing frames.		
After that, frames are converted into a video file.	

## Attribution

This code is a modification of the code originally posted in this [blog post](https://www.learnopencv.com/face-morph-using-opencv-cpp-python/). For more details about this code [Face Morph Using OpenCV — C++ / Python](https://www.learnopencv.com/face-morph-using-opencv-cpp-python/).

Note that unlike the original code, only the corners and half way points are added to the facial keypoints.	
The neck and the ears points manually added in the original code have been omitted to make it completely automatic.

## Installation dependencies for macOS

```bash
$ ./install_morphing_dependencies_macos.sh`
```

## How to morph between 2 images

The following script runs the entire pipeline.

```bash
$./run_morphing_with_images.sh <image1> <image2> <framerate> <duration_milis>
```

- `image1`: initial image.	
- `image2`: final image.	
- `framerate`: frame-rate in fps.	
- `duration`: morphing duration in miliseconds.

### Example

```bash
$./morphing.sh example/harry.jpg example/hermione.jpg 30 2000
```

## Limitations

- Although *Dlib* is quite robust in most cases, it has its own limitations for detecting facial landmarks.	
- In case that the nose and eyes are not enough visible, face detection may fail.
- It also will fail on detecting non-real faces for instance cartoons, even if they have eyes, nose and mouth.

## References

- [Face Morph Using OpenCV — C++ / Python](https://www.learnopencv.com/face-morph-using-opencv-cpp-python/)
    - [Source code](https://github.com/spmallick/learnopencv/tree/master)