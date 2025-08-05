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
<<<<<<< HEAD
    HI = "Salut!",
    LEFT = "Tourner a gauche",
    RIGHT = "Tourner a droite",
    UP = "Pointer vers le haut",
    DANCE = "Alors on danse!",
    FIND_PERSONS = "Trouver des personnes",
    POINT_PERSON = "Pointer une personne"
=======
    HI = 0,
    LEFT = 1,
    RIGHT = 2,
    UP = 3,
    DANCE = 4,
    FIND_PERSONS = 5,
    POINT_PERSON = 6,
    POINT_EVERYONE = 7,
    RESET = 8
>>>>>>> origin/feature/folie-technique-app-movement

class FolieTechnique:
    def __init__(self):
        self.threshold = 0.02
        
    def find_action(self, command):
        return FolieTechniqueAction.HI
    
<<<<<<< HEAD
    def handle_action(self, action: FolieTechniqueAction, opt):
=======
    def handle_action(self, action: FolieTechniqueAction):
        def hello(repetitions=3):
            for _ in range(repetitions):
                send_data_through_UART(180, 1)
                sleep(0.3)
                send_data_through_UART(150, 1)
                sleep(0.3)
        
>>>>>>> origin/feature/folie-technique-app-movement
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
            detector.object_detection(0, 60, opt)
            pass

        elif action == FolieTechniqueAction.POINT_PERSON:
            detector.object_detection(0, 60, opt)
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
    
<<<<<<< HEAD
    def vision_thread(self, vision_queue, opt):
        DetectorViewer(vision_queue).run_computer_vision(opt)

    def audio_callback(input_data, frames, time, status):
        if status:
            print(status)
        volume_norm = np.linalg.norm(input_data) * 10
        if volume_norm > self.threshold:
            print("Detected sound above threshold:", volume_norm)


=======
    def vision_thread(self, detector: DetectorViewer, opt):
        detector.run_computer_vision(opt)
    
    
>>>>>>> origin/feature/folie-technique-app-movement
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
                
                
