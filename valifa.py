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
        self.combo.currentIndexChanged.connect(self.switchLayout)

        self.index = 0

        self.statesInput = QLineEdit()
        self.alphabetInput = QLineEdit()
        self.stringInput = QLineEdit()
        self.finalStates = QLineEdit()

        self.transitionTable = QTableWidget()
        self.resultLabel = QLabel()
        self.graphLabel = QLabel()
        self.layout = QVBoxLayout()

        self.appUI()

    def updateTable(self):
        States = self.statesInput.text().split()
        alphabet = self.alphabetInput.text().split() if self.index == 0 else ["a", "λ"]

        if States or alphabet:
            if isinstance(alphabet, list):
                Header_labels = alphabet.copy()
            else:
                Header_labels = alphabet.split()

            self.transitionTable.setRowCount(len(States))
            self.transitionTable.setVerticalHeaderLabels(States)

            self.transitionTable.setColumnCount(len(Header_labels))
            self.transitionTable.setHorizontalHeaderLabels(Header_labels)

            if self.index == 1:
                self.alphabetInput.setText("a λ")

    def validate(self):
        if self.index == 0:
            self.validatedfa()
        else:
            self.validatenfa()

    def appUI(self):

        self.layout.addWidget(QLabel("Choose Finite Automata"))
        self.layout.addWidget(self.combo)

        self.layout.addWidget(QLabel("States (e.g., q0 q1 q2):"))
        self.layout.addWidget(self.statesInput)

        self.alphabetLabel = QLabel("Alphabet (e.g., a b or 0 1):")
        self.layout.addWidget(self.alphabetLabel)
        self.layout.addWidget(self.alphabetInput)

        # DFA
        self.stringLabel = QLabel("Input String:")
        self.layout.addWidget(self.stringLabel)
        self.layout.addWidget(self.stringInput)

        # NFA
        self.singleStatelabel = QLabel("Input Single State (e.g., q0):")
        self.singleStateinput = QLineEdit()
        self.subsetlabel = QLabel("Input a subset (e.g, q0, q1, q2):")
        self.subsetinput = QLineEdit()

        self.singleStatelabel.hide()
        self.singleStateinput.hide()
        self.subsetlabel.hide()
        self.subsetinput.hide()

        self.layout.addWidget(self.singleStatelabel)
        self.layout.addWidget(self.singleStateinput)
        self.layout.addWidget(self.subsetlabel)
        self.layout.addWidget(self.subsetinput)

        self.layout.addWidget(QLabel("Final States(e.g., q1 q2):"))
        self.layout.addWidget(self.finalStates)

        row = len(self.statesInput.text().split())
        self.transitionTable.setRowCount(row)
        self.transitionTable.setColumnCount(2)

        self.statesInput.textChanged.connect(self.updateTable)
        self.alphabetInput.textChanged.connect(self.updateTable)

        self.layout.addWidget(QLabel("Transition Table :"))
        self.layout.addWidget(self.transitionTable)

        check = QPushButton("Validate String")
        check.clicked.connect(self.validate)

        self.layout.addWidget(check)
        self.layout.addWidget(self.resultLabel)
        self.layout.addWidget(self.graphLabel)

        self.setLayout(self.layout)

    def validatedfa(self):
        states = self.statesInput.text().strip().split()
        alphabet = self.alphabetInput.text().strip().split()
        inputstring = self.stringInput.text().strip()
        transitions = {}

        for i, state in enumerate(states):
            for j, symbol in enumerate(alphabet):
                item = self.transitionTable.item(i, j)
                if item:
                    transitions[(state, symbol)] = item.text().strip()

        if not states or not alphabet:
            self.resultLabel.setText("❌ Please enter states and alphabet")
            return
        if not inputstring:
            self.resultLabel.setText("❌ Please enter an input string")
            return
        if not self.finalStates.text():
            self.resultLabel.setText("❌ Please specify at least one final state")
            return
        else:
            startState = states[0]

        acceptState = self.finalStates.text().split()


        current = startState
        for symbol in inputstring:
            if (current, symbol) in transitions:
                current = transitions[(current, symbol)]
            else:
                self.resultLabel.setText("❌ Rejected (invalid transition)")
                return

        if current in acceptState:
            self.resultLabel.setText(f"✅ Accepted {self.stringInput.text()}")
        else:
            self.resultLabel.setText(f"❌ Rejected {self.stringInput.text()}")

        self.graph(states, transitions, startState, acceptState)

    def extendedTransition(self, subsetStates, transitions):
        currentStates = set(subsetStates)

        newStates = currentStates.copy()
        lambdaClosure = set()

        while newStates != lambdaClosure:
            for state in newStates - lambdaClosure:
                if (state, "λ") in transitions:
                    newStates.update(transitions[(state, "λ")])
                lambdaClosure.add(state)

        currentStates = newStates
        nextStates = set()

        for state in currentStates:
            if (state, "a") in transitions:
                nextStates.update(transitions[(state, "a")])


        currentStates = nextStates
        # Final lambda closure
        newStates = currentStates.copy()
        lambdaClosure = set()

        while newStates != lambdaClosure:
            for state in newStates - lambdaClosure:
                if (state, "λ") in transitions:
                    newStates.update(transitions[(state, "λ")])
                lambdaClosure.add(state)

        currentStates = newStates
        return currentStates

    def validatenfa(self):
        states = self.statesInput.text().strip().split()
        singleState = self.singleStateinput.text().strip()
        subsetInput = self.subsetinput.text().strip()
        transitions = {}

        for i, state in enumerate(states):
            for j, symbol in enumerate(["a", "λ"]):
                item = self.transitionTable.item(i, j)
                if item and item.text().strip():
                    inputText = item.text().strip()
                    moveStates = inputText.split()
                    if moveStates:
                        transitions[(state, symbol)] = moveStates

        if not states:
            self.resultLabel.setText("❌ Please enter states")
            return
        if not singleState:
            self.resultLabel.setText("❌ Please enter a single state")
            return
        if not subsetInput:
            self.resultLabel.setText("❌ Please enter a subset of states")
            return

        acceptStates = set(self.finalStates.text().split())
        subsetStates = subsetInput.split(" ")
        singleReformat = [singleState]

        finalSingleset = self.extendedTransition(singleReformat, transitions)
        finalSubset = self.extendedTransition(subsetStates, transitions)

        resultText = f"ETD: Extended Transition Function"
        resultText += f"\n✅ Single State: {singleState}"
        resultText += f"\n ETD of {singleState} : {', '.join(finalSingleset)}"
        resultText += f"\n✅ Subset: {', '.join(subsetStates)}"
        resultText += f"\nETD of {subsetStates} : {', '.join(finalSubset)}"

        self.resultLabel.setText(resultText)

        startState = states[0]
        self.graph(states, transitions, startState, acceptStates)

    def graph(self, states, transitions, start, accepts):
        dot = Digraph()
        dot.attr(rankdir="LR")
        dot.node("", shape="none")
        dot.edge("", start)

        for state in states:
            shape = "doublecircle" if state in accepts else "circle"
            dot.node(state, shape=shape)

        if self.index == 1:
            for (fromState, symbol), toStates in transitions.items():
                for toState in toStates:
                    dot.edge(fromState, toState, label=symbol)
        else:
            for (fromState, symbol), toState in transitions.items():
                dot.edge(fromState, toState, label=symbol)

        fileName = "img_output"
        dot.render(fileName, format="png", cleanup=True)
        self.graphLabel.setPixmap(QPixmap(fileName + ".png"))

    def switchLayout(self, index):
        self.index = index  # 0 for DFA, 1 for NFA

        self.clearInputs()
        if index == 1:  
            self.stringLabel.hide()
            self.stringInput.hide()
            self.alphabetLabel.hide()
            self.alphabetInput.hide()

            self.singleStatelabel.show()
            self.singleStateinput.show()
            self.subsetlabel.show()
            self.subsetinput.show()
            self.alphabetInput.setText("a")
            self.setWindowTitle("ValiFA - NFA Mode")
            self.updateTable()

        else:
            self.stringLabel.show()
            self.stringInput.show()
            self.alphabetLabel.show()
            self.alphabetInput.show()

            self.singleStatelabel.hide()
            self.singleStateinput.hide()
            self.subsetlabel.hide()
            self.subsetinput.hide()
            self.setWindowTitle("ValiFA - DFA Mode")

    def clearInputs(self):
        self.stringInput.clear()
        self.singleStateinput.clear()
        self.subsetinput.clear()
        self.alphabetInput.clear()
        self.transitionTable.clearContents()
        self.resultLabel.setText("")
        self.graphLabel.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DFAApp()
    window.show()
    sys.exit(app.exec_())
