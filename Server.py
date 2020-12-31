# "C:/Users/Danielle Lavi/AppData/Local/Programs/Python/Python37/python.exe" "c:/Users/Danielle Lavi/Desktop/תקשורת/Hackathon/Server.py"

import socket
import time
import struct
import threading 
import selectors
# from scapy.arch import get_if_addr



group1 = {}
group2 = {}
group1['score'] = 0
group2['score'] = 0
start_time = time.time()
game_on = True
udp_port = 13117
tcp_port = 2095
# host =  get_if_addr('eth1')
 
# 1.open TCP socket and listen 
def tcp_connect():
    #sel = selectors.DefaultSelector()
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', tcp_port)
    # server_address = (host, tcp_port)
    tcp_socket.bind(server_address)
    # tcp_socket.listen(1)
#    tcp_socket.setblocking(0)
    #sel.register(tcp_socket, selectors.EVENT_READ, data=None)
    return tcp_socket

# The first socket - broadcasting the offers
def broadcast():
    global game_on
    broadcasting_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Enable port reusage so we will be able to run multiple clients and servers on single (host, port). 
    broadcasting_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Enable broadcasting mode
    broadcasting_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # Set a timeout so the socket does not block indefinitely when trying to receive data.
    # broadcasting_socket.settimeout(10)
    if game_on:
        while time.time() - start_time < 10:
            server_offer(broadcasting_socket)
            time.sleep(1)
    else:
         while True:
            server_offer(broadcasting_socket)
            time.sleep(1)
        
    broadcasting_socket.close()
   

 
   
def server_offer(broadcasting_socket):

    magic_cookie = 0xfeedbeef
    message_type= 0x2
    dest_port = udp_port
    message = struct.pack('QQQ',magic_cookie ,message_type, dest_port)
    broadcasting_socket.sendto(message, ('<broadcast>', dest_port))
    # print("message sent!")
    
# def tcp_connection():
#     while True:
#         # Wait for a connection
#         connection, client_address = tcp_socket.accept()

#         # Receive the data in small chunks and retransmit it
#         while True:
#             data = connection.recv(16)
#             print(data)
def single_player(group, client):
    try:
        client_connection = group[client][1]
        # client_connection.settimeout(40)
        while game_on:
            client_msg = client_connection.recv(1024)
            group['score'] += 1
    except:
        return


def print_end_of_game():
    winners = None
    group1_score = int(group1['score']/2)
    group2_score = int(group2['score']/2)

    msg = f'Game over!\nGroup 1 typed in {group1_score} characters. Group 2 typed in {group2_score} characters.\n'
    if group1['score'] > group2['score']:
        winners = group1
        msg += 'Group 1 wins!'
    elif group2['score'] > group1['score']:
        winners = group2
        msg += 'Group 2 wins!'
    else:
        msg += 'Its a tie!'
        print(msg)
        return
    msg += 'Congratulations to the winners:\n ==\n'
    for client in winners:
        if client == 'score':
            continue
        msg += winners[client][0] + '\n'

    print(msg)

def start_playing():
    global game_on
    for client in group1:
        if client == 'score':
            continue
        game_thread = threading.Thread(name="t1", target=single_player, args=(group1, client))
        game_thread.setDaemon(True)
        game_thread.start()
    for client in group2:
        if client == 'score':
            continue
        game_thread = threading.Thread(name="t1", target=single_player, args=(group2, client))
        game_thread.setDaemon(True)
        game_thread.start()

    time.sleep(10)
    game_on = False
    print_end_of_game()

def finish_playing():
    for client in group1:
        if client == 'score':
            continue
        client_connection = group1[client][1]
        client_connection.close()
    for client in group2:
        if client == 'score':
            continue
        client_connection = group2[client][1]
        client_connection.close()
    time.sleep(5)
    print('Game over, sending out offer requests...')
    time.sleep(10)


