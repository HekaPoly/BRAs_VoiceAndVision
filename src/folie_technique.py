import enum
import multiprocessing
from time import sleep
import detector
import speech_to_text
import threading
import time

from text_viewer import run_text_window
from uart import send_data_through_UART
import random

class FolieTechniqueAction(enum.Enum):
    HI = "Salut!",
    LEFT = "Tourner a gauche",
    RIGHT = "Tourner a droite",
    UP = "Pointer vers le haut",
    DANCE = "Alors on danse!",
    FIND_PERSONS = "Trouver des personnes",
    POINT_PERSON = "Pointer une personne"

class FolieTechnique:
    def __init__(self):
        self.threshold = 0.02
        
    def find_action(self, command):
        return FolieTechniqueAction.HI
    
    def handle_action(self, action: FolieTechniqueAction, opt):
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
            detector.object_detection(0, 60, opt)
            pass
        elif action == FolieTechniqueAction.POINT_PERSON:
            detector.object_detection(0, 60, opt)
            # if need to show specific element to cv
            # vision_queue.put({"label": label_value, "coordinate_dict": coordinate_dict})
            pass
        else:
            pass
    def get_command_from_text(self, raw_text):
        lower_text = raw_text.lower()
        
        if any(word in lower_text for word in ["bonjour", "hi", "hello", "salu"]):
            return FolieTechniqueAction.HI
            pass
        elif any(word in lower_text for word in ["gauche", "left"]):
            return FolieTechniqueAction.LEFT
        elif any(word in lower_text for word in ["droit", "right"]):
            return FolieTechniqueAction.RIGHT
        elif any(word in lower_text for word in ["haut", "up", "ciel"]):
            return FolieTechniqueAction.UP
        elif any(word in lower_text for word in ["danse", "dance"]):
            return FolieTechniqueAction.DANCE
        elif sum(1 for word in ["trouve", "find", "person", "people"] if word in lower_text) >= 2:
            # if need to show specific element to cv
            # vision_queue.put({"label": label_value, "coordinate_dict": coordinate_dict})
            return FolieTechniqueAction.FIND_PERSONS
        elif sum(1 for word in ["montre", "point", "person", "people"] if word in lower_text) >= 2:
            return FolieTechniqueAction.POINT_PERSON
        else:
            return None

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
    
    def vision_thread(self, vision_queue, opt):
        DetectorViewer(vision_queue).run_computer_vision(opt)

    def audio_callback(input_data, frames, time, status):
        if status:
            print(status)
        volume_norm = np.linalg.norm(input_data) * 10
        if volume_norm > self.threshold:
            print("Detected sound above threshold:", volume_norm)


    def run_folie_app(self, opt):
        # open script window
        text_queue = multiprocessing.Queue()
        text_process = multiprocessing.Process(target=run_text_window, args=(text_queue,))
        text_process.start()
        
        text_queue.put("Dit BIRA!")
        sleep(2)

        # if detect sound
        text_queue.put({"text": "Dit ta commande!", "countdown": 10})
        text = speech_to_text.transcribe_for(10)

        command = self.get_command_from_text(text)
        while(command is None):
            text_queue.put({"text": "Jai mal compris,\npeux-tu repeter ta commande. :)", "countdown": 10})
            text = speech_to_text.transcribe_for(10)
            command = self.get_command_from_text(text)

        text_queue.put({"text": command.value, "countdown": 3})

        sleep(3)
        text_process.terminate()

        
        self.handle_action(command, opt)
        #self.run_reset(text_queue)
        
        sleep(0.1)
                
                
