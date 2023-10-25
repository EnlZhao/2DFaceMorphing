#!/bin/bash

usageHint()
{
	echo "Usage: $ ./build.sh <path to image1(str)> <path to image2(str)> <fps(int)> <duration_milis(int)> [align(1 represents open face alignment)]"
}

if [ "$1" == "" ] || [ "$2" == "" ] || [ "$3" == "" ] || [ "$4" == "" ]; then
	usageHint
	exit
fi

if [ ! -e "$1" ] || [ ! -e "$2" ]; then
    echo -e "\033[1;41mERROR! Image not found\033[0m"
	usageHint
	exit
fi

img1=$1
img2=$2
fps=$3
duration=$4
frames=$(($fps * $duration / 1000))
align=$5 # default 0

if [ $frames -eq 0 ]; then
    echo -e "\033[1;41mWarning! frames number set to 0. You might set fps or duration to 0.\033[0m"
	usageHint
	exit
fi

bold=$(tput bold)
normal=$(tput sgr0)

filename=$(basename -- "$1")
filename1="${filename%.*}"
filename=$(basename -- "$2")
filename2="${filename%.*}"
path="${1%/*}"

if [[ $align -eq 1 ]]; then
    python code/landmark_detector.py --image $img1
    python code/landmark_detector.py --image $img2
    echo "${bold}Aligning images${normal}"
    python code/align_images.py --image $img1
    python code/align_images.py --image $img2
    # rm $path/$filename1.txt $path/$filename2.txt
    img1=$path/aligned-$filename1.png
    img2=$path/aligned-$filename2.png
    filename1="aligned-$filename1"
    filename2="aligned-$filename2"
else
    echo "${bold}Skipping image alignment${normal}"
fi

echo "${bold}Generating facial landmarks${normal}"
python code/landmark_detector.py --image $img1
python code/landmark_detector.py --image $img2

echo "${bold}Creating morphing frames${normal}"
python code/faceMorph.py --image1 $img1 --image2 $img2 --nframes $frames

echo "${bold}Generating video file${normal}"
ffmpeg -framerate $fps -r $fps -start_number 0 -i $path/morph-$filename1-$filename2-%04d.png -b:v 10M -pix_fmt yuv420p -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" $path/$filename1-$filename2.mp4 -y

echo -e "\033[1;42mFace morphing finished!\033[0m"
echo -e "\033[1;32mCheckout morphing results in $path/$filename1-$filename2.mp4\033[0m"