from battleship import BattleShipBoard
from quantum_ship_detector import QuantumShipDetector, MachZehnderCircuit

if __name__ == "__main__":
    
    BOARD_SIZE = 4
    SHIPS_NUMBER = 5
    
    board = BattleShipBoard(size=BOARD_SIZE)
    # board.place_ship_random(num_ships=SHIPS_NUMBER)
    board.set_board([
        [0, 0, 0, 0],
        [0, 0, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ])
    print("Battleship Board:")
    print(board)
    
    detector = QuantumShipDetector(board, shots=1024)
    
    detector.detect_ships_in_row(1)
    detector.detect_ships_in_column(3)
    