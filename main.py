from battleship import BattleShipBoard
from quantum_ship_detector import QuantumShipDetector, MachZehnderCircuit

if __name__ == "__main__":
    
    BOARD_SIZE = 3
    SHIPS_NUMBER = 5
    
    board = BattleShipBoard(size=BOARD_SIZE)
    board.place_ship_random(num_ships=SHIPS_NUMBER)
    print("Battleship Board:")
    print(board)
    
    detector = QuantumShipDetector(board, shots=1024)
    result = detector.run()
    print("Detection Results:")
    print(result)