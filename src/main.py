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
        coordinate_dict, label_to_ids = detector.object_detection(label, 25, opt)
        if label not in label_to_ids:
            raise ValueError(f"Label {label} not found in label to IDs mapping.")
        else:
            for obj_id in label_to_ids[label]:
                if obj_id not in coordinate_dict:
                    raise ValueError(f"Object ID {obj_id} with label {label} not found in coordinate dictionary.")
                else:
                    angle = find_angle(coordinate_dict[obj_id])
                    print(f"Angle for object ID {obj_id} with label {label}: {angle}")

if __name__ == '__main__':
    main()
