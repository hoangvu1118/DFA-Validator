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
        self.layout = QVBoxLayout() # Create an app that element is put on top of each other

        self.build_ui()

    # update function to dynamically update the transition table
    def update_table(self):
        states = self.states_input.text().split()
        alphabet = self.alphabet_input.text().split() if self.index == 0 else ["a", "λ"]
        
        if states and alphabet:
            header_labels = alphabet.copy() if isinstance(alphabet, list) else alphabet.copy().split()
            
            self.transition_table.setRowCount(len(states))
            self.transition_table.setVerticalHeaderLabels(states)
            
            self.transition_table.setColumnCount(len(header_labels))
            self.transition_table.setHorizontalHeaderLabels(header_labels)

    def build_ui(self):
         
        self.layout.addWidget(QLabel("Choose Finite Automata"))
        self.layout.addWidget(self.combo)

        self.layout.addWidget(QLabel("States (e.g., q0 q1 q2):"))
        self.layout.addWidget(self.states_input)

        self.alphabet_label = QLabel("Alphabet (e.g., a b or 0 1):")
        self.layout.addWidget(self.alphabet_label)
        self.layout.addWidget(self.alphabet_input)

        # DFA - Input String (default shown)
        self.string_label = QLabel("Input String:")
        self.layout.addWidget(self.string_label)
        self.layout.addWidget(self.string_input)
        
        # NFA - Extra input fields (initially hidden)
        self.single_state_label = QLabel("Input Single State (e.g., q0):")
        self.single_state_input = QLineEdit()
        self.subset_label = QLabel("Input a subset (e.g, '{q0, q1, q2}'):")
        self.subset_input = QLineEdit()
        
        # Initially, hide the NFA inputs
        self.single_state_label.hide()
        self.single_state_input.hide()
        self.subset_label.hide()
        self.subset_input.hide()
        
        # Add the hidden widgets to the layout
        self.layout.addWidget(self.single_state_label)
        self.layout.addWidget(self.single_state_input)
        self.layout.addWidget(self.subset_label)
        self.layout.addWidget(self.subset_input)
        
        self.layout.addWidget(QLabel("Final States(e.g., q1 q2):"))
        self.layout.addWidget(self.final_states)

        row = len(self.states_input.text().split())
        self.transition_table.setRowCount(row)
        self.transition_table.setColumnCount(2)
        
        # update function to the text changed signals
        self.states_input.textChanged.connect(self.update_table)
        self.alphabet_input.textChanged.connect(self.update_table)

        self.layout.addWidget(QLabel("Transition Table (double-click cells to edit):"))
        self.layout.addWidget(self.transition_table)

        validate_btn = QPushButton("Validate String")
        if(self.index == 0):
            validate_btn.clicked.connect(self.validate_dfa)
        else:
            validate_btn.clicked.connect(self.validate_nfa)

        self.layout.addWidget(validate_btn)
        self.layout.addWidget(self.result_label)
        self.layout.addWidget(self.graph_label)
        
        self.setLayout(self.layout)

    def validate_dfa(self):
        states = self.states_input.text().strip().split()
        alphabet = self.alphabet_input.text().strip().split()
        input_string = self.string_input.text().strip()
        transitions = {}

        #transitions from table
        for i, state in enumerate(states):
            for j, symbol in enumerate(alphabet):
                # Getting element according to state i and input j
                item = self.transition_table.item(i, j) # State after it moves 
                if item: # If it exist -> add to transition dict with key is a transition move e.g (q0, a) -> q1 (value)
                    transitions[(state, symbol)] = item.text().strip()

        # Check if required inputs are provided by the users
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
        self.draw_graph(states, transitions, start_state, accept_state)

    def validate_nfa(self):
        ...

    def draw_graph(self, states, transitions, start, accepts):
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
        #clear input placeholder
        self.clear_inputs()
        # Toggle visibility of input widgets based on mode
        if index == 1:  # NFA
            # Hide DFA specific widgets
            self.string_label.hide()
            self.string_input.hide()
            self.alphabet_label.hide()
            self.alphabet_input.hide()
            
            # Show NFA specific widgets
            self.single_state_label.show()
            self.single_state_input.show()
            self.subset_label.show()
            self.subset_input.show()
            self.alphabet_input.setText("a")
            self.setWindowTitle("ValiFA - NFA Mode")
            
        else:  # DFA
            # Show DFA specific widgets
            self.string_label.show()
            self.string_input.show()
            self.alphabet_label.show()
            self.alphabet_input.show()
            
            # Hide NFA specific widgets
            self.single_state_label.hide()
            self.single_state_input.hide()
            self.subset_label.hide()
            self.subset_input.hide()
            
            self.setWindowTitle("ValiFA - DFA Mode")
        
        # Update transition table

        if index == 1:  # NFA
            self.update_table()
        
        # Clear previous results
        self.result_label.setText("")
        self.graph_label.clear()

    def clear_inputs(self):
        # Clear text fields
        self.string_input.clear()
        self.single_state_input.clear()
        self.subset_input.clear()
        
        # Clear transition table
        self.transition_table.clearContents()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DFAApp()
    window.show()
    sys.exit(app.exec_())
