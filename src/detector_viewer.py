#!/usr/bin/env python3

from ultralytics import YOLO
from threading import Lock, Thread
from scipy.stats import trim_mean

import argparse
import sys
import numpy as np

import torch
import cv2
import pyzed.sl as sl

import time

import ogl_viewer.viewer as gl
import cv_viewer.tracking_viewer as cv_viewer
import cv_viewer.labels as lab
import history as rd
from utils import string_to_label
import detector

lock = Lock()
run_signal = False
exit_signal = False

def torch_thread(weights, img_size, conf_thres=0.2, iou_thres=0.45):
    global image_net, exit_signal, run_signal, detections

    print("Intializing Network...")

    yolo = YOLO(weights)
    yolo.model.to('cuda')
    yolo.model.eval()

    while not exit_signal:
        if run_signal:
            lock.acquire()

            img = cv2.cvtColor(image_net, cv2.COLOR_BGRA2RGB)
            # https://docs.ultralytics.com/modes/predict/#video-suffixes
            det = yolo.predict(img, save=False, imgsz=img_size, conf=conf_thres,
                               iou=iou_thres)[0].cpu().numpy().boxes

            # ZED CustomBox format (with inverse letterboxing tf applied)
            detections = detections_to_custom_box(det, image_net)
            lock.release()
            run_signal = False
        time.sleep(0.01)

class DetectorViewer:
    def __init__(self, queue):
        self.queue = queue
        self.label = -1
        self.coordinate_dict = {}
  
    def check_queue(self):
        """Checks the queue to receive update"""
        while not self.queue.empty():
            message:dict = self.queue.get()
            self.label = message.get("label", self.label)
            self.coordinate_dict = message.get("coordinate_dict", self.coordinate_dict)

        
    def run_computer_vision(self, opt, max_distance: float = 7.0):
        global image_net, exit_signal, run_signal, detections

        capture_thread = Thread(target=detector.torch_thread, kwargs={'weights': opt.weights,
                                                            'img_size': opt.img_size,
                                                            "conf_thres": opt.conf_thres})
        capture_thread.start()
        print("Initializing Camera...")

        zed = sl.Camera()

        input_type = sl.InputType()
        if opt.svo is not None:
            input_type.set_from_svo_file(opt.svo)

        # Create an InitParameters object and set the configuration parameters
        init_params = sl.InitParameters(input_t=input_type, svo_real_time_mode=True)
        init_params.coordinate_units = sl.UNIT.METER
        init_params.depth_mode = sl.DEPTH_MODE.ULTRA
        init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
        init_params.depth_maximum_distance = 3
        init_params.camera_fps = 60

        runtime_params = sl.RuntimeParameters()
        status = zed.open(init_params)

        if status != sl.ERROR_CODE.SUCCESS:
            print(repr(status))
            exit()

        image_left_tmp = sl.Mat()

        print("Initialized Camera")

        positional_tracking_parameters = sl.PositionalTrackingParameters()
        # If the camera is static, uncomment the following line to have better performances
        # and boxes sticked to the ground.
        # positional_tracking_parameters.set_as_static = True
        zed.enable_positional_tracking(positional_tracking_parameters)

        obj_param = sl.ObjectDetectionParameters()
        obj_param.detection_model = sl.OBJECT_DETECTION_MODEL.CUSTOM_BOX_OBJECTS
        obj_param.enable_tracking = False
        zed.enable_object_detection(obj_param)

        objects = sl.Objects()
        obj_runtime_param = sl.ObjectDetectionRuntimeParameters()

        # Display
        camera_infos = zed.get_camera_information()
        camera_res = camera_infos.camera_configuration.resolution

        # Create OpenGL viewer
        viewer = gl.GLViewer()
        point_cloud_res = sl.Resolution(min(camera_res.width, 720), min(camera_res.height, 404))
        point_cloud_render = sl.Mat()
        viewer.init(camera_infos.camera_model, point_cloud_res, obj_param.enable_tracking)
        point_cloud = sl.Mat(point_cloud_res.width, point_cloud_res.height, sl.MAT_TYPE.F32_C4,
                            sl.MEM.CPU)
        image_left = sl.Mat()

        # Utilities for 2D display
        display_resolution = sl.Resolution(min(camera_res.width, 1280), min(camera_res.height, 720))
        image_scale = [display_resolution.width / camera_res.width,
                    display_resolution.height / camera_res.height]
        image_left_ocv = np.full((display_resolution.height, display_resolution.width, 4),
                                [245, 239, 239, 255], np.uint8)

        # Utilities for tracks view
        camera_config = camera_infos.camera_configuration
        tracks_resolution = sl.Resolution(400, display_resolution.height)
        track_view_generator = cv_viewer.TrackingViewer(tracks_resolution, camera_config.fps,
                                                        init_params.depth_maximum_distance)
        track_view_generator.set_camera_calibration(camera_config.calibration_parameters)
        image_track_ocv = np.zeros((tracks_resolution.height, tracks_resolution.width, 4),
                                np.uint8)

        # Camera pose
        cam_w_pose = sl.Pose()
        while viewer.is_available() and not exit_signal:
            self.check_queue()

            if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:

                # -- Get the image
                lock.acquire()
                zed.retrieve_image(image_left_tmp, sl.VIEW.LEFT)
                image_net = image_left_tmp.get_data()
                lock.release()
                run_signal = True

                # -- Detection running on the other thread
                while run_signal:
                    time.sleep(0.001)

                # Wait for detections
                lock.acquire()

                # -- Ingest detections
                zed.ingest_custom_box_objects(detections)
                lock.release()

                zed.retrieve_objects(objects, obj_runtime_param)

                object_list = objects.object_list
                for obj in object_list:
                    if len(obj.bounding_box) == 0 : continue  
                    if np.isnan(obj.position).any(): continue
                    if obj.position[2] > max_distance: continue  # Filter outliers by distance.
                    if obj.raw_label not in self.coordinate_dict:
                        self.coordinate_dict[obj.raw_label] = np.empty((0,3))
                    self.coordinate_dict[obj.raw_label] = np.vstack([self.coordinate_dict[obj.raw_label], np.array(list(obj.position))])

                rd.write_history(object_list, self.label)
                
                # -- Display
                # Retrieve display data
                zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA, sl.MEM.CPU, point_cloud_res)
                point_cloud.copy_to(point_cloud_render)
                zed.retrieve_image(image_left, sl.VIEW.LEFT, sl.MEM.CPU, display_resolution)
                zed.get_position(cam_w_pose, sl.REFERENCE_FRAME.WORLD)

                # 2D rendering
                np.copyto(image_left_ocv, image_left.get_data())
                cv_viewer.render_2D(image_left_ocv, image_scale, objects, obj_param.enable_tracking,
                                    self.label)
                global_image = cv2.hconcat([image_left_ocv, image_track_ocv])

                # Tracking view
                # track_view_generator.generate_view(objects, cam_w_pose, image_track_ocv,
                # objects.is_tracked)

                cv2.imshow("ZED | 2D View and Birds View", global_image)
                key = cv2.waitKey(10)

                if key == 27 :
                    exit_signal = True
            else:
                exit_signal = True
        
        viewer.exit()
        point_cloud.free()
        image_left.free()
        exit_signal = True
        zed.disable_object_detection()
        zed.close()