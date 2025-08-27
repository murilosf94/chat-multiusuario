#server.py
import socket
import threading
import time

HOST = '127.0.0.1'
PORT = 65432        

#cria um obj socket, o socket.AF_INET significa que estamos usando endereços IPv4 e o socket.SOCK_STREAM significa que estamos usando TCP e o with garante que o socket será fechado corretamente depois do bloco de código
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))#vincula o socket ao endereço e porta definidos
    s.listen()#coloca o socket em modo de escuta
    print(f"Servidor escutando em {HOST}:{PORT}")
    timenow=time.time()
    printf(f"{timenow}")
    
    conn, addr = s.accept()#aceita uma conexão de um cliente
    #conn é o novo socket que será usado para a comunicação com o cliente, e addr é uma tupla com o endereço do cliente que se conectou
    
    #usa o novo socket para comunicação

    with conn:
        print(f"Conectado por {addr}")
        
        
        apelido = conn.recv(1024).decode('utf-8')
        print(f"Novo cliente conectado: {apelido}")

        #loop infinito para o server ainda receber mensagens
        while True:
            #recebe dados do cliente, 1024 é o tamanho máx do pacote
            dados = conn.recv(1024)

            #se receber dados vazios, o cliente encerrou a conexão
            if not dados:
                break
            
            #decodifica e exibe a mensagem
            mensagem = dados.decode('utf-8')
            print(f"{apelido}: {mensagem}")

            #envia uma resposta genérica de volta
            resposta = f"{mensagem}"
            conn.sendall(resposta.encode('utf-8'))
            
    print("Conexão encerrada.")