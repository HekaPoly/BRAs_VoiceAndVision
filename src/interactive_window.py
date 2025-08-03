import tkinter as tk
from tkinter import Toplevel
import threading
import speech_to_text

class Windows:
    dialogue_window = None
    dialogue_box = None

    @staticmethod
    def open():
        try:
            if Windows.dialogue_window is not None:
                print("[DEBUG] Window already open")
                return

            Windows.dialogue_window = tk.Tk()
            Windows.dialogue_window.title("Dialogue Box")

            Windows.dialogue_box = tk.Text(Windows.dialogue_window, height=20, width=60, wrap="word")
            Windows.dialogue_box.pack(padx=10, pady=10)

            tk.Button(Windows.dialogue_window, text="Clear", command=Windows.clear).pack(side="left", padx=10)
            tk.Button(Windows.dialogue_window, text="Close", command=Windows.close).pack(side="right", padx=10)

            tk.Button(Windows.dialogue_window,text="Start Listening",command=Windows.open_dialogue_window).pack(side="bottom", pady=10)

            Windows.dialogue_window.protocol("WM_DELETE_WINDOW", Windows.close)
            Windows.dialogue_window.mainloop()

        # Aide avec le déboguage
        except Exception as e:
            import traceback
            print("[ERROR] Exception in Windows.open():")
            traceback.print_exc()

    @staticmethod
    def close():
        if Windows.dialogue_window:
            Windows.dialogue_window.destroy()
            Windows.dialogue_window = None
            Windows.dialogue_box = None

    @staticmethod
    def clear():
        if Windows.dialogue_box:
            Windows.dialogue_box.delete("1.0", tk.END)

    @staticmethod
    def display(inputs: str):
        if Windows.dialogue_box:
            Windows.dialogue_box.insert(tk.END, f"{inputs}\n")
            Windows.dialogue_box.see(tk.END)

    @staticmethod
    def open_dialogue_window():
        # def listen_loop():    # Écoute infinie
        #     while True:
        #         try:
        #             Windows.display("🎙️ Écoute en cours...")
        #             text = speech_to_text.transcribe_for(5)
        #             if text:
        #                 Windows.display(f"🗣️ {text}")
        #         except Exception as e:
        #             Windows.display(f"[Erreur]: {e}")

        def listen_once():     # Écoute pour 5 secondes ou plus dès que le bouton est appuyer sur le window
            try:
                Windows.display("🎙️ Écoute en cours...")
                text = speech_to_text.transcribe_directly(5)
                if text:
                    Windows.display(f"🗣️ {text}")
            except Exception as e:
                Windows.display(f"[Erreur]: {e}")

        threading.Thread(target=listen_once, daemon=True).start()

if __name__ == "__main__":
    print("[DEBUG] Starting app")
    Windows.open()
