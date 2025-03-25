import socket
import random

def movement():
    host = "0.0.0.0"
    port = 4000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.bind((host, port))

    print("UDP Movement Server started on port", port)

    try:
        while True:
            rand = random.randint(0, 10)
            data, addr = sock.recvfrom(1024)
            message = data.decode().strip()
            print(f"Received from {addr}: {message}")

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
        print("Movement Server closed.")
