from gpiozero import Button
from signal import pause

LftButton = Button(20)
RgtButton = Button(26)

def LftButtonPressed():
    print("Left Button Pressed")
    return

def RgtButtonPressed():
    print("Right Button Pressed")
    return

LftButton.when_pressed = LftButtonPressed
RgtButton.when_pressed = RgtButtonPressed

pause()
# ---------------------------------------------------------------------
