import os
import bz2
import argparse
from face_alignment import image_align
from align_landmarks_detector import LandmarksDetector

def unpack_bz2(src_path):
    data = bz2.BZ2File(src_path).read()
    dst_path = src_path[:-4]
    with open(dst_path, 'wb') as fp:
        fp.write(data)
    return dst_path


if __name__ == "__main__":
    """
    Extracts and aligns all faces from images using DLib and a function from original FFHQ dataset preparation step
    python align_images.py /raw_images /aligned_images
    """
    parser = argparse.ArgumentParser(description='Align faces from input images', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('origin_dir', help='Directory with images for face alignment')
    parser.add_argument('aligned_dir', help='Directory for storing aligned images')
    parser.add_argument('--output_size', default=1024, help='The dimension of images for input to the model', type=int)
    parser.add_argument('--x_scale', default=1, help='Scaling factor for x dimension', type=float)
    parser.add_argument('--y_scale', default=1, help='Scaling factor for y dimension', type=float)
    parser.add_argument('--em_scale', default=0.1, help='Scaling factor for eye-mouth distance', type=float)
    parser.add_argument('--use_alpha', default=False, help='Add an alpha channel for masking', type=bool)

    args, other_args = parser.parse_known_args()

    _origin_img_dir = args.origin_dir
    _aligned_img_dir = args.aligned_dir

    landmarks_detector = LandmarksDetector()
    for img_name in os.listdir(_origin_img_dir):
        print('\033[1;32mAligning %s ...' % img_name)
        try:
            raw_img_path = os.path.join(_origin_img_dir, img_name)
            fn = face_img_name = '%s_%02d.png' % (os.path.splitext(img_name)[0], 1)
            if os.path.isfile(fn):
                continue
            print('\033[0mGetting landmarks...')
            for i, face_landmarks in enumerate(landmarks_detector.get_landmarks(raw_img_path), start=1):
                try:
                    print('Starting face alignment...')
                    face_img_name = '%s_%02d.png' % (os.path.splitext(img_name)[0], i)
                    aligned_face_path = os.path.join(_aligned_img_dir, face_img_name)
                    image_align(raw_img_path, aligned_face_path, face_landmarks, output_size=args.output_size, x_scale=args.x_scale, y_scale=args.y_scale, em_scale=args.em_scale, alpha=args.use_alpha)
                    print(f'\033[1;32mWrote result {aligned_face_path}\n\033[0m')
                except:
                    print("\033[1;41mException in face alignment!\033[0m")
        except:
            print("\033[1;41mException in landmark detection!\033[0m")