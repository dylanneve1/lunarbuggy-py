import socket
from controludp_utils import get_input

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

            except socket.timeout:
                print("Request Timed Out")
                continue
    finally:
        sock.close()
