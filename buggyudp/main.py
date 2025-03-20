import threading
from buggyudp_movement import movement
from buggyudp_soil import soil_sample

if __name__ == '__main__':
    t1 = threading.Thread(target=movement)
    t2 = threading.Thread(target=soil_sample)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
