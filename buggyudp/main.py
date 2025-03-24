import threading
from buggyudp_movement import movement
from buggyudp_soil import soil_sample
from buggyudp_image import image_server  # Import the image server

if __name__ == '__main__':
    t1 = threading.Thread(target=movement)
    t2 = threading.Thread(target=soil_sample)
    t3 = threading.Thread(target=image_server)  # Add image server thread

    t1.start()
    t2.start()
    t3.start()  # Start the image server

    t1.join()
    t2.join()
    t3.join()
