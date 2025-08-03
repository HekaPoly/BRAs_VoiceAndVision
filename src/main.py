from scipy.stats import trim_mean
import speech_to_text
import numpy as np
import utils
import history as history
import detector
import argparse
import torch
import math
import faulthandler
import uart
from enum import Enum
import interactive_window

faulthandler.enable()

class Mode(Enum):
    FIX_THRESHOLD = 0
    TRIMMED = 1

def find_angle(coordinated_target_list:np.ndarray, mode: Mode = Mode.FIX_THRESHOLD) -> int:
    x = z = 0
    if mode == Mode.TRIMMED:
        x = trim_mean(coordinated_target_list[:,0], proportiontocut=0.1)
        z = trim_mean(coordinated_target_list[:,2], proportiontocut=0.1)
    elif mode == Mode.FIX_THRESHOLD:
        x = history.get_distance(coordinated_target_list[:,0])
        z = history.get_distance(coordinated_target_list[:,2])
    
    angle_rad = math.atan(x / z)
    angle_deg = math.degrees(angle_rad)
    return angle_deg

def main():
    text = speech_to_text.transcribe_directly()
    print(text)
    label = utils.string_to_label(text)
    print(label)

    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=str, default='../models/yolov8n.pt', help='model.pt path(s)')
    parser.add_argument('--svo', type=str, default=None, help='optional svo file')
    parser.add_argument('--img_size', type=int, default=416, help='inference size (pixels)')
    parser.add_argument('--conf_thres', type=float, default=0.4, help='object confidence threshold')
    opt = parser.parse_args()

    with torch.no_grad():
        coordinate_dict = detector.object_detection(label, 25, opt)
        if label not in coordinate_dict:
            raise ValueError(f"Label {label} not found in coordinate dictionary.")
        else:
            angle = find_angle(coordinate_dict.get(label, np.empty((0, 3))))
            print("angle :", angle)

    # Pas sure ou mettre la fonction pour maintenant
    interactive_window.Windows.start_infinite_cam(label, opt)

if __name__ == '__main__':
    main()
