# server.py
import socket
import threading
import time
import queue

HOST = '127.0.0.1'
PORT = 55555
q= queue.Queue()

def thread2():
    global apelido
    lasttime_ping = time.time()
    while True:
        #envia a data e hora a cada 60 segundos
        if time.time() - lasttime_ping > 60:
            timenow = time.localtime()
            tempo = f"{timenow.tm_hour}:{timenow.tm_min}:{timenow.tm_sec}"
            if conn:
                conn.sendall(f"DATA: {tempo}".encode('utf-8'))
            lasttime_ping = time.time()
            print(f"Horário: {tempo}")

        #processa a fila de mensagens
        if not q.empty():
            mensagem_do_cliente = q.get().strip() #.strip remove espaço extra
            
            #lógica para comandos e mensagens
            if mensagem_do_cliente.startswith(":nome "):
                novo_nome = mensagem_do_cliente.split(" ", 1)[1]
                apelido = novo_nome
                print(f"Nome do usuário alterado para: {apelido}")
                
            elif mensagem_do_cliente == ":quit":
                print(f"Usuário {apelido} solicitou desconexão.")

                conn.close()
                break

            else:
                # É uma mensagem normal, não um comando
                timenow = time.localtime()
                horario = f"{timenow.tm_hour}:{timenow.tm_min}:{timenow.tm_sec}"
                
                # Resposta para o próprio cliente (o "eco")
                eco = f"{mensagem_do_cliente}"
                if conn:
                    conn.sendall(f"{eco}".encode('utf-8'))
                
                # Mensagem que seria enviada a todos os usuários (por enquanto, apenas imprimimos)
                mensagem_formatada = f"{apelido} ({horario}): {mensagem_do_cliente}"
                print(f"{mensagem_formatada}")



def thread1():
    while True:

        #recebe dados do cliente, 1024 é o tamanho máx do pacote
        dados = conn.recv(1024)

        #se receber dados vazios, o cliente encerrou a conexão
        if not dados:
            break

        # decodifica e exibe a mensagem
        mensagem = dados.decode('utf-8')
        q.put(mensagem)

        # envia uma resposta genérica de volta
    print("Conexão encerrada.")



#cria um obj socket, o socket.AF_INET significa que estamos usando endereços IPv4 e o socket.SOCK_STREAM significa que estamos usando TCP e o with garante que o socket será fechado corretamente depois do bloco de código
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))  # vincula o socket ao endereço e porta definidos
    s.listen()  # coloca o socket em modo de escuta
    print(f"Servidor escutando em {HOST}:{PORT}")


    conn, addr = s.accept()  # aceita uma conexão de um cliente
    #conn é o novo socket que será usado para a comunicação com o cliente, e addr é uma tupla com o endereço do cliente que se conectou

    #usa o novo socket para comunicação

    with conn:
        print(f"Conectado por {addr}")
        timenow = time.localtime()
        tempo= f"CONECTADO!!"
        conn.sendall(tempo.encode('utf-8'))
        print(tempo)

        apelido = conn.recv(1024).decode('utf-8')
        print(f"Novo cliente conectado: {apelido}")
        thread_recepcao = threading.Thread(target=thread2)
        thread_recepcao.start()
        thread_insercao = threading.Thread(target=thread1)
        thread_insercao.start()
        thread_recepcao.join()
        thread_insercao.join()



