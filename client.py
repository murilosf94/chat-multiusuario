# client.py
import socket
import threading
import time
import sys
import os

HOST = '127.0.0.1'
PORT = 55555
PORT2 = 55556
PORT3 = 55557


def imprimirtempo():
    while True:
        tempoagora = s3.recv(1024)
        print(f"{tempoagora.decode('utf-8')}")



def mandarcomando(s):

    while True:

        # pede para o usuário digitar a mensagem
        mensagem = input("")

        # se a mensagem for ':quit', o cliente encerra a conexão


        # envia a mensagem codificada em bytes
        s2.sendall(mensagem.encode('utf-8'))
        if mensagem == ":quit":
            print("programa encerrado")
            exit()


        # aguarda e recebe a resposta do servidor

        dados = s2.recv(1024)
        dados2 = dados.decode('utf-8')
        if dados2 != " ":
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
        tempoagora = s.recv(1024)
        print(f"{tempoagora.decode('utf-8')}")


        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.connect((HOST, PORT2))
        s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s3.connect((HOST, PORT3))
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