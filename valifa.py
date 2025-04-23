import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton,
    QTableWidget, QComboBox
)
from PyQt5.QtGui import QPixmap, QIcon
from graphviz import Digraph
from style import get_stylesheet

class DFAApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ValiFA")
        self.setWindowIcon(QIcon("static/good-icon.png"))
        self.resize(700, 800)
        self.setStyleSheet(get_stylesheet())

        self.combo = QComboBox()
        self.combo.addItems(["Deterministic Finite Accepters (DFA)", "Nondeterministic Finite Accepters (NFA)"])
        self.combo.currentIndexChanged.connect(self.switch_layout)

        # 0 indicate for DFA | 1 for NFA
        self.index = 0; # Default is DFA

        # Input fields
        self.states_input = QLineEdit()
        self.alphabet_input = QLineEdit()
        self.string_input = QLineEdit()
        self.final_states = QLineEdit()

        self.transition_table = QTableWidget()
        self.result_label = QLabel()
        self.graph_label = QLabel()
        
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout() # Create an app that element is put on top of each other

        layout.addWidget(QLabel("Choose Finite Automata"))
        layout.addWidget(self.combo)

        # need to fix this -> to fit with the layout of NFA requirements
        layout.addWidget(QLabel("States (e.g., q0 q1 q2):"))
        layout.addWidget(self.states_input)

        layout.addWidget(QLabel("Alphabet (e.g., a b || 0 1):"))
        layout.addWidget(self.alphabet_input)

        layout.addWidget(QLabel("Input String:"))
        layout.addWidget(self.string_input)

        
        layout.addWidget(QLabel("Final States(e.g., q1 q2):"))
        layout.addWidget(self.final_states)

        row = len(self.states_input.text().split())
        self.transition_table.setRowCount(row)
        self.transition_table.setColumnCount(2)

        # update function to dynamically update the transition table
        def update_table():
            states = self.states_input.text().split()
            alphabet = self.alphabet_input.text().split()
            
            if states and alphabet:
                self.transition_table.setRowCount(len(states))
                header_labels = alphabet.copy() if isinstance(alphabet, list) else alphabet.copy().split()

                if(self.index == 1):
                    # The requirement state that only need 1 edge label 'a' & lambda label
                    if(len(header_labels) > 1):
                        header_labels = ["a"]
                    header_labels.append("λ")
                self.transition_table.setColumnCount(len(header_labels))
                self.transition_table.setHorizontalHeaderLabels(header_labels)
                self.transition_table.setVerticalHeaderLabels(states)
        
        # update function to the text changed signals
        self.states_input.textChanged.connect(update_table)
        self.alphabet_input.textChanged.connect(update_table)

        layout.addWidget(QLabel("Transition Table (double-click cells to edit):"))
        layout.addWidget(self.transition_table)

        validate_btn = QPushButton("Validate String")
        if(self.index == 0):
            validate_btn.clicked.connect(self.validate_dfa)
        else:
            validate_btn.clicked.connect(self.validate_nfa)
        layout.addWidget(validate_btn)

        layout.addWidget(self.result_label)
        layout.addWidget(self.graph_label)
        
        self.setLayout(layout)

    def validate_dfa(self):
        states = self.states_input.text().split()
        alphabet = self.alphabet_input.text().split()
        input_string = self.string_input.text()
        transitions = {}

        #transitions from table
        for i, state in enumerate(states):
            for j, symbol in enumerate(alphabet):
                # Getting element according to state i and input j
                item = self.transition_table.item(i, j) # State after it moves 
                if item: # If it exist -> add to transition dict with key is a transition move e.g (q0, a) -> q1 (value)
                    transitions[(state, symbol)] = item.text()

        # Check if required inputs are provided
        if not states or not alphabet:
            self.result_label.setText("❌ Please enter states and alphabet")
            return
        if not input_string:
            self.result_label.setText("❌ Please enter an input string")
            return
        if not self.final_states.text():
            self.result_label.setText("❌ Please specify at least one final state")
            return
        else:
            start_state = states[0]
        
        accept_state = self.final_states.text().split() 

        # Checking input string
        current = start_state
        for symbol in input_string:
            if (current, symbol) in transitions:
                current = transitions[(current, symbol)]
            else:
                self.result_label.setText("❌ Rejected (invalid transition)")
                return
            
        #At the end of string check if it is in final state or not
        if current in accept_state:
            self.result_label.setText(f"✅ Accepted {self.string_input.text()}")
        else:
            self.result_label.setText(f"❌ Rejected {self.string_input.text()}")

        # Draw DFA
        self.draw_graph(states, alphabet, transitions, start_state, accept_state)

    def validate_nfa(self):
        ...

    def draw_graph(self, states, alphabet, transitions, start, accepts):
        dot = Digraph()
        dot.attr(rankdir='LR')
        dot.node('', shape='none')
        dot.edge('', start)

        for state in states:
            shape = 'doublecircle' if state in accepts else 'circle'
            dot.node(state, shape=shape)

        for (from_state, symbol), to_state in transitions.items():
            dot.edge(from_state, to_state, label=symbol)

        filename = "img_output"
        dot.render(filename, format='png', cleanup=True)
        self.graph_label.setPixmap(QPixmap(filename + '.png'))
    
    def switch_layout(self, index):
        self.index = index  # 0 for DFA, 1 for NFA
        
        # Update UI elements based on selected mode
        if index == 1:  # NFA
            self.setWindowTitle("ValiFA - NFA Mode")
            # Update transition table for NFA requirements
            states = self.states_input.text().split()
            if states:
                self.transition_table.setRowCount(len(states))
                header_labels = ["a", "λ"]  # NFA only needs 'a' and lambda
                self.transition_table.setColumnCount(len(header_labels))
                self.transition_table.setHorizontalHeaderLabels(header_labels)
                self.transition_table.setVerticalHeaderLabels(states)
        else:  # DFA
            self.setWindowTitle("ValiFA - DFA Mode")
            # Update transition table for DFA requirements
            states = self.states_input.text().split()
            alphabet = self.alphabet_input.text().split()
            if states and alphabet:
                self.transition_table.setRowCount(len(states))
                self.transition_table.setColumnCount(len(alphabet))
                self.transition_table.setHorizontalHeaderLabels(alphabet)
                self.transition_table.setVerticalHeaderLabels(states)
        
        # Clear previous validation results
        self.result_label.setText("")
        self.graph_label.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DFAApp()
    window.show()
    sys.exit(app.exec_())
