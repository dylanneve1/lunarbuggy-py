import socket

def send_with_ack(sock, packet, addr, expected_ack, max_retries=3, timeout=3):
    original_timeout = sock.gettimeout()
    sock.settimeout(timeout)
    for attempt in range(max_retries):
        try:
            sock.sendto(packet, addr)
            ack, _ = sock.recvfrom(1024)
            if ack.decode().strip() == expected_ack:
                print(f"Received expected ACK: {expected_ack}")
                sock.settimeout(original_timeout)
                return True
            else:
                print(f"Received unexpected ACK: {ack.decode().strip()} (Expected: {expected_ack}), attempt {attempt+1}/{max_retries}")
        except socket.timeout:
            print(f"Timeout waiting for {expected_ack}, attempt {attempt+1}/{max_retries}")
        except Exception as e:
            print(f"Error in send_with_ack: {e}")
    sock.settimeout(original_timeout)
    return False
