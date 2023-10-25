#!/bin/bash
#
# This script installs several dependencies to make face morphing work.
# Basically dlib for landmark detection, opencv for processing images,
# some python tools and ffmpeg for generating video from raw frames.
#
# Troubleshooting:
# If your bash does not find brew, try to launch them from
# /usr/local/bin/brew.

brew install ffmpeg
brew install python
brew install python3
brew install cmake
brew install boost
brew install boost-python3

pip install numpy
pip install scipy
pip install scikit-image
pip install matplotlib
pip install imutils
pip install opencv-python
pip install dlib