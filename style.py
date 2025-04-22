def get_stylesheet():
    return """
    QWidget {
        background-color: #f5f5f5;
    }
    
    QLineEdit {
        background-color: #FFD580;
        border: 1px solid black;
        border-radius: 4px;
        padding: 6px;
        font-size: 13px;
    }

    QLabel {
        font-weight: bold;
        color: #2C3E50;
        font-size: 14px;
        margin-top: 8px;
    }

    QTableWidget {
        gridline-color: #7F8C8D;
        background-color: white;
        alternate-background-color: #ECF0F1;
        selection-background-color: #3498DB;
    }
    
    QHeaderView::section {
        background-color: #E67E22;
        color: white;
        font-weight: bold;
        padding: 4px;
        border: 1px solid #D35400;
    }
    
    QPushButton {
        font-weight: bold;
        background-color: #E67E22;
        color: white;
        border-radius: 4px;
        padding: 8px 16px;
        border: none;
    }
    
    QPushButton:hover {
        background-color: #E74C3C;
    }
    
    QPushButton:pressed {
        background-color: #A93226;
    }
    
    QComboBox {
        background-color: #FFD580;
        border: 1px solid black;
        border-radius: 4px;
        padding: 4px;
        color: black;
        font-weight: bold;
        min-height: 25px;
    }
    
    QComboBox::drop-down {
        border: 0px;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        width: 14px;
        height: 14px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #FFEFD5;
        selection-background-color: #E67E22;
        selection-color: white;
    }
    
    .result-accepted {
        color: #27AE60;
        font-weight: bold;
    }
    
    .result-rejected {
        color: #E74C3C;
        font-weight: bold;
    }
    """
