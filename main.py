# Import the class
from frc_apriltags import USBCamera

# Instantiate the class
camera = USBCamera(camNum = 0, resolution = (1280, 720))

# Main loop
while (True):
    # Get the stream
    stream = camera.getStream()

    # Press q to end the program
    if ( camera.getEnd() == True ):
        break