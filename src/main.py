import record, algorithm
import detector
import argparse
import torch
import faulthandler
faulthandler.enable()


def main():
    print("Presentation of computer vision")

    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=str, default='../models/yolov8n.pt', help='model.pt path(s)') #A modifier pour changer de modele
    parser.add_argument('--svo', type=str, default=None, help='optional svo file')
    parser.add_argument('--img_size', type=int, default=416, help='inference size (pixels)')
    parser.add_argument('--conf_thres', type=float, default=0.4, help='object confidence threshold')
    opt = parser.parse_args()

    with torch.no_grad():
        detector.object_detection(None, None, opt)

if __name__ == '__main__':
    main()
    