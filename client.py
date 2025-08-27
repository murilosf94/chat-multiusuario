#client.py
import socket


HOST = '127.0.0.1'
PORT = 65432        

#cria um obj socket, o socket.AF_INET significa que estamos usando endereços IPv4 e o socket.SOCK_STREAM significa que estamos usando TCP e o with garante que o socket será fechado corretamente depois do bloco de código
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        #tenta conectar ao servidor, se o servidor não stiver rodando, essa linha falha
        s.connect((HOST, PORT))
        print("Conectado ao servidor. Digite suas mensagens. (Digite 'sair' para fechar a conexão)")

        apelido = input("Digite seu apelido: ")
        s.sendall(apelido.encode('utf-8'))
        
        #loop infinito para o cliente ainda enviar mensagens
        while True:
            #pede para o usuário digitar a mensagem
            mensagem = input("> ")

            #se a mensagem for 'sair', o cliente encerra a conexão
            if mensagem.lower() == 'sair':
                break

            #envia a mensagem codificada em bytes
            s.sendall(mensagem.encode('utf-8'))

            #aguarda e recebe a resposta do servidor
            dados = s.recv(1024)
            print(f"Você digitou: {dados.decode('utf-8')}")#exibe a resposta do servidor

    except ConnectionRefusedError:
        print("Não foi possível conectar. Verifique se o servidor está em execução.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")