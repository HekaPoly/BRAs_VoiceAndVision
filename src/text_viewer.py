import multiprocessing
import tkinter as tk
import traceback

class TextViewer:
    def __init__(self, queue):
        self.queue = queue
        self.dialogue_window = tk.Tk()
        self.dialogue_window.title("Dialogue Box")

        self.label = tk.Label(self.dialogue_window, text="Start Listening", font=("Helvetica", 16), height=20, width=60)
        self.label.pack(padx=10, pady=5)
        self.countdown = tk.Label(self.dialogue_window, text="", font=("Helvetica", 16), height=20, width=60)
        self.countdown.pack(padx=10)

        tk.Button(self.dialogue_window, text="Clear", command=self.clear).pack(side="left", padx=10)
        self.dialogue_window.protocol("WM_DELETE_WINDOW", self.close)

        # tk.Button(self.dialogue_window,text="Start Listening",command=self.open_dialogue_window).pack(side="bottom", pady=10)

    def open(self):
        try:
            self.dialogue_window.after(100, self.check_queue)
            self.dialogue_window.mainloop()

        except Exception as e:
            print("[ERROR] Exception in self.open():")
            traceback.print_exc()

    def close(self):
        if self.dialogue_window:
            self.dialogue_window.destroy()
            self.dialogue_window = None
            self.label = None

    def clear(self):
        if self.label:
            self.label.config(text="Start Listening")

    def update_text(self, inputs: str):
        if self.label:
            self.label.config(text=inputs)

    def start_countdown(self, countdown: int):
        if self.countdown:
            self.countdown.config(text=f"{countdown} secondes")
            for i in range(countdown, 0, -1):
                self.countdown.config(text=f"{i} secondes")
                self.dialogue_window.update()
                self.dialogue_window.after(1000)
            self.countdown.config(text=f"")
            self.label.config(text=f"Je suis en train de reflechir...")

    def check_queue(self):
        """Periodically checks the queue to receive text"""
        while not self.queue.empty():
            message = self.queue.get()
            if isinstance(message, str):
                self.update_text(message)
            elif isinstance(message, dict):
                if "text" in message:
                    self.update_text(message["text"])
                if "countdown" in message:
                    self.start_countdown(countdown=message["countdown"])
            else:
                print("[DEBUG] Received unknown message type:", type(message))
        self.dialogue_window.after(100, self.check_queue)
        

def run_text_window(queue: multiprocessing.Queue):
    app = TextViewer(queue)
    app.open()

def main():
    queue = multiprocessing.Queue()

    gui_process = multiprocessing.Process(target=run_text_window, args=(queue,))
    gui_process.start()

    print("Testing inputs:")
    try:
        while True:
            user_input = input("> ")
            queue.put(user_input)
    except KeyboardInterrupt:
        print("Closing...")
    finally:
        gui_process.terminate()
        gui_process.join()

if __name__ == "__main__":
    print("[DEBUG] Starting app")
    main()
