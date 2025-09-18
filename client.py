#client.py
import socket
import threading
import sys

HOST = '127.0.0.1'
PORTA = 55555

def receber_mensagens(socket_cliente):
    """Lida com o recebimento de mensagens do servidor."""
    while True:
        try:
            mensagem = socket_cliente.recv(1024).decode('utf-8')
            if not mensagem:
                print("\nConexão com o servidor foi encerrada.")
                break
            
            sys.stdout.write('\r' + ' ' * 60 + '\r')
            print(f"{mensagem}")
            sys.stdout.write("> ")
            sys.stdout.flush()

        except (ConnectionAbortedError, ConnectionResetError):
            print("\nConexão com o servidor foi perdida.")
            break
        except Exception:
            break
    
    print("Pressione ENTER para encerrar o programa.")

def enviar_mensagens(socket_cliente):
    """Lida com o envio de mensagens para o servidor."""
    while True:
        try:
            sys.stdout.write("> ")
            sys.stdout.flush()
            mensagem = input()

            if mensagem:
                socket_cliente.sendall(mensagem.encode('utf-8'))
            
            if mensagem.lower() == ":quit":
                print("Desconectando...")
                break
        except (EOFError, KeyboardInterrupt):
            print("\nEnviando comando para desconectar...")
            socket_cliente.sendall(":quit".encode('utf-8'))
            break
        except Exception:
            break

def principal():
    """Função principal para iniciar o cliente."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_cliente:
        try:
            socket_cliente.connect((HOST, PORTA))
            
            mensagem_boas_vindas = socket_cliente.recv(1024).decode('utf-8')
            print(mensagem_boas_vindas)

            if "Limite de clientes" in mensagem_boas_vindas:
                return

            #pergunta o apelido e envia para o servidor
            apelido = input("Digite seu apelido: ")
            if not apelido:
                #usa a porta local do cliente para criar um apelido padrão
                porta_local = socket_cliente.getsockname()[1]
                apelido = f"Anônimo_{porta_local}"
            
            socket_cliente.sendall(apelido.encode('utf-8'))

            #inicia as threads de comunicação
            thread_recebimento = threading.Thread(target=receber_mensagens, args=(socket_cliente,))
            thread_envio = threading.Thread(target=enviar_mensagens, args=(socket_cliente,))

            thread_recebimento.start()
            thread_envio.start()

            thread_envio.join()
            socket_cliente.close()
            thread_recebimento.join()

        except ConnectionRefusedError:
            print("Não foi possível conectar. Verifique se o servidor está em execução.")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    principal()