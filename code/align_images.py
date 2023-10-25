import os
import argparse
from face_alignment import image_align

if __name__ == "__main__":
    """
    Extracts and aligns all faces from images using DLib and a function from original FFHQ dataset preparation step
    python align_images.py /raw_images /aligned_images
    This code currently supports only images.jpg/png/jpeg files with a single face.
    """
    parser = argparse.ArgumentParser(description='Align faces from input images', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--image', required=True, help="path to input image")
    parser.add_argument('--output_size', default=1024, help='The dimension of images for input to the model', type=int)
    parser.add_argument('--x_scale', default=1, help='Scaling factor for x dimension', type=float)
    parser.add_argument('--y_scale', default=1, help='Scaling factor for y dimension', type=float)
    parser.add_argument('--em_scale', default=0.1, help='Scaling factor for eye-mouth distance', type=float)
    parser.add_argument('--use_alpha', default=False, help='Add an alpha channel for masking', type=bool)

    args, other_args = parser.parse_known_args()

    image = args.image
    _aligned_img_dir = os.path.split(image)[0]
    img_name = os.path.split(image)[1]

    # points_filename = "example/harry.txt"
    pointe_filecname = os.path.splitext(image)[0] + ".txt"
    landmarks_detector = []
    with open(pointe_filecname) as file :
        for line in file :
            x, y = line.split()
            landmarks_detector.append((int(x), int(y)))

    split_path = os.path.splitext(img_name)
    print(f'\033[1;32mAligning {img_name}...')
    print('\033[0mGetting landmarks...')

    try:
        print('Starting face alignment...')
        face_img_name = f"aligned-{split_path[0]}.png"
        aligned_face_path = os.path.join(_aligned_img_dir, face_img_name)
        image_align(image, aligned_face_path, landmarks_detector, output_size=args.output_size, 
                    x_scale=args.x_scale, y_scale=args.y_scale, em_scale=args.em_scale, alpha=args.use_alpha)
        print(f'\033[1;32mWrote result {aligned_face_path}\n\033[0m')
    except:
        print("\033[1;41mException in face alignment!\033[0m")