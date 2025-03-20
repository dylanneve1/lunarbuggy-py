import socket
import random

def movement():
    host = socket.gethostname()
    port = 4000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    print("UDP Movement Server started on port", port)

    try:
        while True:
            rand = random.randint(0, 10)
            data, addr = sock.recvfrom(1024)
            message = data.decode().strip()
            print(f"Received from {addr}: {message}")

            if message.lower() == 'q':
                print("Quit command received. Shutting down movement server.")
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
        print("Movement Server closed.")
