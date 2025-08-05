import enum
import multiprocessing
from time import sleep
from detector_viewer import DetectorViewer
import speech_to_text
import threading
import time

from text_viewer import run_text_window
from uart import send_data_through_UART

class FolieTechniqueAction(enum.Enum):
    HI = 0,
    LEFT = 1,
    RIGHT = 2,
    UP = 3,
    DANCE = 4,
    FIND_PERSONS = 5,
    POINT_PERSON = 6,
    POINT_EVERYONE = 7,
    RESET = 8

class FolieTechnique:
    def __init__(self):
        self.threshold = 0.02
        
    def find_action(self, command):
        return FolieTechniqueAction.HI
    
    def handle_action(self, action: FolieTechniqueAction):
        def hello(repetitions=3):
            for _ in range(repetitions):
                send_data_through_UART(180, 1)
                sleep(0.3)
                send_data_through_UART(150, 1)
                sleep(0.3)
        
        if action == FolieTechniqueAction.HI:
            hello(3)
        elif action == FolieTechniqueAction.LEFT:
            send_data_through_UART(315, 0)
            sleep(2)
        elif action == FolieTechniqueAction.RIGHT:
            send_data_through_UART(45, 0)
            sleep(2)
        elif action == FolieTechniqueAction.UP:
            send_data_through_UART(180, 1)
            sleep(2)
        elif action == FolieTechniqueAction.DANCE:
            def hello_dance():
                send_data_through_UART(300, 0)
                sleep(1)
                hello(2)
                send_data_through_UART(60, 0)
                sleep(1)
                hello(2)
                self.handle_action(FolieTechniqueAction.RESET)
            
            def base_dance(sleep_time=0.5):
                send_data_through_UART(90, 0)
                sleep(sleep_time)
                send_data_through_UART(90, 1)
                sleep(sleep_time)
                send_data_through_UART(0, 0)
                sleep(sleep_time)
                send_data_through_UART(0, 1)
                sleep(sleep_time)
            
            def base_dance_2(sleep_time=0.5):
                send_data_through_UART(90, 0)
                sleep(sleep_time)
                send_data_through_UART(90, 1)
                sleep(sleep_time)
                send_data_through_UART(180, 0)
                sleep(sleep_time)
                send_data_through_UART(180, 1)
                sleep(sleep_time)
                send_data_through_UART(90, 0)
                sleep(sleep_time)
                send_data_through_UART(90, 1)
                sleep(sleep_time)
                send_data_through_UART(0, 0)
                sleep(sleep_time)
                send_data_through_UART(0, 1)
                sleep(sleep_time)

            hello_dance()
            sleep(1)
            self.handle_action(FolieTechniqueAction.POINT_EVERYONE) # Invite everyone to the dance
            sleep(1)
            base_dance()
            for i in range(2):
                base_dance(0.3)
            base_dance_2()
            for i in range(2):
                base_dance_2(0.3)
            self.handle_action(FolieTechniqueAction.HI)
            sleep(1)

        elif action == FolieTechniqueAction.FIND_PERSONS:
            pass

        elif action == FolieTechniqueAction.POINT_PERSON:
            # if need to show specific element to cv
            # vision_queue.put({"label": label_value, "coordinate_dict": coordinate_dict})
            PERSON_ANGLE_HORIZONTAL = 80
            PERSON_ANGLE_VERTICAL = 90
            send_data_through_UART(PERSON_ANGLE_VERTICAL, 1)
            sleep(0.5)
            send_data_through_UART(PERSON_ANGLE_HORIZONTAL, 0)
            sleep(0.5)
        
        elif action == FolieTechniqueAction.POINT_EVERYONE:
            send_data_through_UART(90, 0)
            sleep(0.5)
            send_data_through_UART(90, 1)
            sleep(0.5)
            for i in range(2):
                send_data_through_UART(0, 0)
                sleep(0.5)
                send_data_through_UART(270, 0)
                sleep(0.5)
                send_data_through_UART(0, 0)
                sleep(0.5)
                send_data_through_UART(90, 0)
                sleep(0.5)
            self.handle_action(FolieTechniqueAction.RESET)
        elif action == FolieTechniqueAction.RESET:
            send_data_through_UART(0, 0)
            sleep(2)
            send_data_through_UART(0, 1)
            sleep(2)
        else:
            pass

    def run_command(self, command: str, vision_queue):
        action: FolieTechniqueAction = self.find_action(command)
        self.handle_action(action)
            
        
        sleep(3)
        pass
    
    def run_reset(self, text_queue):
        send_data_through_UART(45, 0)
        sleep(2)
        send_data_through_UART(0, 1)
        sleep(2)
        send_data_through_UART(0, 2)
        sleep(2)
        text_queue.put("Start Listening")
    
    def vision_thread(self, detector: DetectorViewer, opt):
        detector.run_computer_vision(opt)
    
    
    def run_folie_app(self, opt):
        # open script window
        text_queue = multiprocessing.Queue()
        text_process = multiprocessing.Process(target=run_text_window, args=(text_queue,))
        text_process.start()
        
        vision_queue = multiprocessing.Queue()
        vision_process = multiprocessing.Process(target=self.vision_thread, args=(vision_queue,))
        vision_process.start()
        
        while(True):
            # if detect sound
            command = speech_to_text.transcribe_for() # TODO: create function countdown in text_viewer
            text_queue.put(command)
            
            self.run_command(command, vision_queue)
            self.run_reset(text_queue)
            
            sleep(0.1)
                
                