def run_server():
        # Listen for incoming connections
    tcp_socket = tcp_connect()
    tcp_socket.listen()
    tcp_socket.settimeout(10)
    hostname = socket.gethostname()
    dns_resolved_addr = socket.gethostbyname(hostname)
    print(f"Server started, listening on IP address {dns_resolved_addr}")
    broadcastT = threading.Thread(name="t1", target=broadcast)
    broadcastT.setDaemon(True)
    broadcastT.start()

    while time.time() - start_time < 10:
        tcp_socket.listen()
        # Wait for a connection
        try:
            conn_socket, client_address = tcp_socket.accept()
        except:
            break
        #conn_socket.setblocking(False)
        try:
            # Receive the data in small chunks and retransmit it
            # while time.time() - start_time < 10:
            team_name = conn_socket.recv(1024)
            if team_name:
                if len(group1) > len(group2):
                    group2[client_address]=[team_name.decode('utf-8'),conn_socket,0]
                        # aa='welcome team ' + team_name.decode('utf-8') + ' your in group 1'
                        # message = bytes(aa,'utf-8')                      
                else:
                    group1[client_address]=[team_name.decode('utf-8'),conn_socket,0]
                    #     aa='welcome team ' +team_name.decode('utf-8') + ' your in group 1'
                    #     message = bytes(aa,'utf-8')
                    # conn_socket.sendall(message)
                                           
            else:
                err_msg='no name was sent ,connection is closing...'
                conn_socket.sendall(bytes(err_msg,'utf-8'))
                print(err_msg)
                break
        except:
            print("some error ocuured, closing connection")
            # conn_socket.close()
        # finally:
        #     # Clean up the connection
        #     conn_socket.close()
    msg = f'Welcome to Keyboard Spamming Battle Royale.\n Group 1:\n ==\n'
    
    for client in group1:
        if client == 'score':
            continue
        msg += f'{group1[client][0]}\n'
    msg += 'Group 2:\n ==\n'
    for client in group2:
        if client == 'score':
            continue
        msg += f'{group2[client][0]}\n'
    msg += 'Start pressing keys on your keyboard as fast as you can!!'
    for client in group1:
        if client == 'score':
            continue
        group1[client][1].send(bytes(msg,'utf-8'))
    for client in group2:
        if client == 'score':
            continue
        group2[client][1].send(bytes(msg,'utf-8'))

    start_playing()
    finish_playing()
    
    # broadcast()
    
    # broadcastFT = threading.Thread(name="t1", target=broadcast)
    # broadcastFT.setDaemon(True)
    # broadcastFT.start()


def main():
    while True:
    #     run_server()
       # Listen for incoming connections
        global group1
        group1 = {}
        global group2
        group2 = {}
        group1['score'] = 0
        group2['score'] = 0
        start_time = time.time()
        game_on = True
        tcp_socket = tcp_connect()
        tcp_socket.listen()
        tcp_socket.settimeout(10)
        hostname = socket.gethostname()
        dns_resolved_addr = socket.gethostbyname(hostname)
        print(f"Server started, listening on IP address {dns_resolved_addr}")
        broadcastT = threading.Thread(name="t1", target=broadcast)
        broadcastT.setDaemon(True)
        broadcastT.start()

        while time.time() - start_time < 10:
            tcp_socket.listen()
            # Wait for a connection
            try:
                conn_socket, client_address = tcp_socket.accept()
            except:
                break
            #conn_socket.setblocking(False)
            try:
                # Receive the data in small chunks and retransmit it
                # while time.time() - start_time < 10:
                team_name = conn_socket.recv(1024)
                if team_name:
                    if len(group1) > len(group2):
                        group2[client_address]=[team_name.decode('utf-8'),conn_socket,0]
                            # aa='welcome team ' + team_name.decode('utf-8') + ' your in group 1'
                            # message = bytes(aa,'utf-8')                      
                    else:
                        group1[client_address]=[team_name.decode('utf-8'),conn_socket,0]
                        #     aa='welcome team ' +team_name.decode('utf-8') + ' your in group 1'
                        #     message = bytes(aa,'utf-8')
                        # conn_socket.sendall(message)
                                            
                else:
                    err_msg='no name was sent ,connection is closing...'
                    conn_socket.sendall(bytes(err_msg,'utf-8'))
                    print(err_msg)
                    break
            except:
                print("some error ocuured, closing connection")
                # conn_socket.close()
            # finally:
            #     # Clean up the connection
            #     conn_socket.close()
        msg = f'Welcome to Keyboard Spamming Battle Royale.\n Group 1:\n ==\n'
        
        for client in group1:
            if client == 'score':
                continue
            msg += f'{group1[client][0]}\n'
        msg += 'Group 2:\n ==\n'
        for client in group2:
            if client == 'score':
                continue
            msg += f'{group2[client][0]}\n'
        msg += 'Start pressing keys on your keyboard as fast as you can!!'
        for client in group1:
            if client == 'score':
                continue
            group1[client][1].sendall(bytes(msg,'utf-8'))
        for client in group2:
            if client == 'score':
                continue
            group2[client][1].sendall(bytes(msg,'utf-8'))

        start_playing()
        finish_playing()
        tcp_socket.close()
        



if __name__ == "__main__":
    main()
