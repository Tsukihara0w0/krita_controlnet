from PyQt5.QtWidgets import QWidget, QCheckBox, QPushButton
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout

class CollapsibleWidget(QWidget):
    """
    ===============================================================================================
    ユーザーが内容を表示・非表示できる折りたたみ式のウィジェットを作成するためのクラス
    QPushButtonと任意のQWidgetを組み合わせたコンテナ型のウィジェット
    parameters:
        title(str): ボタンのテキスト
        content_widget(QWidget): 表示・非表示できる中身のウィジェット
        checkable(boor, optional): ボタンの横にチェックボックスを表示するか否か。デフォルトでTrue
    ===============================================================================================
    """
    def __init__(self, title, content_widget, checkable=True):
        super().__init__()

        self.title = title
        self.content_widget = content_widget
        self.is_collapsed = True

        # チェックボックスの有無
        if checkable == True:
            self.checkbox = QCheckBox()

            self.toggle_button = QPushButton(self.title)
            self.toggle_button.setCheckable(True)
            self.toggle_button.setChecked(False)

            self.button_layout = QHBoxLayout()
            self.button_layout.addWidget(self.checkbox)
            self.button_layout.addWidget(self.toggle_button)
            self.button_layout.addStretch()

            self.layout = QVBoxLayout()
            self.layout.addLayout(self.button_layout)
            self.layout.addWidget(self.content_widget)
        else:
            self.toggle_button = QPushButton()
            self.toggle_button.setCheckable(True)
            self.toggle_button.setChecked(False)

            self.layout = QVBoxLayout()
            self.layout.addWidget(self.toggle_button)
            self.layout.addWidget(self.content_widget)
        
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.toggle_button.clicked.connect(self.toggle_content_visibility)
        
        # 閉じた状態で始めるために一度表示切り替え
        self.toggle_content_visibility()
    
    def toggle_content_visibility(self):
        self.is_collapsed = not self.is_collapsed
        self.toggle_button.setChecked(self.is_collapsed)
        self.content_widget.setVisible(self.is_collapsed)
    
    def isChecked(self):
        if hasattr(self, "checkbox"):
            return self.checkbox.isChecked()
        else:
            return None