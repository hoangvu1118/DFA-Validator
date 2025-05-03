# 1.Valifa - Validator for Finite Automata
ValiFa has 2 modes
+ DFA mode: It is created for receiving input string and check if it is accepted by a DFA
+ NFA mode: User input the single state, and a substate T, the program will then output the **Extended Transition Function**
+ Finally, it will draw the graph for each of the mode

# 2.App screenshots
## DFA-Mode: Accepted - Rejected String
<img src="https://github.com/user-attachments/assets/aa28e0aa-f5f7-4d06-8a90-ea891c7a4a75" alt="Demo Image" width="400" height="500"/>
<img src="https://github.com/user-attachments/assets/335e59f3-bfbc-4b0e-8173-1bbcefe6f963" alt="Demo Image" width="400" height="500"/>

## NFA-Mode: Single State Extended Transition Function
<img src="https://github.com/user-attachments/assets/b1d1df18-0a14-49aa-b965-2105602c5b6e" alt="Demo Image" width="400" height="500"/>

# 3.Installation Instructions
To install these dependencies, you can run:
```
    pip install -r requirement.txt
```

## System Requirements
For this program, I use graphviz to draw the DFA/NFA graph
So for graphviz to work properly, you need to install the Graphviz software:

You can choose 1 out of below 3 options
1. Windows: Install from https://graphviz.org/download/ or using winget:
```
    winget install graphviz
```
2. Linux:
```
    sudo apt install graphviz
```
3. macOS:
```
    brew install graphviz
```

## Run Venv Environment

If using Windows run this in the bash
```
    eval "$(conda shell.bash hook)"
```
OR

1. Run the conda initialization command:
```
conda init bash
```
2. After running this command, you'll need to restart your terminal or reload your bash configuration:
```
source ~/.bashrc   # On Linux
# OR
source ~/.bash_profile   # On macOS
# OR on Windows with Git Bash
source ~/.bash_profile
```
