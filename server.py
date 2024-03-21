import socket
import threading #threading allows multiple users to interact without waiting for other users to send a message

HEADER = 64
FORMAT = 'utf-8'
PORT = 5050 #basically delcaring a port to use to connect to a host
#SERVER = socket.gethostbyname(socket.gethostname())#automatically get the ip address of the device
SERVER = "192.168.0.180"
ADDR = (SERVER,PORT)#declare a tuple
DISCONNECT_MESSAGE= "!DISCONNECT"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#declare an address family and how data will be streamed
server.bind(ADDR)

def handle_client(conn,addr):
    print(f"New connection {addr} made ")
    connected = True
    while connected:
        msg_len = conn.recv(HEADER).decode(FORMAT)
        #print(msg_len)
        if msg_len:
            msg_len=int(msg_len)
            msg=conn.recv(msg_len).decode(FORMAT)
            if msg==DISCONNECT_MESSAGE:
                connected=False
            print(f"{addr} sent {msg}")  
    conn.close()
    
def start():
    server.listen()
    while True:
        conn,addr=server.accept()# get ip and port of the device that connected to this server
        thread = threading.Thread(target=handle_client, args=(conn,addr))#create a thread for the new connection and pass it to handle client function with the arguments conn and addr
        thread.start()
        print(f"Active connections: {threading.active_count()-1}")

print("START PROGRAM IN SERVER ADDRESS: " + SERVER)
start()
