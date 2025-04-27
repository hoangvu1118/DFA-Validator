import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QPushButton,
    QTableWidget,
    QComboBox,
)
from PyQt5.QtGui import QPixmap, QIcon
from graphviz import Digraph
from style import get_stylesheet
import re


class DFAApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ValiFA - DFA Mode")
        self.setWindowIcon(QIcon("static/good-icon.png"))
        self.resize(700, 800)
        self.setStyleSheet(get_stylesheet())

        self.combo = QComboBox()
        self.combo.addItems(
            [
                "Deterministic Finite Accepters (DFA)",
                "Nondeterministic Finite Accepters (NFA)",
            ]
        )
        self.combo.currentIndexChanged.connect(self.switch_layout)

        # 0 indicate for DFA | 1 for NFA
        self.index = 0
        # Default is DFA

        # Input fields
        self.states_input = QLineEdit()
        self.alphabet_input = QLineEdit()
        self.string_input = QLineEdit()
        self.final_states = QLineEdit()

        self.transition_table = QTableWidget()
        self.result_label = QLabel()
        self.graph_label = QLabel()
        self.layout = (
            QVBoxLayout()
        )  # Create an app that element is put on top of each other

        self.build_ui()

    # update function to dynamically update the transition table
    def update_table(self):
        states = self.states_input.text().split()
        alphabet = self.alphabet_input.text().split() if self.index == 0 else ["a", "λ"]

        if states or alphabet:
            header_labels = (
                alphabet.copy()
                if isinstance(alphabet, list)
                else alphabet.copy().split()
            )
            self.transition_table.setRowCount(len(states))
            self.transition_table.setVerticalHeaderLabels(states)

            self.transition_table.setColumnCount(len(header_labels))
            self.transition_table.setHorizontalHeaderLabels(header_labels)
            if self.index == 1:
                self.alphabet_input.setText("a λ")

    def validate(self):
        if self.index == 0:
            self.validate_dfa()
        else:
            self.validate_nfa()

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
        self.subset_label = QLabel("Input a subset (e.g, q0, q1, q2):")
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
        validate_btn.clicked.connect(self.validate)

        self.layout.addWidget(validate_btn)
        self.layout.addWidget(self.result_label)
        self.layout.addWidget(self.graph_label)

        self.setLayout(self.layout)

    def validate_dfa(self):
        states = self.states_input.text().strip().split()
        alphabet = self.alphabet_input.text().strip().split()
        input_string = self.string_input.text().strip()
        transitions = {}

        # transitions from table
        for i, state in enumerate(states):
            for j, symbol in enumerate(alphabet):
                # Getting element according to state i and input j
                item = self.transition_table.item(i, j)  # State after it moves
                if item:
                    # print(f"State: {state}, Symbol: {symbol}, Item: {item}, Item text: {item.text()}, index :{i} {j}")
                    # If it exist -> add to transition dict with key is a transition move e.g (q0, a) -> q1 (value)
                    transitions[(state, symbol)] = item.text().strip()
                    # print(f"Transition at index {i} {j} : {transitions[(state,symbol)]}")
                else:
                    print(f"State: {state}, Symbol: {symbol}, Item is None")

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

        # At the end of string check if it is in final state or not
        if current in accept_state:
            self.result_label.setText(f"✅ Accepted {self.string_input.text()}")
        else:
            self.result_label.setText(f"❌ Rejected {self.string_input.text()}")

        # Draw DFA
        self.draw_graph(states, transitions, start_state, accept_state)

    def extendedTransition(self, subset_states, transitions):
        # Initialize with all subset states
        current_states = set(subset_states)

        # Apply lambda transitions first (lambda closure)
        new_states = current_states.copy()
        lambda_processed = set()

        while new_states != lambda_processed:
            for state in new_states - lambda_processed:
                if (state, "λ") in transitions:
                    new_states.update(transitions[(state, "λ")])
                lambda_processed.add(state)

        current_states = new_states

        # Process 'a' transitions for all current states
        next_states = set()
        for state in current_states:
            if (state, "a") in transitions:
                next_states.update(transitions[(state, "a")])

        # Update current states
        current_states = next_states

        # Apply lambda transitions again
        new_states = current_states.copy()
        lambda_processed = set()

        while new_states != lambda_processed:
            for state in new_states - lambda_processed:
                if (state, "λ") in transitions:
                    new_states.update(transitions[(state, "λ")])
                lambda_processed.add(state)

        current_states = new_states
        return current_states

    def validate_nfa(self):
        states = self.states_input.text().strip().split()
        single_state = self.single_state_input.text().strip()
        subset_input = self.subset_input.text().strip()
        transitions = {}

        # Parse transitions from table - NFA, each cell contains multiple states
        for i, state in enumerate(states):
            for j, symbol in enumerate(["a", "λ"]):  # NFA uses fixed symbols
                item = self.transition_table.item(i, j)
                if item and item.text().strip():
                    # Split by commas, spaces, or both and strip each state
                    dest_states = [
                        s.strip() for s in item.text().replace(",", " ").split()
                    ]
                    # Filter out empty strings
                    dest_states = [s for s in dest_states if s]
                    if dest_states:
                        transitions[(state, symbol)] = dest_states
                        print(
                            f"State: {state} Symbol :{symbol} Table : {transitions[(state, symbol)]} "
                        )
        # Parse subset input to handle different formats
        subset_states = self.parse_subset(subset_input)

        # Validation checks
        if not states:
            self.result_label.setText("❌ Please enter states")
            return
        if not single_state:
            self.result_label.setText("❌ Please enter a single state")
            return
        if not subset_input:
            self.result_label.setText("❌ Please enter a subset of states")
            return

        accept_states = set(self.final_states.text().split())
        singleReformat = [single_state]
        print(singleReformat)
        finalSingleset = self.extendedTransition(singleReformat, transitions)
        finalSubset = self.extendedTransition(subset_states, transitions)

        # Havent processed the subset input yet
        result_text = f"ETD: Extended Transition Function"
        result_text += f"\n✅ Single State: {single_state}"
        result_text += f"\n ETD of {single_state} : {', '.join(finalSingleset)}"
        result_text += f"\n✅ Subset: {', '.join(subset_states)}"
        result_text += f"\nETD of {subset_states} : {', '.join(finalSubset)}"

        self.result_label.setText(result_text)

        # Draw the NFA graph
        start_state = states[0]
        self.draw_nfa_graph(states, transitions, start_state, accept_states)

    def parse_subset(self, subset_text):
        """Parse a subset string like '{q0, q1, q2}' or 'q0,q1,q2' into a list of states"""
        # Remove curly braces, spaces around commas
        cleaned = subset_text.strip().replace("{", "").replace("}", "")
        # Split by commas and/or spaces
        result = [s.strip() for s in re.split(r"[,\s]+", cleaned)]
        # Remove empty strings
        return [s for s in result if s]

    def draw_nfa_graph(self, states, transitions, start, accepts):
        dot = Digraph()
        dot.attr(rankdir="LR")
        dot.node("", shape="none")
        dot.edge("", start)

        for state in states:
            shape = "doublecircle" if state in accepts else "circle"
            dot.node(state, shape=shape)

        for (from_state, symbol), to_states in transitions.items():
            for to_state in to_states:
                dot.edge(from_state, to_state, label=symbol)

        filename = "img_output"
        dot.render(filename, format="png", cleanup=True)
        self.graph_label.setPixmap(QPixmap(filename + ".png"))

    def draw_graph(self, states, transitions, start, accepts):
        dot = Digraph()
        dot.attr(rankdir="LR")
        dot.node("", shape="none")
        dot.edge("", start)

        for state in states:
            shape = "doublecircle" if state in accepts else "circle"
            dot.node(state, shape=shape)

        for (from_state, symbol), to_state in transitions.items():
            dot.edge(from_state, to_state, label=symbol)

        filename = "img_output"
        dot.render(filename, format="png", cleanup=True)
        self.graph_label.setPixmap(QPixmap(filename + ".png"))

    def switch_layout(self, index):
        self.index = index  # 0 for DFA, 1 for NFA
        # clear input placeholder
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
        self.alphabet_input.clear()

        # Clear transition table
        self.transition_table.clearContents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DFAApp()
    window.show()
    sys.exit(app.exec_())
