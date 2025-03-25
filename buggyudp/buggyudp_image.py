import socket
import os
import uuid
import hashlib
from buggyudp_generate_image import generate_lunar_image
from buggyudp_generate_image import rover_prompt
from buggyudp_utils import send_with_ack
import math

IMAGE_CHUNK_SIZE = 1024
SEPARATOR = b"||"  # used to split header from data
WINDOW_SIZE = 20     # Number of packets to send concurrently

def send_window(sock, addr, packets, window_size, max_retries=10, ack_timeout=30):
    """
    Sends packets using a sliding window protocol. ACKs may arrive out-of-order.
    Only unacknowledged packets in the current window are resent.
    Returns True if all packets are acknowledged; otherwise, returns False.
    """
    acked = set()
    retries = {seq: 0 for seq in packets.keys()}
    total_packets = len(packets)
    
    while len(acked) < total_packets:
        # Build current window: select up to window_size unacknowledged packets (lowest seq first)
        window = [seq for seq in sorted(packets.keys()) if seq not in acked][:window_size]
        
        # Send each unacknowledged packet in the window.
        for seq in window:
            try:
                sock.sendto(packets[seq], addr)
                print(f"Sent packet {seq} (retry {retries[seq]})")
            except Exception as e:
                print(f"Error sending packet {seq}: {e}")
        
        # Wait for ACKs for these packets until timeout.
        sock.settimeout(ack_timeout)
        try:
            while True:
                try:
                    ack, _ = sock.recvfrom(1024)
                except socket.timeout:
                    break  # exit inner loop on timeout
                try:
                    ack_msg = ack.decode().strip()
                except UnicodeDecodeError as ude:
                    print(f"Unicode decode error for ACK: {ude}")
                    continue
                if ack_msg.startswith("ACK:"):
                    try:
                        seq_ack = int(ack_msg.split(":")[1])
                        if seq_ack in packets and seq_ack not in acked:
                            acked.add(seq_ack)
                            print(f"Received ACK for packet {seq_ack}")
                        else:
                            print(f"Received duplicate or unknown ACK: {ack_msg}")
                    except Exception as e:
                        print("Error parsing ACK:", e)
                # Break if all packets in the current window are acknowledged.
                if all(seq in acked for seq in window):
                    break
        except Exception as e:
            print(f"Error during ACK receiving: {e}")
        finally:
            sock.settimeout(None)
        
        # For each packet in the window that did not get an ACK, increment its retry count.
        for seq in window:
            if seq not in acked:
                retries[seq] += 1
                print(f"Packet {seq} did not receive ACK, retry count is now {retries[seq]}.")
                if retries[seq] >= max_retries:
                    print(f"Packet {seq} failed after {max_retries} retries.")
                    return False
    return True

def image_send(sock, addr, image_path):
    try:
        file_size = os.path.getsize(image_path)
        total_packets = math.ceil(file_size / IMAGE_CHUNK_SIZE)
        overall_md5 = hashlib.md5()
        
        # Send start packet.
        start_packet = f"START:{total_packets}".encode()
        if not send_with_ack(sock, start_packet, addr, "ACK:START"):
            print("Failed to receive ACK for START packet.")
            return False
        
        # Build packets dictionary.
        packets = {}
        with open(image_path, "rb") as image_file:
            seq = 1
            while True:
                chunk = image_file.read(IMAGE_CHUNK_SIZE)
                if not chunk:
                    break
                overall_md5.update(chunk)
                # Compute per-packet checksum.
                packet_checksum = hashlib.md5(chunk).hexdigest()
                # Prepend a marker "DATA:" so the header is clearly identified.
                header = f"DATA:SEQ:{seq}:CHK:{packet_checksum}:".encode()
                packet = header + SEPARATOR + chunk
                packets[seq] = packet
                seq += 1
        
        # Send data packets using sliding window.
        if not send_window(sock, addr, packets, WINDOW_SIZE):
            print("Sliding window transmission failed. Sending TRANSFER_ERROR.")
            try:
                sock.sendto(b"TRANSFER_ERROR", addr)
            except Exception as e:
                print(f"Error sending TRANSFER_ERROR: {e}")
            return False
        
        # Signal end-of-data.
        if not send_with_ack(sock, b"END", addr, "ACK:END"):
            print("Failed to receive ACK for END packet.")
            return False
        
        # Send overall checksum.
        overall_checksum = overall_md5.hexdigest()
        if not send_with_ack(sock, overall_checksum.encode(), addr, "ACK:CHECKSUM"):
            print("Failed to receive ACK for checksum packet.")
            return False
        
        print(f"Sent image with overall checksum {overall_checksum} to {addr}, total packets: {total_packets}")
        return True
    except Exception as e:
        print(f"Error in image_send: {e}")
        return False

def image_server():
    host = "0.0.0.0"
    port = 6000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.bind((host, port))
    print("UDP Image Server started on port", port)

    artifacts_dir = "artifacts"
    os.makedirs(artifacts_dir, exist_ok=True)

    try:
        while True:
            try:
                data, addr = sock.recvfrom(1024)
            except Exception as e:
                print(f"Error receiving command: {e}")
                continue
            message = data.decode().strip()
            print(f"Received from {addr}: {message}")

            if message.lower() == 'q':
                print("Quit command received. Shutting down image server.")
                break

            if message == "get_image":
                # Generate image.
                unique_id = uuid.uuid4().hex
                image_filename = f"lunar_image_{unique_id}.png"
                image_path = os.path.join(artifacts_dir, image_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
                generated_path = generate_lunar_image(image_path, rover_prompt)

                # Attempt to send the image until the client confirms success,
                # or maximum resend attempts are reached.
                resend_attempts = 0
                max_resend_attempts = 3
                while resend_attempts < max_resend_attempts:
                    print("Sending image...")
                    if not image_send(sock, addr, generated_path):
                        print("Image send failed. Sending TRANSFER_ERROR and retrying transfer.")
                        try:
                            sock.sendto(b"TRANSFER_ERROR", addr)
                        except Exception as e:
                            print(f"Error sending TRANSFER_ERROR: {e}")
                        resend_attempts += 1
                        continue
                    
                    # Wait for final confirmation from client.
                    sock.settimeout(60)
                    try:
                        resp, _ = sock.recvfrom(1024)
                        resp_msg = resp.decode().strip()
                        if resp_msg == "RESEND":
                            print("Client requested a resend.")
                            resend_attempts += 1
                        elif resp_msg == "IMAGE_OK":
                            print("Client confirmed successful image receipt.")
                            break
                        else:
                            print("Received unknown response:", resp_msg)
                            break
                    except socket.timeout:
                        print("No final confirmation received. Assuming image received successfully.")
                        break
                    except Exception as e:
                        print(f"Error receiving final confirmation: {e}")
                        break
                    finally:
                        sock.settimeout(None)
                if resend_attempts >= max_resend_attempts:
                    print("Maximum resend attempts reached. Aborting image transmission.")
    except Exception as e:
        print(f"Server encountered an error: {e}")
    finally:
        sock.close()
        print("Image Server closed.")
