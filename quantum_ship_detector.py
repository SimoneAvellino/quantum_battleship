from battleship import BattleShipBoard, BoardComponent, BoardRow
from qiskit import QuantumCircuit
import numpy as np
from qiskit.providers.basic_provider import BasicSimulator

class MachZehnderCircuit(QuantumCircuit):
    
    def __init__(self, board: BattleShipBoard, component: BoardComponent):
        self.board = board
        self.component = component
        
        super().__init__(len(component)**2 + 1, 1 + board.ships_number())
        super().rx(np.pi / 3, 0)
        self._set_cnot_gates()
        super().rx(-np.pi, 0)
        super().barrier()
        self._set_measurement_gates()
        super().barrier()
        super().rx(np.pi, 0)
        self._set_cnot_gates()
        super().rx(-np.pi/3, 0)
        super().measure(0, 0)
        
    def _set_cnot_gates(self):
        # step = self.component.step()
        for idx in range(len(self.component)):
            if isinstance(self.component, BoardRow):
                x = self.component.index
                y = idx
            else:
                x = idx
                y = self.component.index
            target = x * self.board.size + y + 1
            super().cx(0, target)
            
# i * 4 + j + 1
            
    def _set_measurement_gates(self):
        measure_idx = 1 
        for x, y in self.board.ship_coordinates:
            qubit = x * self.board.size + y + 1
            super().measure(qubit, measure_idx)
            measure_idx += 1
            
    def run(self, shots: int = 1024):
        backend = BasicSimulator()
        job = backend.run(self, shots=shots)
        result = job.result()
        return result.get_counts()  
            
class QuantumShipDetector:
    
    def __init__(self, board: BattleShipBoard, shots: int = 1024):
        self.board = board
        self.shots = shots
        
    def detect_ships_in_row(self, row_index: int):
        row = self.board.get_row(row_index)
        circuit = MachZehnderCircuit(self.board, row)
        print("Quantum Circuit:")
        print(circuit.draw())
        result = circuit.run(self.shots)
        print(f"Results for row {row_index}:\n {result}")
        
    def detect_ships_in_column(self, column_index: int):
        column = self.board.get_column(column_index)
        circuit = MachZehnderCircuit(self.board, column)
        print("Quantum Circuit:")
        print(circuit.draw())
        result = circuit.run(self.shots)
        print(f"Results for column {column_index}:\n {result}")