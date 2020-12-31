# "C:/Users/Danielle Lavi/AppData/Local/Programs/Python/Python37/python.exe" "c:/Users/Danielle Lavi/Desktop/תקשורת/Hackathon/Client.py"

import socket
import struct
import keyboard
import time
import threading
# import getch


game_on = True
udp_port = 13117
tcp_port = 2095

def send_keys(tcp_sock):
    global game_on
    # start_time = time.time()
    while game_on:
        try:
            key = keyboard.read_key()
            if key:
            # send_key = bytes(str_key, 'utf-8')
                send_key = bytes(key, 'utf-8')
                tcp_sock.sendall(send_key)
        except:
            break
def set_clients_socket():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP

    # Enable port reusage so we will be able to run multiple clients and servers on single (host, port). 
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Enable broadcasting mode
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", udp_port))
    print('Client started, listening for offer requests...')
    
    return client

def main():
    while True:
        client = set_clients_socket()
        while True:
            data, addr = client.recvfrom(1024)
            message = struct.unpack('QQQ', data)
            # If the magic cookie is wrong the connection wont be established
            if message[0] != 0xfeedbeef:
                print('This message is rejected because a wrong cookie was sent')
                break
            # If the message type is wrong the connection wont be established
            if message[1] != 0x2:
                print('This message type is not supported')
                break
            # Create a TCP/IP socket
            tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect the socket to the port where the server is listening
            server_address = ('localhost', tcp_port)
            tcp_sock.connect(server_address)
            try:
                # Send data
                team=input('Enter Your Team Name:')
                message = bytes(team,'utf-8')
                tcp_sock.sendall(message)
                welcome = tcp_sock.recv(1024)
                print(welcome.decode("utf-8"))

                # Use a separate thread for the key presses
                key_thread = threading.Thread(name="t1", target=send_keys, args=(tcp_sock,))
                key_thread.setDaemon(True)
                key_thread.start()
                    # key = getch.getch() 
                    # str_key = str(key)
                time.sleep(10)
                game_on = False

                time.sleep(5)
                print('Server disconnected, listening for offer requests...')
                time.sleep(10)
                tcp_sock.close()
                break

            except:
                tcp_sock.close()
                break


if __name__ == "__main__":
    main()
