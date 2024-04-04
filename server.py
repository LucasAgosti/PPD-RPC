from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client

class RPCGameServer:
    def __init__(self, host="localhost", port=8000):
        self.server = SimpleXMLRPCServer((host, port), allow_none=True)
        self.moves = []
        self.clients = []  # Esta lista irá armazenar os endereços dos clientes para comunicação bidirecional
        self.current_turn = 0  # Controla o turno atual
        self.register_functions()

    def register_functions(self):
        self.server.register_function(self.register_client, "register_client")
        self.server.register_function(self.deregister_client, "deregister_client")
        self.server.register_function(self.make_move_on_server, "make_move_on_server")
        self.server.register_function(self.get_pending_moves, "get_pending_moves")

        # Adicione aqui outros métodos que deseja expor via RPC

    def run(self):
        print(f"Servidor iniciado em http://{self.server.server_address[0]}:{self.server.server_address[1]}/")
        self.server.serve_forever()

    # Função para registrar um cliente
    def register_client(self, client_address):
        if len(self.clients) < 2:
            self.clients.append(client_address)
            print(f"Cliente registrado: {client_address}")
            return True, len(self.clients) - 1  # Retorna True e o índice do jogador
        return False, -1  # Retorna False e -1 se não puder adicionar mais clientes

    def deregister_client(self, client_address):
        # Remove o cliente da lista, se ele estiver nela
        if client_address in self.clients:
            self.clients.remove(client_address)
            print(f"Cliente saiu do jogo: {client_address}")
            return True  # Retorno para confirmar a desregisto do cliente
        return False  # Caso o endereço do cliente não esteja na lista

    # Implemente os procedimentos do jogo, como fazer um movimento, aqui
    #def make_move(self, player_index, move):
        # Lógica para fazer um movimento
     #   print(f"Jogador {player_index} fez um movimento: {move}")
        # Retorne o resultado do movimento, verificar turno, etc.
      #  return True

    def make_move_on_server(self, client_address, start_pos, end_pos):
        # Armazena o movimento para que o outro cliente possa pegá-lo
        self.moves.append((client_address, start_pos, end_pos))
        return True

    def get_pending_moves(self, client_address):
        # Retorna movimentos pendentes para o cliente solicitante
        pending_moves = [move for move in self.moves if move[0] != client_address]
        self.moves = [move for move in self.moves if move[0] == client_address]  # Remove os movimentos entregues
        return pending_moves


if __name__ == "__main__":
    game_server = RPCGameServer()
    game_server.run()
