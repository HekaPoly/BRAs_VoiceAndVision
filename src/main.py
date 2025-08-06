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
from folie_technique import FolieTechnique
import multiprocessing

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
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=str, default='../models/yolov8n.pt', help='model.pt path(s)')
    parser.add_argument('--svo', type=str, default=None, help='optional svo file')
    parser.add_argument('--img_size', type=int, default=416, help='inference size (pixels)')
    parser.add_argument('--conf_thres', type=float, default=0.4, help='object confidence threshold')
    parser.add_argument('--mode', type=str, default="", help='')
    opt = parser.parse_args()

    if opt.mode == "folie":
        with torch.no_grad():
                FolieTechnique().run_folie_app(opt)
    else:
        while True:
            try:
                a = input("Enter angle: ")
                b = input("Enter motor ID: ")
                if input("Do you want to enter velocity? (y/N): ").strip().lower() == 'y':
                    c = input("Enter velocity %: ")
                else:
                    c = 80
                uart.send_data_through_UART(int(a), int(b), int(c))
                print("Data sent successfully.\n")
            except ValueError:
                print("Invalid input. Please enter numeric values.\n\n")

if __name__ == '__main__':
    main()

       


