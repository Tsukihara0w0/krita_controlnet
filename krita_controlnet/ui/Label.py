from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QFont

class CustomLabel(QLabel):
    """
    =================================================================
    ラベル名を太字にしたQLabel
    prameter:
        text(str): ラベル名
        isbold(bool, optional): 太字にするか否か。デフォルトでtrue
    =================================================================
    """
    def __init__(self, text, isbold=True):
        super().__init__(text)
        
        self.custom_font = QFont()

        if isbold:
            self.custom_font.setBold(True)
            self.setFont(self.custom_font)
    
    def setPointSize(self, value):
        self.custom_font.setPointSize(value)
        self.setFont(self.custom_font)
