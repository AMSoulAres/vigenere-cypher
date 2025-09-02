import socket
import threading
import sys

from cypher import VigenereCypher

class ChatClient:
    """
    Um cliente de chat P2P simples que tenta se conectar a um peer,
    e se falhar, inicia um servidor para ouvir uma conexão.
    """

    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.peer_socket = None
        self.cypher = VigenereCypher("abroba")

    def _preprocess_message_for_sending(self, message):
        # print(f"Pré-processando para envio: '{message}'")
        encoded = self.cypher.encode(message)
        print(f"Texto cifrado: {encoded}")
        return encoded

    def _postprocess_received_message(self, message):
        # print(f"Pós-processando recebido: '{message}'")
        print(message)
        return self.cypher.decode(message)

    def _receive_messages(self):
        while True:
            try:
                if not self.peer_socket:
                    break
                data = self.peer_socket.recv(1024)
                if not data:
                    print("Conexão fechada pelo peer.")
                    break
                
                message = data.decode('utf-8')
                message = message.lower()
                processed_message = self._postprocess_received_message(message)
                print(f"\nMensagem recebida: {processed_message}")
                print("Digite sua mensagem: ", end="")
                sys.stdout.flush()

            except (ConnectionResetError, ConnectionAbortedError):
                print("A conexão foi perdida.")
                break
            except Exception as e:
                print(f"Ocorreu um erro ao receber a mensagem: {e}")
                break
        
        if self.peer_socket:
            self.peer_socket.close()
            self.peer_socket = None
        print("Thread de recebimento finalizada.")

    def _send_messages(self):
        try:
            while True:
                message = input("Digite sua mensagem: ")
                message = message.lower()
                if message == 'quit':
                    break
                
                if self.peer_socket:
                    processed_message = self._preprocess_message_for_sending(message)
                    self.peer_socket.sendall(processed_message.encode('utf-8'))
                else:
                    print("Nenhum peer conectado para enviar mensagem.")
                    break
        finally:
            if self.peer_socket:
                self.peer_socket.close()

    def start(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print(f"Tentando conectar a {self.host}:{self.port}...")
            client_socket.connect((self.host, self.port))
            self.peer_socket = client_socket
            print("Conectado com sucesso a um peer.")
        except ConnectionRefusedError:
            print("Nenhum peer encontrado. Iniciando como servidor e aguardando conexão...")
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(1)
            
            conn, addr = server_socket.accept()
            self.peer_socket = conn
            print(f"Conectado por {addr}")
            server_socket.close()
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            client_socket.close()
            return

        if self.peer_socket:
            receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            receive_thread.start()
            
            self._send_messages()

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    
    chat_client = ChatClient(host, port)
    chat_client.start()
