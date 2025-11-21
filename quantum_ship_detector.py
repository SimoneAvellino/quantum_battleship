from calendar import c
import re
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
        # print("Quantum Circuit:")
        # print(circuit.draw())
        result = circuit.run(self.shots)
        # print(f"Results for row {row_index}:\n {result}")
        return result
        
    def detect_ships_in_column(self, column_index: int):
        column = self.board.get_column(column_index)
        circuit = MachZehnderCircuit(self.board, column)
        # print("Quantum Circuit:")
        # print(circuit.draw())
        result = circuit.run(self.shots)
        # print(f"Results for column {column_index}:\n {result}")
        return result

    def _analyze_result(self, result: dict):
        """
        result: dict {bitstring: count}
        bitstring = bombs...bombs path
        - bombs = tutti i bit tranne l'ultimo
        - path  = ultimo bit (0/1)

        Ritorna:
        - patterns: set di stringhe 'bombs' (possibili posizioni nave)
        - ev_score: detection_count / explosion_count (se possibile)
        """
        detection_count = 0  # eventi EV (found, no explosion)
        explosion_count = 0  # eventi con almeno una bomba=1
        patterns = set()

        for bitstring, count in result.items():
            # ignora completamente '000...0' (nessuna info)
            if set(bitstring) == {"0"}:
                continue

            bombs = bitstring[:-1]   # tutti i qubit "nave"
            path = bitstring[-1]     # qubit fotone

            # caso 1: almeno una bomba = 1 -> esplosione
            if set(bombs) != {"0"}:
                explosion_count += count
                patterns.add(bombs)
            # caso 2: nessuna bomba = 1 ma path = 1 -> detection EV
            elif path == "1":
                detection_count += count
                # bombs è "000...0": non porta info di posizione,
                # ma lo includiamo se vuoi tracciare tutte le configurazioni
                patterns.add(bombs)
            # caso 3: bombs tutti 0, path=0 -> nessuna info, ignora

        ev_score = detection_count / explosion_count if explosion_count > 0 else 0.0
        return patterns, ev_score
        
    def run(self, verbose: bool = False):
        ev_scores = []
        solutions = []
        row_results = {}
        column_results = {}

        # Analizza tutte le righe
        for i in range(self.board.size):
            result = self.detect_ships_in_row(i)
            patterns, ev_score = self._analyze_result(result)

            if patterns:
                row_results[i] = patterns
            if ev_score > 0:
                ev_scores.append(ev_score)

            if verbose:
                print(f"Row {i} raw results:", result)
                print(f"Row {i} patterns:", patterns)
                print(f"Row {i} EV score:", ev_score)

        # Analizza tutte le colonne
        for j in range(self.board.size):
            result = self.detect_ships_in_column(j)
            patterns, ev_score = self._analyze_result(result)

            if patterns:
                column_results[j] = patterns
            if ev_score > 0:
                ev_scores.append(ev_score)

            if verbose:
                print(f"Column {j} raw results:", result)
                print(f"Column {j} patterns:", patterns)
                print(f"Column {j} EV score:", ev_score)

        # Incrocio righe/colonne: cerca overlap di '1' nelle stringhe bombs
        for row_index, row_possibilities in row_results.items():
            for row_possibility in row_possibilities:
                if verbose:
                    print(f"R{row_index} - {row_possibility}")
                for col_index, col_possibilities in column_results.items():
                    for col_possibility in col_possibilities:
                        if verbose:
                            print(f"    C{col_index} - {col_possibility}")
                        overlap = any(
                            a == '1' and b == '1'
                            for a, b in zip(row_possibility, col_possibility)
                        )
                        if overlap:
                            if verbose:
                                print(f"        OVERLAP DETECTED BETWEEN R{row_index} AND C{col_index}")
                            solutions.append((row_index, col_index))

        mean_ev = sum(ev_scores) / len(ev_scores) if ev_scores else 0.0
        return solutions, mean_ev