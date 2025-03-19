from socket import *
import socket

def get_input():
    command = input("Please Input Command: ")
    while not command:
        command = input("Please Input Command: ")
    return command

def movement():
    host = socket.gethostname()
    port = 4000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = (host, port)
    sock.settimeout(1)
    try:
        while True:
            try:
                command = get_input()
                sock.sendto(command.encode(), server_addr)
                if command.lower() == 'q':
                    data, addr = sock.recvfrom(1024)
                    print("Response:", data.decode())
                    break
                data, addr = sock.recvfrom(1024)
                print("Response:", data.decode())
            except timeout:
                print("Request Timed Out")
                continue
    finally:
        sock.close()

def soil_sample():
    host = socket.gethostname()
    port = 5000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = (host, port)
    sock.settimeout(1)
    try:
        while True:
            try:
                command = get_input()
                sock.sendto(command.encode(), server_addr)
                if command.lower() == 'q':
                    data, addr = sock.recvfrom(1024)
                    print("Response:", data.decode())
                    break
                data, addr = sock.recvfrom(1024)
                print("Response:", data.decode())
            except timeout:
                print("Request Timed Out")
                continue
    finally:
        sock.close()
if __name__ == '__main__':
    while True:
        print("Please Choose a function")
        print("1: movement")
        print("2: soil sampling")
        print("exit: Exit the program")
        choice = input("->")
        match choice:
            case '1':
                movement()
            case '2':
                soil_sample()
            case 'exit':
                print("Program Terminating")
                break
            case _:
                print("Invalid Input Command")