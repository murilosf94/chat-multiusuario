import socket
import threading
import time
import sys

#endereco
HOST = '127.0.0.1'
PORTA = 55555

#lista para os clientes e seus apelidos
clientes_conectados = []
apelidos = []

#trava para condicoes de corrida
trava_clientes = threading.Lock()

def obter_horario_atual():
    """Retorna data e horário formatados como DD/MM/AAAA HH:MM:SS."""
    return time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())

#envia mensagem para todos os clientes
def transmitir(mensagem, conexao_remetente=None): #cliente remetente evita que quem enviou receba a propria mensagem
    """Envia uma mensagem para todos os clientes, exceto o remetente."""
    clientes_a_remover = []
    with trava_clientes: #utiliza a trava para evitar condicoes de corrida
        for conexao_cliente in list(clientes_conectados):
            if conexao_cliente != conexao_remetente:
                try:
                    conexao_cliente.sendall(mensagem.encode('utf-8')) #codifica a mensagem para o formato de bytes antes de enviar
                except (socket.error, BrokenPipeError) as e:
                    print(f"Erro ao enviar mensagem para um cliente: {e}. Agendando remoção.")
                    clientes_a_remover.append(conexao_cliente)

    for conn in clientes_a_remover:
        remover_cliente(conn)

#quando um cliente desconecta ou perde a conexao
def remover_cliente(conn):
    """Remove um cliente das listas e avisa a todos sobre a saída."""
    apelido_removido = None
    with trava_clientes: #com a trava para remover o cliente com seguranca
        if conn in clientes_conectados:
            indice = clientes_conectados.index(conn)
            apelido_removido = apelidos.pop(indice)#remove o apelido da lista
            clientes_conectados.remove(conn)#remove a conexao da lista
            print(f"Usuário '{apelido_removido}' se desconectou.")
    
    try:
        conn.close() #fecha a conexao
    except Exception as e:
        print(f"Erro ao fechar a conexão do cliente: {e}")

    if apelido_removido:
        transmitir(f"{apelido_removido} saiu do chat.", None) #avisa a todos que o cliente saiu

#funcao que cada thread de cliente vai executar
def gerenciar_cliente(conn, addr):
    print(f"Nova conexão de {addr}")

    mensagem_boas_vindas = f"{obter_horario_atual()}: CONECTADO!!"
    conn.sendall(mensagem_boas_vindas.encode('utf-8'))

    try:
        apelido = conn.recv(1024).decode('utf-8').strip()#espera um apelido
        if not apelido: 
            apelido = f"{addr[0]}:{addr[1]}"#caso o cliente nao envie um apelido, usa o endereco IP:porta como apelido

        with trava_clientes: #adiciona o cliente e apelido as listas
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
        while True: #constantemente espera por mensagens do cliente
            try:
                mensagem = conn.recv(1024).decode('utf-8') #a thread fica bloqueada aqui esperando por mensagens e se recebe, decodifica
                if not mensagem:
                    break

                if mensagem.startswith(':'): #verifica se é um comando especial
                    if mensagem.lower() == ':quit':
                        break #quebra o loop para desconectar
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
                                
                                #avisa no console do servidor
                                print(f"AVISO DE NOME: {mensagem_notificacao}")

                                #envia a notificação para todos os clientes, incluindo quem mudou
                                transmitir(mensagem_notificacao, None)
                            else:
                                conn.sendall("Nome não pode ser vazio.".encode('utf-8'))
                        except IndexError:
                            conn.sendall("Comando de nome inválido. Use :nome <novo_nome>".encode('utf-8'))
                    else:
                        conn.sendall(f"Comando '{mensagem}' desconhecido.".encode('utf-8'))
                else:
                    mensagem_eco = f"Voce digitou: {mensagem}" #eco para o proprio cliente da mensagem que enviou
                    conn.sendall(mensagem_eco.encode('utf-8')) #envia o eco
                    
                    mensagem_formatada = f"{apelido} ({obter_horario_atual()}): {mensagem}" #formata a mensagem para transmitir
                    print(mensagem_formatada) #mostra no console do servidor
                    transmitir(mensagem_formatada, conn) #transmite para todos os outros clientes
                        
            except UnicodeDecodeError: #caso tenha erro de decodificacao
                print(f"Cliente {apelido} enviou dados mal formatados, ignorando.")
                #envia uma mensagem de aviso ao cliente
                conn.sendall("Erro: Por favor, envie apenas texto no formato UTF-8.".encode('utf-8'))
                continue
            except (ConnectionResetError, ConnectionAbortedError): #se o cliente desconectar abruptamente
                print(f"Conexão com {apelido} perdida abruptamente.")
                break #sai do loop para finalizar a thread
    except (ConnectionResetError, ConnectionAbortedError):
        print(f"Conexão com {apelido} perdida abruptamente.")
    finally:
        remover_cliente(conn) #remove o cliente das listas

def enviar_horario_periodicamente(): #roda em sua propria thread em segundo plano
    while True:
        time.sleep(60) #espera 60 segundos
        mensagem_horario = f"DATA E HORARIO DO SERVIDOR ({obter_horario_atual()})"
        transmitir(mensagem_horario, None) #envia para todos os clientes

def iniciar_servidor(limite):
    #cria o socket do servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((HOST, PORTA))
        servidor.listen() #coloca em modo de escuta
        print(f"Servidor escutando em {HOST}:{PORTA} com limite de {limite} clientes.")

        thread_horario = threading.Thread(target=enviar_horario_periodicamente, daemon=True) #thread para enviar horario
        thread_horario.start()

        while True:
            conn, addr = servidor.accept() #quando um cliente conecta, accept envia a conexao e endereco
            #verifica o limite de clientes utilizando a trava
            with trava_clientes: 
                if len(clientes_conectados) >= limite:
                    print(f"Conexão de {addr} recusada. Limite atingido.")
                    conn.sendall("Limite de clientes atingido.".encode('utf-8'))
                    conn.close()
                    continue
            
            #para cada cliente, cria uma nova thread
            thread_cliente = threading.Thread(target=gerenciar_cliente, args=(conn, addr))
            thread_cliente.start()

if __name__ == "__main__":
    try:
        #pela linha de comando, o usuario pode definir o limite de clientes utilizando o primeiro argumento após iniciar o script
        #exemplo: python server.py 10
        limite_clientes = int(sys.argv[1]) if len(sys.argv) > 1 else 5 #se nao for passado, usa 5 como padrao
    except (IndexError, ValueError):
        print("Uso: python server.py <limite_de_clientes>")
        limite_clientes = 5
    iniciar_servidor(limite_clientes)