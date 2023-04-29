import socket
import pickle
import random
import threading

peers = {}
server_ip = "localhost"
server_port = 42001
listening_ip = socket.gethostbyname(socket.gethostname())
listening_port = random.randint(49152, 65536)
listening_address = (listening_ip, listening_port)
lock = threading.Lock()
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def is_valid_input(guess: str) -> bool:
    if len(guess) != 3:
        return False
    if not guess.isdigit():
        return False
    if len(set(guess)) != 3:
        return False
    return True

def baseball_game(guess: str, problem: str) -> tuple:
    strikes = 0
    balls = 0
    for i in range(3):
        if guess[i] == problem[i]:
            strikes += 1
        elif guess[i] in problem:
            balls += 1
    return (strikes, balls)

def help() -> None:
    print("help: lookup command (display all possible commands and their description)")
    print("online_users: send a request to the register server, get back a list of all online peers and display them on the screen")
    print("connect [ip] [port]: request to play a game with the given IP and port")
    print("disconnect [peer]: end your game session with the listed peer")
    print("guess [peer] [your guessing number]: send a guessing number to the peer that you've already initiated a game with via the \"connect\" command ")
    print("logoff: send a message (notification) to register server for logging off")

def online_users() -> None:
    client_socket.send("online_users".encode())
    online_users = pickle.loads(client_socket.recv(1024))
    print(online_users)

def connect(ip: str, port: int) -> None:
    peer = hash((ip, port))
    lock.acquire()
    peers[peer] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lock.release()
    peers[peer].connect((ip, port))
    print("Connected to peer:", peer)

def disconnect(peer: int) -> None:
    peers[peer].send("disconnect".encode())
    peers[peer].close()
    print("Disconnected to peer", peer)

def guess(peer: int, guessing_number: str) -> None:
    peers[peer].send(("guess" + guessing_number).encode())
    result = peers[peer].recv(32).decode()
    if result == "The answer is correct.":
        print(result)
        disconnect(peer)
    else:
        print(result)

def logoff() -> None:
    client_socket.send("logoff".encode())
    client_socket.close()
    for i in peers:
        disconnect(i)

def handle_client(connection_socket: socket.socket) -> None:
    print("\nNew game has started.")
    game = "".join(random.sample("0123456789", 3))
    while True:
        command = connection_socket.recv(32).decode()
        if command == "disconnect":
            print("User has disconnected.")
            print("Enter your command: ")
            connection_socket.close()
            break
        elif command[:5] == "guess":
            guess = command[5:]
            strikes, balls = baseball_game(guess, game)
            if strikes == 3:
                connection_socket.send("The answer is correct.".encode())
            else:
                connection_socket.send(f"{strikes} strike(s), {balls} ball(s)".encode())
            print("User has guessed")
            print("Enter your command: ")

def listen_for_connections():
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_socket.bind(listening_address)
    listening_socket.listen()
    while True:
        connection_socket, client_address = listening_socket.accept()
        t = threading.Thread(target=handle_client, args=(connection_socket, ))
        t. daemon = False
        t.start()

def main() -> None:
    client_socket.connect((server_ip,server_port))
    client_socket.send(pickle.dumps(listening_address))
    t = threading.Thread(target=listen_for_connections)
    t. daemon = True
    t.start()
    while True:
        command = input("Enter your command: ").split()
        if command[0] == "help":
            help()
        elif command[0] == "online_users":
            online_users()
        elif command[0] == "connect":
            if len(command) != 3:
                continue
            connect(command[1], int(command[2]))
        elif command[0] == "disconnect":
            if len(command) != 2:
                continue
            disconnect(int(command[1]))
        elif command[0] == "guess":
            if len(command) != 3:
                continue
            guess(int(command[1]), command[2])
        elif command[0] == "logoff":
            logoff()
            break
        else:
            print("Type help to see list of commands")

if __name__ == "__main__":
    main()
