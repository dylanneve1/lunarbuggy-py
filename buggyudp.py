from socket import *
import socket
import random
import threading


def movement():
    host = socket.gethostname()
    port = 4000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    print("UDP Server started on port", port)

    try:
        while True:
            rand = random.randint(0,10)
            data, addr = sock.recvfrom(1024)
            message = data.decode().strip()
            print(f"Received from {addr}: {message}")

            if message.lower() == 'q':
                print("Quit command received. Shutting down.")
                response = "Server is shutting down."
                sock.sendto(response.encode(), addr)
                break

            response = ""
            match message:
                case 'w':
                    response = "Moving Forward"
                case 'a':
                    response = "Moving Left"
                case 's':
                    response = "Moving Backward"
                case 'd':
                    response = "Moving Right"
                case _:
                    response = "Invalid Movement Command"
                    
            if rand < 4:
                print("Simulating Lost Packet")
                continue
            if response:
                sock.sendto(response.encode(), addr)
    finally:
        sock.close()
        print("Server closed.")

def soil_sample():
    host = socket.gethostname()
    port = 5000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    print("UDP Server started on port", port)

    try:
        while True:
            rand = random.randint(0,10)
            data, addr = sock.recvfrom(1024)
            message = data.decode().strip()
            print(f"Received from {addr}: {message}")

            if message.lower() == 'q':
                print("Quit command received. Shutting down.")
                response = "Server is shutting down."
                sock.sendto(response.encode(), addr)
                break

            response = ""
            match message:
                case 'soil':
                    response = "Sampling Soil"
                case 'air':
                    response = "Sampling Air"
                case _:
                    response = "Invalid Sample Command"
                    
            if rand < 4:
                print("Simulating Lost Packet")
                continue
            if response:
                sock.sendto(response.encode(), addr)
    finally:
        sock.close()
        print("Server closed.")

if __name__ == '__main__':
    t1 = threading.Thread(target=movement)
    t2 = threading.Thread(target=soil_sample)

    t1.start()
    t2.start()

    t1.join()
    t2.join()