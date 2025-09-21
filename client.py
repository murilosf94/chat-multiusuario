#PROJETO FINAL - CHAT MULTIUSUARIO
#Murilo de Souza Freitas - 23012056
#Gabriel Geraldo Mazolli - 23011007
import socket
import threading
import sys

HOST = '127.0.0.1'
PORTA = 55555

#fica em um loop infinito esperando por mensagens do servidor
def receber_mensagens(socket_cliente):
    """Lida com o recebimento de mensagens do servidor."""
    while True:
        try:
            mensagem = socket_cliente.recv(1024).decode('utf-8') #decodifica a mensagem recebida
            if not mensagem: #se a mensagem for vazia, o servidor fechou a conexao
                print("\nConexão com o servidor foi encerrada.")
                break

            sys.stdout.write('\r' + ' ' * 60 + '\r') #limpa a linha atual
            print(f"{mensagem}")
            sys.stdout.write("> ")
            sys.stdout.flush()

        except (ConnectionAbortedError, ConnectionResetError):
            print("\nConexão com o servidor foi perdida.")
            break

        except Exception as e:
            print(f"\nOcorreu um erro ao receber mensagens: {e}")
            break
    
    print("Pressione ENTER para encerrar o programa.")

#essa thread fica em loop ininito esperando por algum input do usuario
def enviar_mensagens(socket_cliente):
    """Lida com o envio de mensagens para o servidor."""
    while True:
        try:
            sys.stdout.write("> ")
            sys.stdout.flush()
            mensagem = input() #espera o usuario digitar algo

            if mensagem:
                socket_cliente.sendall(mensagem.encode('utf-8')) #codifica a mensagem para o formato de bytes antes de enviar
            
            if mensagem.lower() == ":quit": #se o usuario digitar :quit, desconecta
                print("Desconectando...")
                break
        except (EOFError, KeyboardInterrupt):
            print("\nEnviando comando para desconectar...")
            socket_cliente.sendall(":quit".encode('utf-8'))
            break
        except Exception as e:
            print(f"\nOcorreu um erro ao enviar mensagens: {e}")
            break


def main():
    """Função main para iniciar o cliente."""
    #cria o socket do cliente e tenta conectar ao servidor
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
                apelido = f"Usuário {porta_local}"
            
            socket_cliente.sendall(apelido.encode('utf-8'))

            #inicia as threads de comunicação
            thread_recebimento = threading.Thread(target=receber_mensagens, args=(socket_cliente,))
            thread_envio = threading.Thread(target=enviar_mensagens, args=(socket_cliente,))

            thread_recebimento.start()
            thread_envio.start()

            thread_envio.join() #espera a thread de envio terminar (quando o usuario digitar :quit)
            socket_cliente.close() #fecha o socket do cliente
            thread_recebimento.join() #espera a thread de recebimento terminar
        except ConnectionRefusedError:
            print("Não foi possível conectar. Verifique se o servidor está em execução.")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()