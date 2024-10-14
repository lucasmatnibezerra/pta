import socket
import os
import signal
import sys

#constantes
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 11550
USER_FILE = './users.txt'
FILES_DIR = './files'
SEQ_NUM = 0

#função para carregar usuarios
def load_users():
    with open(USER_FILE, 'r') as f:
        users = [line.strip() for line in f.readlines()]
    return users

#função para manipular o comando CUMP
def handle_cump(user, valid_users):
    if user in valid_users:
        return f"{SEQ_NUM} OK"
    else:
        return f"{SEQ_NUM} NOK"

#função para o comando list 
def handle_list():
    try:
        files = os.listdir(FILES_DIR)
        if not files:
            return f"{SEQ_NUM} NOK"
        files_str = ','.join(files)
        return f"{SEQ_NUM} ARQS {len(files)} {files_str}"
    except Exception as e:
        print(f"Erro ao listar arquivos: {e}")
        return f"{SEQ_NUM} NOK"


#função para o PEGA
def handle_pega(filename):
    file_path = os.path.join(FILES_DIR, filename)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                file_data = f.read()
            file_size = len(file_data)
            return f"{SEQ_NUM} ARQ {file_size} {file_data}"
        except Exception as e:
            print(f"Erro ao ler arquivo: {e}")
            return f"{SEQ_NUM} NOK"
    else:
        return f"{SEQ_NUM} NOK"

#conexão do cliente
def handle_client(client_socket, valid_users):
    global SEQ_NUM

    #CUMP inicial 
    data = client_socket.recv(1024).decode()
    parts = data.split()
    SEQ_NUM = int(parts[0])  #sequencia de números
    command = parts[1]
    
    if command == "CUMP":
        user = parts[2]
        response = handle_cump(user, valid_users)
        client_socket.send(response.encode())
        if "NOK" in response:
            client_socket.close()
            return
    else:
        client_socket.send(f"{SEQ_NUM} NOK".encode())
        client_socket.close()
        return
    
    #comunicação entre o servidor e o cliente
    while True:
        try:
            data = client_socket.recv(1024).decode()
            parts = data.split()
            if len(parts) < 2:
                client_socket.send(f"{SEQ_NUM} NOK".encode())
                break
            
            SEQ_NUM = int(parts[0])
            command = parts[1]

            if command == "LIST":
                response = handle_list()
                client_socket.send(response.encode())
            elif command == "PEGA":
                filename = parts[2]
                response = handle_pega(filename)
                client_socket.send(response.encode())
            elif command == "TERM":
                client_socket.send(f"{SEQ_NUM} OK".encode())
                client_socket.close()
                break
            else:
                client_socket.send(f"{SEQ_NUM} NOK".encode())
        except Exception as e:
            print(f"Error handling client: {e}")
            client_socket.send(f"{SEQ_NUM} NOK".encode())
            client_socket.close()
            break
#ctrl + c para parar o servidor
def signal_handler(sig, frame):
    print("\n[*] desligando server...")
    sys.exit(0)

# Capturando o sinal de interrupção
signal.signal(signal.SIGINT, signal_handler)


#loop do server
def start_server():
    valid_users = load_users()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"[*] Listening on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"[*] Accepted connection from {addr}")
        handle_client(client_socket, valid_users)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    start_server()

    
