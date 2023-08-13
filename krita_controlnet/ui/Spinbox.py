from PyQt5.QtWidgets import QWidget, QSpinBox, QDoubleSpinBox, QSlider
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

class SpinBoxNoScroll(QSpinBox): 
    def wheelEvent(self, event):
        event.ignore()

class DoubleSpinBoxNoScroll(QDoubleSpinBox):
    def wheelEvent(self, event):
        event.ignore()

class SliderNoScroll(QSlider):
    def wheelEvent(self, event):
        event.ignore()

class CustomSpinBox(QWidget):
    """
    ===============================================================================================
    QSpinBox(もしくはQDoubleSpinBox)とQSliderを連動させたウィジェットを作成するクラス
    スピンボックスとスライダーが連動して同じ値を保持する
    parameters:
        minimum(int or float): スピンボックスとスライダーの最小値
        maximum(int or float): スピンボックスとスライダーの最大値
        step(int or float): スピンボックスとスライダーの増減ステップ。小数の場合QDoubleSpinBoxとなる
        layout(str): ウィジェットのレイアウト
                     "vertical"もしくは"horizontal"を指定可能
                     デフォルトは"horizontal"
    ===============================================================================================
    """
    def __init__(self, minimum, maximum, step, layout="horizontal"):
        super().__init__()

        if isinstance(step, int): # SpinBoxかDoubleSpinBoxか判定
            self.spinbox = SpinBoxNoScroll()
        else:
            self.spinbox = DoubleSpinBoxNoScroll()
        
        self.slider = SliderNoScroll()
        self.slider.setOrientation(Qt.Horizontal)
        
        self.spinbox.valueChanged.connect(self.spinboxChanged)
        self.slider.valueChanged.connect(self.sliderChanged)
        
        if layout == "vertical": self.layout = QVBoxLayout()
        elif layout == "horizontal": self.layout = QHBoxLayout()
        
        self.layout.addWidget(self.spinbox)
        self.layout.addWidget(self.slider)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.setSingleStep(step)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
    
    def setMinimum(self, value):
        self.spinbox.setMinimum(value)
        self.slider.setMinimum(value / self.spinbox.singleStep())
    
    def setMaximum(self, value):
        self.spinbox.setMaximum(value)
        self.slider.setMaximum(value / self.spinbox.singleStep())
    
    def setSingleStep(self, value):
        self.spinbox.setSingleStep(value)
        if isinstance(self.spinbox, QDoubleSpinBox):
            self.spinbox.setDecimals(len(str(value).split(".")[-1]))
    
    def spinboxChanged(self, value):
        value2 = self.round2(value / self.spinbox.singleStep())
        self.slider.setValue(value2)
    
    def sliderChanged(self, value):
        value2 = self.round2(float(value) * self.spinbox.singleStep())
        self.spinbox.setValue(value2)
    
    def round2(self, value):
        decimals = len(str(self.spinbox.singleStep()).split(".")[-1])
        return round(value, decimals)
    
    def setValue(self, value):
        self.spinbox.setValue(value)
    
    def value(self):
        return self.spinbox.value()
    
    def valueChanged(self, func):
        self.spinbox.valueChanged.connect(func)
    
    def setDecimals(self, value):
        self.spinbox.setDecimals(value)
    
    def setConf(self, min, max, step, value):
        self.setSingleStep(step)
        self.setMinimum(min)
        self.setMaximum(max)
        self.setValue(value)
        


