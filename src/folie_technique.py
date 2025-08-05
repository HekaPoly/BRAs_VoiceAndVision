import enum
import multiprocessing
from detector_viewer import DetectorViewer
import sounddevice as sd
from time import sleep
import detector
import speech_to_text
import threading
import time
import numpy as np


from text_viewer import run_text_window
from uart import send_data_through_UART
import random

VOLUME_THRESHOLD = 0.2

class FolieTechniqueAction(enum.Enum):
    HI = "Salut! :D",
    LEFT = "Tourner a gauche",
    RIGHT = "Tourner a droite",
    UP = "Pointer vers le haut",
    DANCE = "Alors on danse!",
    FIND_PERSONS = "Trouver des personnes",
    POINT_PERSON = "Pointer une personne",
    RESET = "Reset BIRA"

class FolieTechnique:
    def __init__(self):
        self.threshold = 0.02
        self.hasStarted = False
        
    def hello_dance(self,):
        send_data_through_UART(300, 0)
        sleep(1)
        self.hello(2)
        send_data_through_UART(60, 0)
        sleep(1)
        self.hello(2)
    
    def base_dance(self, sleep_time=0.5):
        send_data_through_UART(90, 0)
        sleep(sleep_time)
        send_data_through_UART(90, 1)
        sleep(sleep_time)
        send_data_through_UART(0, 0)
        sleep(sleep_time)
        send_data_through_UART(0, 1)
        sleep(sleep_time)
    
    def base_dance_2(self, sleep_time=0.5):
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

    def hello(self, repetitions=3):
        send_data_through_UART(180, 1)
        sleep(5)
        for _ in range(repetitions):
            send_data_through_UART(185, 1)
            sleep(3)
            send_data_through_UART(175, 1)
            sleep(3)
            
    def handle_action(self, action: FolieTechniqueAction, opt):
        if action == FolieTechniqueAction.HI:
            self.hello(3)
        elif action == FolieTechniqueAction.LEFT:
            send_data_through_UART(0, 0)
            sleep(2)
        elif action == FolieTechniqueAction.RIGHT:
            send_data_through_UART(75, 0)
            sleep(2)
        elif action == FolieTechniqueAction.UP:
            send_data_through_UART(180, 1)
            sleep(2)
        elif action == FolieTechniqueAction.DANCE:
            self.hello_dance()
            sleep(1)
            self.base_dance()
            for i in range(2):
                self.base_dance(0.3)
            self.base_dance_2()
            for i in range(2):
                self.base_dance_2(0.3)
            sleep(1)

        elif action == FolieTechniqueAction.FIND_PERSONS:
            detector.object_detection(0, 60, opt)
            pass

        elif action == FolieTechniqueAction.POINT_PERSON:
            detector.object_detection(0, 60, opt)
            # if need to show specific element to cv
            # vision_queue.put({"label": label_value, "coordinate_dict": coordinate_dict})
            # PERSON_ANGLE_HORIZONTAL = 80
            # PERSON_ANGLE_VERTICAL = 90
            # send_data_through_UART(PERSON_ANGLE_VERTICAL, 1)
            # sleep(0.5)
            # send_data_through_UART(PERSON_ANGLE_HORIZONTAL, 0)
            # sleep(0.5)
        else:
            print("No action matched.")
        
    def get_command_from_text(self, raw_text):
        lower_text = raw_text.lower()
        
        if any(word in lower_text for word in ["bonjour", "hi", "hello", "salu", "allo"]):
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
    
    def run_reset(self):
        send_data_through_UART(30, 0)
        send_data_through_UART(0, 1)
    
    def vision_thread(self, vision_queue, opt):
        DetectorViewer(vision_queue).run_computer_vision(opt)

    def run_sound_detection(self):
        has_detect = False

        stream = sd.InputStream(channels=1, samplerate=44100, blocksize=1024)
        stream.start()

        while not has_detect:
            data, _ = stream.read(1024)
            volume = np.linalg.norm(data)
            if volume > VOLUME_THRESHOLD:
                print("Audio detected, starting Folie Technique...")       
                has_detect = True
            sleep(0.1)

        stream.stop()
        stream.close()
        

    def run_folie_app(self, opt):
        self.run_reset()
        sleep(2)

        text_queue = multiprocessing.Queue()
        text_process = multiprocessing.Process(target=run_text_window, args=(text_queue,))
        text_process.start()
        
        text_queue.put("Dit BIRA!")
        self.run_sound_detection()
        
        
        text_queue.put({"text": "Prépare toi!", "countdown": 2})
        text_queue.put({"text": "Dit ta commande!", "countdown": 10})
        text = speech_to_text.transcribe_for(12)
        command = self.get_command_from_text(text)
        
        
        while(command is None):
            text_queue.put({"text": "Jai mal compris,\npeux-tu repeter ta commande. :)", "countdown": 10})
            text = speech_to_text.transcribe_for(10)
            command = self.get_command_from_text(text)


        text_queue.put({"text": command.value, "countdown": 3})
        sleep(3)
        text_process.terminate()

        self.handle_action(command, opt)

        print("Done action, resetting...")
        sleep(5)
        self.run_reset()
                        
                
