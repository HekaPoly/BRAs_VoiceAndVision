#import record
import algorithm
import outputs.retrieve_data as retrieve_data
#import detector
import argparse
#mport torch
import math
import faulthandler
import UART
import robotic
faulthandler.enable()



def main():
    text = record.transcribe_directly()
    print(text)
    label = algorithm.stringtoLabel(text)

    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=str, default='../models/yolov8n.pt', help='model.pt path(s)') #A modifier pour changer de modele
    parser.add_argument('--svo', type=str, default=None, help='optional svo file')
    parser.add_argument('--img_size', type=int, default=416, help='inference size (pixels)')
    parser.add_argument('--conf_thres', type=float, default=0.4, help='object confidence threshold')
    opt = parser.parse_args()

    with torch.no_grad():
        detector.object_detection(label, 45, opt)
    


if __name__ == '__main__':
    #main()
    x = input("x = ")
    y = input("y = ")
    z = input("z = ")
    UART.send_data_to_all_motors([x,y,z],[70,60,3])
    #x = retrieve_data.get_distance(0) * 100
    #y = retrieve_data.get_distance(1) * 100
    #z = retrieve_data.get_distance(2) * 100
    # x =6
    # y=-23.55555
    # z=10.000
    # BASE_HEIGHT = 30.0
    # ARM_LENGTH1 = 23.0
    # ARM_LENGTH2 = 15.0
    # current_angles = (0.0, 0.0, 0.0)  # Angles initiaux (en degrés)
    # target_position = (x, y, z)

    # if not robotic.is_reachable(BASE_HEIGHT, ARM_LENGTH1, ARM_LENGTH2, target_position):
    #     print("L'objet est hors de portée.")
    # else:
    #     try:
    #         theta_base, theta_arm1, theta_arm2 = robotic.calculate_angles(BASE_HEIGHT, ARM_LENGTH1, ARM_LENGTH2, target_position)
    #         print(f"Angles calculés : Base = {theta_base:.0f} degrés, Bras 1 = {theta_arm1:.0f} degrés, Bras 2 = {theta_arm2:.0f} degrés")
    #         UART.send_data_to_all_motors([int(theta_base),int(theta_arm1),int(theta_arm2)],[70,70,70])
    #     except ValueError as e:
    #         print(e)