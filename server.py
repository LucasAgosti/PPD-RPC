from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client

class RPCGameServer:
    def __init__(self, host="localhost", port=8000):
        self.server = SimpleXMLRPCServer((host, port), allow_none=True)
        self.moves = []
        self.clients = []  # Esta lista irá armazenar os endereços dos clientes para comunicação bidirecional
        self.register_functions()
        self.player1 = False
        self.player2 = False
        self.lockedBoard = False

    def register_functions(self):
        self.server.register_function(self.register_client, "register_client")
        self.server.register_function(self.deregister_client, "deregister_client")
        self.server.register_function(self.make_move_on_server, "make_move_on_server")
        self.server.register_function(self.get_pending_moves, "get_pending_moves")

        self.server.register_function(self.quit_game, "quit_game")
        self.server.register_function(self.lock_board, "lock_board")
        #self.server.register_function(self.notify_client())
        # Adicione aqui outros métodos que deseja expor via RPC

    def run(self):
        print(f"Servidor iniciado em http://{self.server.server_address[0]}:{self.server.server_address[1]}/")
        self.server.serve_forever()

    # Função para registrar um cliente
    def register_client(self, client_address):
        if len(self.clients) < 2:
            self.clients.append(client_address)
            print(f"Cliente registrado: {client_address}")
            if len(self.clients) == 1:
                #print("Você é o jogador 1")
                self.player1 = True
            elif len(self.clients) == 2:
                self.player2 = True
                #print("Você é o jogador 2")
            return True, len(self.clients) - 1  # Retorna True e o índice do jogador
        return False, -1  # Retorna False e -1 se não puder adicionar mais clientes

    def deregister_client(self, client_address):
        # Remove o cliente da lista, se ele estiver nela
        if client_address in self.clients:
            self.clients.remove(client_address)
            print(f"Cliente saiu do jogo: {client_address}")
            return True  # Retorno para confirmar a desregisto do cliente
        return False  # Caso o endereço do cliente não esteja na lista

    def notify_client(self, client_address):
        if client_address in self.clients:
            print(client_address)
            #return client_address

    def quit_game(self, client_address):
        # Implementação da lógica para determinar o vencedor e notificar os clientes
        winner_address = [addr for addr in self.clients if addr != client_address][0]
        self.notify_winner(winner_address)
        self.lock_board()
        return True

    def lock_board(self):
        self.lockedBoard = True


    def notify_winner(self, winner_address):
        # Esta função notifica o vencedor. Implementação depende do método de notificação escolhido
        # Por exemplo, pode-se chamar uma função no cliente para mostrar uma mensagem de vitória

        if self.player1:
            print("Jogador 2 venceu")
        elif self.player2:
            print("Jogador 1 venceu")

    def make_move_on_server(self, client_address, start_pos, end_pos):
        # Armazena o movimento para que o outro cliente possa pegá-lo
        if not self.lockedBoard:
            self.moves.append((client_address, start_pos, end_pos))
            return True
        return False

    def get_pending_moves(self, client_address):
        # Retorna movimentos pendentes para o cliente solicitante
        pending_moves = [move for move in self.moves if move[0] != client_address]
        self.moves = [move for move in self.moves if move[0] == client_address]  # Remove os movimentos entregues
        return pending_moves


if __name__ == "__main__":
    game_server = RPCGameServer()
    game_server.run()
