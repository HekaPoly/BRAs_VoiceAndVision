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
    POINT_PERSON = 6

class FolieTechnique:
    def __init__(self):
        self.threshold = 0.02
        
    def find_action(self, command):
        return FolieTechniqueAction.HI
    
    def handle_action(self, action: FolieTechniqueAction):
        if action == FolieTechniqueAction.HI:
            pass
        elif action == FolieTechniqueAction.LEFT:
            pass
        elif action == FolieTechniqueAction.RIGHT:
            pass
        elif action == FolieTechniqueAction.UP:
            pass
        elif action == FolieTechniqueAction.DANCE:
            pass
        elif action == FolieTechniqueAction.FIND_PERSONS:
            pass
        elif action == FolieTechniqueAction.POINT_PERSON:
            # if need to show specific element to cv
            # vision_queue.put({"label": label_value, "coordinate_dict": coordinate_dict})
            pass
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
                
                
