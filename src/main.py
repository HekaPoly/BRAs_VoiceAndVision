import record
import algorithm
import outputs.retrieve_data as retrieve_data
import detector
import argparse
import torch
import math
import faulthandler
import UART
faulthandler.enable()

def find_angle() -> int:
    x = retrieve_data.get_distance(0) 
    y = retrieve_data.get_distance(1)
    z = retrieve_data.get_distance(2)
    angle_rad = math.atan(x/z)
    
    # Convert radians to degrees
    angle_deg = math.degrees(angle_rad)
    print("First angle: ", angle_deg)

    return angle_deg

def find_second_angle() -> int:
    x = retrieve_data.get_distance(0) 
    y = retrieve_data.get_distance(1)
    z = retrieve_data.get_distance(2)
    dist = math.dist((x, y, z), (0, 0, 0))
    angle_rad = math.asin(y/dist)
    
    # Convert radians to degrees
    angle_deg = math.degrees(angle_rad)
    print("Second angle: ", angle_deg)

    return angle_deg

def main():
    text = "bouteille"
    print(text)
    label = algorithm.stringtoLabel(text)
    print(label)
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=str, default='../models/yolov8n.pt', help='model.pt path(s)') #A modifier pour changer de modele
    parser.add_argument('--svo', type=str, default=None, help='optional svo file')
    parser.add_argument('--img_size', type=int, default=416, help='inference size (pixels)')
    parser.add_argument('--conf_thres', type=float, default=0.4, help='object confidence threshold')
    opt = parser.parse_args()

    with torch.no_grad():
        detector.object_detection(label, 60, opt)
    
    angles = (find_angle(), find_second_angle())
    UART.send_data_through_UART(angles[0], 0)
    UART.send_data_through_UART(angles[1], 1)

if __name__ == '__main__':
    UART.send_data_through_UART(0, 0)
    input()
    UART.send_data_through_UART(0, 1)
    input()
    UART.send_data_through_UART(0, 2)
    input()
    UART.send_data_through_UART(0, 3)
    input()
    main()
