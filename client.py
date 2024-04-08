import tkinter as tk
from tkinter import messagebox
import xmlrpc.client
import uuid


class RPCGameClient(tk.Tk):
    def __init__(self, server_url="http://localhost:8000"):
        super().__init__()
        self.title('Resta 1')
        self.server = xmlrpc.client.ServerProxy(server_url, allow_none=True)
        self.client_address = "client_unique_identifier"  # Exemplo de identificador

        self.is_my_turn = True
        self.clientIndex = None
        self.registered = False
        self.lockedBoard = False
        self.register_client()
        self.setup_board()
        self.setup_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.client_address = str(uuid.uuid4())

        self.start_checking_for_moves()

    def register_client(self):
        try:
            success, player_index = self.server.register_client(self.client_address)
            if success:
                print(f"Registrado como jogador {player_index + 1}.")
                self.registered = True
                self.clientIndex = player_index + 1
                #if player_index == 0:
                    #print("é o jogador 1")
                    #self.is_my_turn = True
                #else:
                    #print("É o jogador 2")
                    #self.is_my_turn = False
            else:
                messagebox.showerror("Erro", "Não foi possível registrar no servidor. Talvez o jogo esteja cheio.")
                self.destroy()
        except Exception as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao servidor: {e}")
            self.destroy()

    def on_close(self):
        if self.registered:
            try:
                self.server.deregister_client(self.client_address)
                print("Desconectado do servidor.")
            except Exception as e:
                print(f"Erro ao tentar se desconectar do servidor: {e}")
        self.destroy()

    def setup_board(self):
        self.board = [
            [-1, -1, 1, 1, 1, -1, -1],
            [-1, -1, 1, 1, 1, -1, -1],
            [ 1,  1, 1, 1, 1,  1,  1],
            [ 1,  1, 1, 0, 1,  1,  1],
            [ 1,  1, 1, 1, 1,  1,  1],
            [-1, -1, 1, 1, 1, -1, -1],
            [-1, -1, 1, 1, 1, -1, -1]
        ]
        self.canvas = tk.Canvas(self, width=400, height=400)
        self.canvas.pack()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def setup_ui(self):
        self.quit_button = tk.Button(self, text="Desistir", command=self.quit_game)
        self.quit_button.pack()

    def quit_game(self):
        try:
            self.server.quit_game(self.client_address)  # Envia solicitação de desistência
            if self.clientIndex == 1:
                messagebox.showinfo("Fim de jogo", "Você desistiu. O jogador 2 venceu.")
                self.disable_board()

            else:
                messagebox.showinfo("Fim de jogo", "Você desistiu. O jogador 1 venceu.")
                self.disable_board()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def disable_board(self):
        status = self.server.lock_board()
        if status:
            self.lockedBoard = True
            print("TRAVOU O BOARD")
        else:
            self.lockedBoard = True

    def draw_peg(self, row, col, color='black'):
        x0 = col * 50 + 15
        y0 = row * 50 + 15
        x1 = x0 + 20
        y1 = y0 + 20
        self.canvas.create_oval(x0, y0, x1, y1, fill=color, tags="peg")

    def draw_board(self):
        self.canvas.delete("peg")
        for row in range(7):
            for col in range(7):
                if self.board[row][col] == 1:
                    self.draw_peg(row, col)

    def on_canvas_click(self, event):
        if self.lockedBoard == False:
            if not self.is_my_turn:
                print("Não é sua vez!")
                return
            col = event.x // 50
            row = event.y // 50

            if 0 <= row < 7 and 0 <= col < 7:
                if hasattr(self, 'selected_peg') and self.selected_peg:
                    start_pos = self.selected_peg
                    end_pos = (row, col)
                    if self.is_valid_move(start_pos, end_pos):
                        self.make_move(start_pos, end_pos)
                        if self.check_game_state():
                            return
                        self.selected_peg = None
                    else:
                        self.selected_peg = None
                elif self.board[row][col] == 1:
                    self.selected_peg = (row, col)
        else:
            messagebox.showinfo("Jogo finalizado", "A partida já finalizou, reinicie o jogo para jogar novamente.")
            return

    def is_valid_move(self, start_pos, end_pos):
        if (0 <= end_pos[0] < 7 and 0 <= end_pos[1] < 7 and
                self.board[end_pos[0]][end_pos[1]] == 0 and
                self.board[start_pos[0]][start_pos[1]] == 1):
            row_diff = end_pos[0] - start_pos[0]
            col_diff = end_pos[1] - start_pos[1]
            if abs(row_diff) == 2 and col_diff == 0 and self.board[(start_pos[0] + end_pos[0]) // 2][start_pos[1]] == 1:
                return True
            if abs(col_diff) == 2 and row_diff == 0 and self.board[start_pos[0]][(start_pos[1] + end_pos[1]) // 2] == 1:
                return True
        return False

    def check_game_state(self):
        peg_count = sum(row.count(1) for row in self.board)
        if peg_count == 1:
            print("Parabéns, você venceu!")
            return True
        elif not self.any_valid_moves():
            print("Você perdeu, não há mais movimentos possíveis")
            return True
        return False

    def notify_winner(self, winner_address):
        pass

    def any_valid_moves(self):
        for row in range(7):
            for col in range(7):
                if self.board[row][col] == 1:
                    #Checagem dos quatro movimentos possíveis das peças
                    for drow, dcol in [(2, 0), (-2, 0), (0, 2), (0, -2)]:
                        if self.is_valid_move((row, col), (row + drow, col + dcol)):
                            return True
        return False

    def start_checking_for_moves(self):
        self.check_for_new_moves()
        self.after(1000, self.start_checking_for_moves)

    def check_for_new_moves(self):
        try:
            new_moves = self.server.get_pending_moves(self.client_address)
            for _, start_pos, end_pos in new_moves:
                self.make_move(start_pos, end_pos, update_server=False)
        except Exception as e:
            print(f"Erro ao verificar novos movimentos: {e}")

    def make_move(self, start_pos, end_pos, update_server=True):
        self.board[(start_pos[0] + end_pos[0]) // 2][(start_pos[1] + end_pos[1]) // 2] = 0
        self.board[start_pos[0]][start_pos[1]] = 0
        self.board[end_pos[0]][end_pos[1]] = 1
        self.draw_board()

        # Enviar detalhes do movimento para o servidor
        if update_server:
            try:
                self.server.make_move_on_server(self.client_address, start_pos, end_pos)
            except Exception as e:
                print(f"Erro ao enviar movimento para o servidor: {e}")

if __name__ == "__main__":
    client = RPCGameClient()
    client.mainloop()
