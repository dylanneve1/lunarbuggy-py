import socket
import os
import uuid
import hashlib
import time

IMAGE_CHUNK_SIZE = 8192
SEPARATOR = b"||"  # matches the server's separator

def receive_image(sock, attempts):
    print("Receiving image...")
    image_chunks = {}
    total_packets = None
    try:
        # Receive start packet then send ACK.
        data, addr = sock.recvfrom(1024)
        valid_start = False
        start_packet_timeout = 5
        deadline = time.time() + start_packet_timeout
        while not valid_start and time.time() < deadline:
            try:
                data, addr = sock.recvfrom(1024)
            except socket.timeout:
                print("Timeout waiting for start packet.")
                return False
            if data.startswith(b"START:"):
                valid_start = True
                try:
                    total_packets = int(data.decode().split(":")[1])
                    print(f"Expecting {total_packets} packets.")
                    sock.sendto(b"ACK:START", addr)
                except Exception as e:
                    print(f"Error parsing start packet: {e}")
                    return False
        
        # Receive data packets until END marker.
        while True:
            packet, addr = sock.recvfrom(IMAGE_CHUNK_SIZE + 200)
            # Check for known control messages.
            if packet == b"END":
                print("Received END packet.")
                sock.sendto(b"ACK:END", addr)
                break
            if packet == b"TRANSFER_ERROR":
                print("Received TRANSFER_ERROR from server.")
                return False
            # If packet does not contain separator, log and ignore.
            if SEPARATOR not in packet:
                print("Packet missing separator, ignoring.")
                continue
            
            try:
                header, chunk = packet.split(SEPARATOR, 1)
            except Exception as e:
                print(f"Error splitting packet: {e}")
                continue
            # Check that the header starts with our marker.
            if not header.startswith(b"DATA:"):
                print("Non-data packet received, ignoring.")
                continue
            # Remove "DATA:" prefix.
            try:
                header_str = header.decode(errors="replace").replace("DATA:", "")
            except Exception as e:
                print(f"Error decoding header: {e}")
                continue
            header_parts = header_str.split(":")
            if len(header_parts) >= 3 and header_parts[0] == "SEQ" and header_parts[2] == "CHK":
                try:
                    seq = int(header_parts[1])
                except ValueError:
                    print("Error converting sequence number.")
                    continue
                transmitted_checksum = header_parts[3] if len(header_parts) >= 4 else ""
                computed_checksum = hashlib.md5(chunk).hexdigest()
                if computed_checksum != transmitted_checksum:
                    print(f"Checksum mismatch for packet {seq}.")
                    continue  # do not ACK so that sender will resend
                image_chunks[seq] = chunk
                print(f"Received packet {seq}")
                ack_msg = f"ACK:{seq}".encode()
                sock.sendto(ack_msg, addr)
            else:
                print("Invalid header format, ignoring packet.")
        
        # Receive overall checksum.
        checksum_packet, addr = sock.recvfrom(1024)
        try:
            checksum_str = checksum_packet.decode().strip()
        except Exception as e:
            print(f"Error decoding overall checksum: {e}")
            return False
        if checksum_str == "TRANSFER_ERROR":
            print("Received TRANSFER_ERROR from server.")
            return False
        else:
            received_overall_checksum = checksum_str
            print(f"Received overall checksum: {received_overall_checksum}")
            sock.sendto(b"ACK:CHECKSUM", addr)
        
        if total_packets is None or len(image_chunks) != total_packets:
            print(f"Packet loss detected. Expected {total_packets}, got {len(image_chunks)}.")
            return False
        
        # Reassemble image in order.
        image_data = b"".join(image_chunks[i] for i in sorted(image_chunks.keys()))
        computed_overall_checksum = hashlib.md5(image_data).hexdigest()
        print(f"Computed overall checksum: {computed_overall_checksum}")
        
        if computed_overall_checksum == received_overall_checksum:
            print("Overall checksum match! Image data verified.")
            sock.sendto(b"IMAGE_OK", addr)
            # Save image.
            artifacts_dir = "artifacts"
            os.makedirs(artifacts_dir, exist_ok=True)
            unique_id = uuid.uuid4().hex
            filepath = os.path.join(artifacts_dir, f"received_image_{unique_id}.png")
            if os.path.exists(filepath):
                os.remove(filepath)
            with open(filepath, "wb") as f:
                f.write(image_data)
            print(f"Image saved as {filepath}")
            return True
        else:
            print("Overall checksum mismatch! Requesting resend.")
            sock.sendto(b"RESEND", addr)
            return False
        
    except socket.timeout:
        print("Timeout receiving image.")
        return False
    except Exception as e:
        print(f"Error receiving image: {e}")
        return False

def image_client():
    host = socket.gethostname()
    port = 6000
    server_addr = (host, port)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(10)
    
    try:
        while True:
            command = input("Enter 'get_image' to receive an image, or 'q' to quit: ")
            sock.sendto(command.encode(), server_addr)
            if command.lower() == 'q':
                break
            if command == "get_image":
                attempts = 0
                max_attempts = 3
                while attempts < max_attempts:
                    if receive_image(sock, attempts):
                        break
                    attempts += 1
                    print(f"Resend requested. Attempt {attempts}/{max_attempts}")
                if attempts >= max_attempts:
                    print("Failed to receive a valid image after multiple attempts.")
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        sock.close()
