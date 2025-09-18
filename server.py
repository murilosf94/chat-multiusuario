#server.py
import socket
import threading
import time
import sys

HOST = '127.0.0.1'
PORTA = 55555

clientes_conectados = []
apelidos = []
trava_clientes = threading.Lock()

def obter_horario_atual():
    """Retorna o horário formatado como HH:MM:SS."""
    return time.strftime("%H:%M:%S", time.localtime())

def transmitir(mensagem, conexao_remetente=None):
    """Envia uma mensagem para todos os clientes, exceto o remetente."""
    clientes_a_remover = []
    with trava_clientes:
        for conexao_cliente in list(clientes_conectados):
            if conexao_cliente != conexao_remetente:
                try:
                    conexao_cliente.sendall(mensagem.encode('utf-8'))
                except:
                    clientes_a_remover.append(conexao_cliente)

    for conn in clientes_a_remover:
        remover_cliente(conn)

def remover_cliente(conn):
    """Remove um cliente das listas e avisa a todos sobre a saída."""
    apelido_removido = None
    with trava_clientes:
        if conn in clientes_conectados:
            indice = clientes_conectados.index(conn)
            apelido_removido = apelidos.pop(indice)
            clientes_conectados.remove(conn)
            print(f"Usuário '{apelido_removido}' se desconectou.")
    
    try:
        conn.close()
    except:
        pass

    if apelido_removido:
        transmitir(f"{apelido_removido} saiu do chat.", None)


def gerenciar_cliente(conn, addr):
    print(f"Nova conexão de {addr}")
    
    mensagem_boas_vindas = f"{obter_horario_atual()}: CONECTADO!! Por favor, informe seu apelido."
    conn.sendall(mensagem_boas_vindas.encode('utf-8'))

    try:
        apelido = conn.recv(1024).decode('utf-8').strip()
        if not apelido:
            apelido = f"Anônimo_{addr[1]}"

        with trava_clientes:
            clientes_conectados.append(conn)
            apelidos.append(apelido)
        
        print(f"Cliente {addr} definiu o apelido como '{apelido}'.")
        transmitir(f"{apelido} entrou no chat.", conn)
        conn.sendall("Você entrou no chat!".encode('utf-8'))

    except Exception as e:
        print(f"Erro ao configurar apelido para {addr}: {e}")
        conn.close()
        return

    try:
        while True:
            mensagem = conn.recv(1024).decode('utf-8')
            if not mensagem:
                break

            if mensagem.startswith(':'):
                if mensagem.lower() == ':quit':
                    break
                elif mensagem.lower().startswith(':nome '):
                    try:
                        novo_apelido = mensagem.split(" ", 1)[1].strip()
                        if novo_apelido:
                            antigo_apelido = ""
                            with trava_clientes:
                                #pega o nome antigo e atualiza para o novo na lista global
                                indice = clientes_conectados.index(conn)
                                antigo_apelido = apelidos[indice]
                                apelidos[indice] = novo_apelido
                            
                            #atualiza o apelido local para esta thread
                            apelido = novo_apelido

                            mensagem_notificacao = f"{antigo_apelido} agora é conhecido como {novo_apelido}."
                            
                            #log no console do servidor para verificação
                            print(f"AVISO DE NOME: {mensagem_notificacao}")

                            #envia a notificação para TODOS os clientes, incluindo quem mudou
                            transmitir(mensagem_notificacao, None)
                        else:
                             conn.sendall("Nome não pode ser vazio.".encode('utf-8'))
                    except IndexError:
                        conn.sendall("Comando de nome inválido. Use :nome <novo_nome>".encode('utf-8'))
                else:
                    conn.sendall(f"Comando '{mensagem}' desconhecido.".encode('utf-8'))
            else:
                mensagem_eco = f"Voce digitou: {mensagem}"
                conn.sendall(mensagem_eco.encode('utf-8'))
                
                mensagem_formatada = f"{apelido} ({obter_horario_atual()}): {mensagem}"
                print(mensagem_formatada)
                transmitir(mensagem_formatada, conn)

    except (ConnectionResetError, ConnectionAbortedError):
        print(f"Conexão com {apelido} perdida abruptamente.")
    finally:
        remover_cliente(conn)

def enviar_horario_periodicamente():
    while True:
        time.sleep(60)
        mensagem_horario = f"HORARIO DO SERVIDOR ({obter_horario_atual()})"
        transmitir(mensagem_horario, None)

def iniciar_servidor(limite):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((HOST, PORTA))
        servidor.listen()
        print(f"Servidor escutando em {HOST}:{PORTA} com limite de {limite} clientes.")

        thread_horario = threading.Thread(target=enviar_horario_periodicamente, daemon=True)
        thread_horario.start()

        while True:
            conn, addr = servidor.accept()
            with trava_clientes:
                if len(clientes_conectados) >= limite:
                    print(f"Conexão de {addr} recusada. Limite atingido.")
                    conn.sendall("Limite de clientes atingido.".encode('utf-8'))
                    conn.close()
                    continue
            
            thread_cliente = threading.Thread(target=gerenciar_cliente, args=(conn, addr))
            thread_cliente.start()

if __name__ == "__main__":
    try:
        limite_clientes = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    except (IndexError, ValueError):
        print("Uso: python servidor.py <limite_de_clientes>")
        limite_clientes = 5
    iniciar_servidor(limite_clientes)