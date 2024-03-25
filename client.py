import tkinter as tk
from tkinter import messagebox
import xmlrpc.client

class RPCGameClient(tk.Tk):
    def __init__(self, server_url="http://localhost:8000"):
        super().__init__()
        self.title('Resta 1')
        self.server = xmlrpc.client.ServerProxy(server_url, allow_none=True)
        self.client_address = "client_unique_identifier"  # Exemplo de identificador
        self.setup_board()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

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
        # Aqui você pode adicionar a lógica para processar os cliques no tabuleiro
        # Por exemplo, determinar a peça selecionada, validar e fazer movimentos
        col = event.x // 50
        row = event.y // 50

        if 0 <= row < 7 and 0 <= col < 7:
            if hasattr(self, 'selected_peg') and self.selected_peg:
                start_pos = self.selected_peg
                end_pos = (row, col)
                if self.is_valid_move(start_pos, end_pos):
                    self.make_move(start_pos, end_pos)
                    self.selected_peg = None  # Reset selected peg after a move
                else:
                    self.selected_peg = None  # Deselect peg if move is invalid
            elif self.board[row][col] == 1:
                self.selected_peg = (row, col)  # Select a peg

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

    def make_move(self, start_pos, end_pos):
        # Remove the jumped peg
        self.board[(start_pos[0] + end_pos[0]) // 2][(start_pos[1] + end_pos[1]) // 2] = 0
        # Move selected peg to new position
        self.board[start_pos[0]][start_pos[1]] = 0
        self.board[end_pos[0]][end_pos[1]] = 1
        self.draw_board()

    def on_close(self):
        # Aqui você pode adicionar qualquer lógica necessária antes de fechar a aplicação
        # Por exemplo, notificar o servidor sobre a desconexão
        self.destroy()

if __name__ == "__main__":
    client = RPCGameClient()
    client.mainloop()
