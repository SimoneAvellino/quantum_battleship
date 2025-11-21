import random
from abc import ABC, abstractmethod
import string

class BoardComponent(ABC):
    
    def __init__(self, board: "BattleShipBoard", index: int):
        self.board = board
        self.index = index
        
    def __len__(self):
        return self.board.size
    
    @abstractmethod
    def __getitem__(self, i: int):
        pass
    
    def step(self):
        pass

class BoardColumn(BoardComponent):
    
    def __init__(self, board: "BattleShipBoard", column_index: int):
        super().__init__(board, column_index)
        
    def __getitem__(self, i: int):
        return self.board[i][self.index]
    
    def __str__(self):
        string_rep = ""
        for i in range(len(self)):
            string_rep += str(self[i]) + "\n"
        return string_rep
    
    def step(self):
        return self.board.size
        
class BoardRow(BoardComponent):
    
    def __init__(self, board: "BattleShipBoard", row_index: int):
        super().__init__(board, row_index)
        
    def __getitem__(self, i: int):
        print(self.index, i)
        print(self.board)
        return self.board.get_element(self.index, i) 
    
    def __str__(self):
        string_rep = ""
        for i in range(len(self)):
            string_rep += str(self[i]) + " "
        return string_rep.strip()
    
    def step(self):
        return 1



class BattleShipBoard:
    
    def __init__(self, size: int):
        self.size = size
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.ship_coordinates = set()
        
    def _detect_ships_coordinates(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 1:
                    self.ship_coordinates.add((i, j))
                    
    def set_board(self, board_matrix: list[list[int]]):
        self.board = board_matrix
        self._detect_ships_coordinates()
        
        
    def _all_coordinates(self):
        return [(i, j) for i in range(self.size) for j in range(self.size)]
    
    def place_ship_random(self, num_ships = 5):
        coordinates = self._all_coordinates()
        random_coorinate_indices = random.sample(coordinates, num_ships)
        for x, y in random_coorinate_indices:
            self.board[x][y] = 1
            
        self.ship_coordinates = set(random_coorinate_indices)
        
    def ships_number(self):
        return len(self.ship_coordinates)
        
    def __str__(self):
        display = ""
        for row in self.board:
            display += " ".join(str(cell) for cell in row) + "\n"
        return display
    
    def __getitem__(self, i: int, j: int):
        return self.board[i][j]
    
    def get_element(self, i: int, j: int):
        return self.board[i][j]
    
    def get_column(self, column_index: int) -> BoardColumn:
        return BoardColumn(self, column_index)
    
    def get_row(self, row_index: int) -> BoardRow:
        return BoardRow(self, row_index)