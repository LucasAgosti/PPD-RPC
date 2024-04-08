from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client

class RPCGameServer:
    def __init__(self, host="localhost", port=8000):
        self.server = SimpleXMLRPCServer((host, port), allow_none=True)
        self.moves = []
        self.clients = []
        self.register_functions()
        self.player1 = False
        self.player2 = False
        self.lockedBoard = False

        self.game_over = False

    def register_functions(self):
        self.server.register_function(self.register_client, "register_client")
        self.server.register_function(self.deregister_client, "deregister_client")
        self.server.register_function(self.make_move_on_server, "make_move_on_server")
        self.server.register_function(self.get_pending_moves, "get_pending_moves")

        self.server.register_function(self.quit_game, "quit_game")
        self.server.register_function(self.lock_board, "lock_board")
        self.server.register_function(self.notify_client, "notify_client")

        self.server.register_function(self.end_game, "end_game")
        self.server.register_function(self.is_game_over, "is_game_over")

    def run(self):
        print(f"Servidor iniciado em http://{self.server.server_address[0]}:{self.server.server_address[1]}/")
        self.server.serve_forever()

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
        if client_address in self.clients:
            self.clients.remove(client_address)
            print(f"Cliente saiu do jogo: {client_address}")
            return True
        return False

    def notify_client(self, client_address):
        if client_address in self.clients:
            print(client_address)
            #return client_address

    def quit_game(self, client_address):
        self.lock_board()

    def lock_board(self):
        self.lockedBoard = True

    def end_game(self, client_id):
        self.game_over = True
        return True

    def is_game_over(self):
        return self.game_over

    def notify_winner(self, winner_address):
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
