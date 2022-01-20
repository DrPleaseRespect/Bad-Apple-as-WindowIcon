from PySide2.QtCore import QObject, Signal
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QWidget
import sys
import os
import time
import ctypes
import threading
import mpv

# Workaround for Window Icon 
# https://stackoverflow.com/a/1552105
APPID = F'drpleaserespect.badapple.programthing'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)

class Signal(QObject):
    Thing = Signal(int)

class BadApple(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.Signals = Signal()
        self.setWindowTitle("Bad Apple")
        # Initalize List of Images
        self.images = []
        self.lock = False
        print("PRELOADING ALL IMAGES")
        images_raw = os.listdir("IMAGES")
        current = time.time()
        for item in images_raw:
            if item.endswith(".png"):
                self.images.append(QIcon(f"IMAGES/{item}"))
        elasped = time.time() - current
        print("LOADED ALL IMAGES IN", elasped, "SECONDS")
        print("LOADING COMPLETE")
        self.show()
        # USE MPV PLAYER FOR AUDIO AND SYNC TO FRAMES
        self.player = mpv.MPV(video='no')
        self.player.play("bad.webm")
        self.player.wait_until_playing()
        self.player.pause = True
        self.player.seek(0, reference='absolute')

        self.Signals.Thing.connect(self.iconchange)
        
        threading.Thread(target=self.logicthread).start()

    def closeEvent(self, event) -> None:
        self.player.quit()
        return super().closeEvent(event)

    def iconchange(self,index):
        self.setWindowIcon(self.images[index])

    def logicthread(self):
        previous = time.time()
        imageindex = 0
        fps = 30
        self.player.pause = False
        while True:
            try:
                current = time.time()
                elasped = current - previous
                self.Signals.Thing.emit(imageindex)

                # USES MPV TIME TO DETERMINE FRAME TIME
                if self.player.time_pos is None:
                    return
                thigy = round(abs(self.player.time_pos) * fps)

                # USES ELASPED TIME TO DETERMINE FRAME TIME
                # thigy = abs(round(elasped * fps))

                imageindex = thigy
                print(F"FRAME: {imageindex} | TIME: {self.player.time_pos}")


                time.sleep(1/fps - ((time.time() - previous) % 1/fps))
            except mpv.ShutdownError:
                return



if "__main__" == __name__:
    app = QApplication(sys.argv)
    badapple = BadApple()
    sys.exit(app.exec_())
