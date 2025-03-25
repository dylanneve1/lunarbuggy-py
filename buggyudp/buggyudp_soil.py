import socket
import random

def soil_sample():
    host = "0.0.0.0"
    port = 5000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.bind((host, port))

    print("UDP Soil Sampling Server started on port", port)

    try:
        while True:
            rand = random.randint(0, 10)
            data, addr = sock.recvfrom(1024)
            message = data.decode().strip()
            print(f"Received from {addr}: {message}")

            if message.lower() == 'q':
                print("Quit command received. Shutting down soil sampling server.")
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
        print("Soil Sampling Server closed.")
