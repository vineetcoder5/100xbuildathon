# main_server.py
import socket
from collections import deque

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def start_server():
    # server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 65432))

    print("📋 Server listening for messages...\n")
    
    while True:
        data, _ = server_socket.recvfrom(1024)
        message = data.decode()
        print(f"[Message Recieved] {message.strip()}")
        

if __name__ == "__main__":
    start_server()
