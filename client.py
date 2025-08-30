# client.py
import socket
import threading
import time

HOST = '127.0.0.1'
PORT = 55555


def imprimirtempo():
    while True:
        tempoagora = s.recv(1024)
        print(f"{tempoagora.decode('utf-8')}")
        break


def mandarcomando(s):
    while True:

        # pede para o usuário digitar a mensagem
        mensagem = input("> ")

        # se a mensagem for ':quit', o cliente encerra a conexão
        if mensagem.lower() == ':quit':
            break

        # envia a mensagem codificada em bytes
        s.sendall(mensagem.encode('utf-8'))

        # aguarda e recebe a resposta do servidor
        dados = s.recv(1024)
        print(f"Você digitou: {dados.decode('utf-8')}")  # exibe a resposta do servidor



# cria um obj socket, o socket.AF_INET significa que estamos usando endereços IPv4 e o socket.SOCK_STREAM significa que estamos usando TCP e o with garante que o socket será fechado corretamente depois do bloco de código
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        # tenta conectar ao servidor, se o servidor não stiver rodando, essa linha falha
        s.connect((HOST, PORT))
        print("Conectado ao servidor. Digite suas mensagens. (Digite ':quit' para fechar a conexão)")

        apelido = input("Digite seu apelido: ")
        if(apelido == ""):
            apelido = s.getsockname()[0]
        s.sendall(apelido.encode('utf-8'))
        thread_recepcao = threading.Thread(target=imprimirtempo)
        thread_recepcao.start()
        thread_insercao = threading.Thread(target=mandarcomando, args=(s,))
        thread_insercao.start()
        thread_recepcao.join()
        thread_insercao.join()

        # loop infinito para o cliente ainda enviar mensagens

    except ConnectionRefusedError:
        print("Não foi possível conectar. Verifique se o servidor está em execução.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")