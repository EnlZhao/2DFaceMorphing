# Face Morphing

![](./example/harry-hermione.gif)

This code generates a morphing effect between two faces.		
1. Facial landmarks recognition in both faces using [Dlib](http://dlib.net).
2. Triangular [Delaunay](https://en.wikipedia.org/wiki/Delaunay_triangulation) segmentation.	
3. [Affine transformation](https://en.wikipedia.org/wiki/Affine_transformation) between the Delaunay triangles of both faces.
4. [Alpha blending](https://en.wikipedia.org/wiki/Alpha_compositing#Alpha_blending) on the paired triangles.	
> Steps 3 and 4 are iterated for different values of alpha to generate a bunch of morphing frames.		
5. After that, frames are converted into a video file using [FFmpeg](https://ffmpeg.org).

## Attribution

- This project is a modification of the code originally posted in this [blog post](https://www.learnopencv.com/face-morph-using-opencv-cpp-python/). 

- Note that unlike the original code, only the corners and half way points are added to the facial keypoints.	
- The neck and the ears points manually added in the original code have been omitted to make it completely automatic.

## Installation dependencies

- Cause this project is running originally on MacOS, the following script installs the dependencies for MacOS.

```bash
$ ./install_morphing_dependencies_macos.sh`
```

> You can also run the project on Ubuntu, but you will need to install the dependencies manually.
> If you are using Ubuntu, you can follow the instructions below.(It might not work totally, please refer to the [blog](https://www.learnopencv.com/install-dlib-on-ubuntu) for more details.)

```bash
sudo apt-get install build-essential cmake pkg-config
sudo apt-get install libx11-dev libatlas-base-dev
sudo apt-get install libgtk-3-dev libboost-python-dev
sudo apt-get install python-dev python-pip python3-dev python3-pip
sudo -H pip2 install -U pip numpy
sudo -H pip3 install -U pip numpy
pip install imutils
pip install dlib
```

## Morphing between 2 images

You can run the script `morphing.sh` to generate a video file with the morphing effect between two images.

```bash
$./run_morphing_with_images.sh <image1> <image2> <framerate> <duration_milis> [align]
```
- `image1`: initial image.	
- `image2`: final image.	
- `framerate`: frame-rate in fps.	
- `duration`: morphing duration in miliseconds.
- `align` [option]: if set 1, the images will be aligned before morphing. Default is 0.

> More details about parameters can be found in the script `morphing.sh` or source code.

### Example

- Unaligned version:

```bash
$./morphing.sh example/harry.jpg example/hermione.jpg 40 3000
```
- Aligned version:

![](example/harry-hermione-aligned.gif)

```bash
$./morphing.sh example/harry.jpg example/hermione.jpg 40 3000 1
```

## Limitations

- Although *Dlib* is quite robust in most cases, it has its own limitations for detecting facial landmarks.	
- In case that the nose and eyes are not enough visible, face detection may fail.
- It also will fail on detecting non-real faces for instance cartoons, even if they have eyes, nose and mouth.

## References

- [Face Morph Using OpenCV — C++ / Python](https://www.learnopencv.com/face-morph-using-opencv-cpp-python/)