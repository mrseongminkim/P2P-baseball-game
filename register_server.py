import socket
import threading
import pickle

server_ip = 'localhost'
server_port = 42001
online_users = {}
lock = threading.Lock()

def handle_client(connection_socket: socket.socket) -> None:
    print("New user has joined the server.")
    client_information = pickle.loads(connection_socket.recv(32))
    user_id = hash(client_information)
    lock.acquire()
    online_users[user_id] = (user_id, client_information[0], client_information[1])
    lock.release()
    while True:
        command = connection_socket.recv(16).decode()
        if command == "online_users":
            print("User has requested list of online users")
            lock.acquire()
            del online_users[user_id]
            connection_socket.send(pickle.dumps(online_users))
            online_users[user_id] = client_information
            lock.release()
        elif command == "logoff":
            print("User has left the server.")
            connection_socket.close()
            lock.acquire()
            del online_users[user_id]
            lock.release()
            break

def main() -> None:
    #IPv4 and TCP socekt
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (server_ip, server_port)
    #Associate IP and Port number with server_socket
    server_socket.bind(server_address)
    #Enable a server to accept connections
    server_socket.listen()
    print('Server is starting up on {} port {}.'.format(*server_address))
    while True:
        connection_socket, client_address = server_socket.accept()
        t = threading.Thread(target=handle_client, args=(connection_socket, ))
        t. daemon = False
        t.start()

if __name__ == "__main__":
    main()
