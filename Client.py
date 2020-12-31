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
    """ The function sends the user's pressed keys to the server

    Args:
        tcp_sock (socket): The socket that is used for connection between Clien and Server
    """
    global game_on
    while game_on:
        try:
            # Get the pressed key from the user
            key = keyboard.read_key()
            if key:
                send_key = bytes(key, 'utf-8')
                # Send the pressed key to the server
                tcp_sock.sendall(send_key)
        except:
            break


def set_clients_socket():
    """ The function creats the socket that will make for a connection between client and Server

    Returns:
        socket: the socket that is used for the connection
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Enable port reusage so we will be able to run multiple clients and servers on single (host, port). 
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Enable broadcasting mode
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", udp_port))
    print('Client started, listening for offer requests...')
    
    return client

def main():
    while True:
        # Create a UDP socket
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
            # Create a TCP socket
            tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('localhost', tcp_port)
            # Connect the socket to the address where the server is listening
            tcp_sock.connect(server_address)
            try:              
                team=input('Enter Your Team Name:')
                message = bytes(team,'utf-8')
                 # Send the team name to the server
                tcp_sock.sendall(message)
                # Receive welcome message from the server
                welcome = tcp_sock.recv(1024)
                print(welcome.decode("utf-8"))

                # Use a separate thread for the key presses
                key_thread = threading.Thread(name="t1", target=send_keys, args=(tcp_sock,))
                key_thread.setDaemon(True)
                key_thread.start()
                    # key = getch.getch() 
                    # str_key = str(key)
                # Wait for the game to end
                time.sleep(10)
                game_on = False
                time.sleep(5)
                print('Server disconnected, listening for offer requests...')

                # Wait for all of the threads to be over
                time.sleep(10)
                tcp_sock.close()
                break

            except:
                tcp_sock.close()
                break


if __name__ == "__main__":
    main()
