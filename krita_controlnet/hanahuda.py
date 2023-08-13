import os
import re
from functools import partial
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QWidget, QGroupBox, QScrollArea, QStackedWidget
from PyQt5.QtWidgets import QPushButton, QLineEdit, QToolButton
from PyQt5.QtGui import QIcon, QPixmap, QFontMetrics
from PyQt5.QtCore import Qt

from .api import *
from .ui.Label import *

class HanhudaWindow(QWidget):
    def __init__(self, main):
        super().__init__()
        
        self.main = main
        
        # list of paths
        self.textual_inversion_path = api.get_textual_inversion_dir()
        self.hypernetworks_path = api.get_hypernetworks_dir()
        self.checkpoints_path = api.get_checkpoints_dir()
        self.lora_path = api.get_lora_dir()
        self.paths_list = [
            self.textual_inversion_path,
            self.hypernetworks_path,
            self.checkpoints_path,
            self.lora_path
        ]
        
        # list of extensions
        self.extensions_list = [".safetensors", ".ckpt", ".pt"]

        # content button size
        self.content_button_width = 100
        self.content_button_height = self.content_button_width * 1.5
        self.max_row = 6 # init value
        
        # init progress
        self.content_total_count = 0
        self.content_progress = 0
        
        self.create_interface()
        self.connect_interface()
        self.toggle_button_clicked(0)
        
        self.setWindowTitle("Extra Networks")
        self.resize(940, 600)
    
    def create_interface(self):
        self.hlayout = QHBoxLayout(self)
        self.vlayout_left = QVBoxLayout()
        self.vlayout_right = QVBoxLayout()
        self.hlayout.addLayout(self.vlayout_left)
        self.hlayout.addLayout(self.vlayout_right)

        self.create_toggle_button_interface()
        self.create_subdir_button_interface()
        self.create_filter_interface()
        self.create_content_interface()
    
    def create_toggle_button_interface(self):
        groupbox = QGroupBox()
        self.vlayout_left.addWidget(groupbox)
        groupbox_layout = QVBoxLayout(groupbox)
        
        # adjust groupbox size
        groupbox.setFixedSize(150, 200)
        
        # create buttons
        self.toggle_button0 = QPushButton("Textual Inversion")
        self.toggle_button0.setCheckable(True)
        self.toggle_button1 = QPushButton("Hypernetworks")
        self.toggle_button1.setCheckable(True)
        self.toggle_button2 = QPushButton("Checkpoints")
        self.toggle_button2.setCheckable(True)
        self.toggle_button3 = QPushButton("Lora")
        self.toggle_button3.setCheckable(True)
        
        # adjust button height
        self.default_button_height = self.toggle_button0.sizeHint().height()
        self.adjusted_button_height = self.default_button_height * 1.5
        self.toggle_button0.setFixedHeight(self.adjusted_button_height)
        self.toggle_button1.setFixedHeight(self.adjusted_button_height)
        self.toggle_button2.setFixedHeight(self.adjusted_button_height)
        self.toggle_button3.setFixedHeight(self.adjusted_button_height)
        
        # add buttons
        groupbox_layout.addWidget(self.toggle_button0)
        groupbox_layout.addWidget(self.toggle_button1)
        groupbox_layout.addWidget(self.toggle_button2)
        groupbox_layout.addWidget(self.toggle_button3)
        groupbox_layout.addStretch()
    
    def create_subdir_button_interface(self):
        self.subdir_stacks = QStackedWidget()
        self.subdir_stacks.setFixedWidth(150)
        self.subdir_buttons = [] # list in list
        
        # create stacks
        for path in self.paths_list:
            page = QWidget()
            page_layout = QVBoxLayout(page)
            buttons = []
            subdirs_list = self.subdirs_list(path)

            # create scroll area
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area_content = QWidget()
            scroll_area_layout = QVBoxLayout(scroll_area_content)

            # create buttons inside the scroll area
            self.create_subdir_buttons(subdirs_list, buttons)
            self.subdir_buttons.append(buttons)
            
            # add buttons to scroll area layout
            for button in buttons:
                scroll_area_layout.addWidget(button)
            scroll_area_layout.addStretch()

            # set the scroll area content and add to the page layout
            scroll_area.setWidget(scroll_area_content)
            page_layout.addWidget(scroll_area)

            # add page to the stack
            self.subdir_stacks.addWidget(page)
        
        # add stacked widget to layout
        self.vlayout_left.addWidget(self.subdir_stacks)
    
    def create_subdir_buttons(self, subdirs: list, buttons: list):
        for subdir in subdirs:
            button = QPushButton(subdir)
            button.setFixedHeight(self.adjusted_button_height)
            buttons.append(button) # add button to list

    def subdirs_list(self, root_path, relative_path = ""):
        subdirs = []
        for item in os.listdir(os.path.join(root_path, relative_path)):
            item_path = os.path.join(relative_path, item)
            full_path = os.path.join(root_path, item_path)
            if os.path.isdir(full_path):
                subdirs.append(item_path)
                subdirs += self.subdirs_list(root_path, item_path)
        return subdirs
        
    def create_filter_interface(self):
        groupbox = QGroupBox()
        self.vlayout_right.addWidget(groupbox)
        groupbox_layout = QHBoxLayout(groupbox)
        
        # adjust groupbox size
        groupbox.setFixedHeight(80)

        # create filter content
        self.label = CustomLabel("") # change text at toggle_button clicked
        self.refresh_button = QToolButton()
        self.refresh_button.setText("🔄")
        self.refresh_button.setToolTip("refresh extra networks")
        self.clear_button = QToolButton()
        self.clear_button.setText("🗑️")
        self.clear_button.setToolTip("clear search text")
        self.filter_line = QLineEdit()
        self.filter_line.setFixedWidth(400)
        self.filter_line.setPlaceholderText("Search...")
        
        # add content to layout
        groupbox_layout.addWidget(self.label)
        groupbox_layout.addWidget(self.refresh_button)
        groupbox_layout.addWidget(self.clear_button)
        groupbox_layout.addWidget(self.filter_line)
    
    def create_content_interface(self):
        self.content_stacks = QStackedWidget()
        self.content_buttons = [] # list in list
        
        # create stacks
        for path in self.paths_list:
            page = QWidget()
            page_layout = QVBoxLayout(page)
            buttons = []
            content_dict = self.files_and_images_dict(path, self.extensions_list)

            # create scroll area
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area_content = QWidget()
            scroll_area.setWidget(scroll_area_content)
            scroll_area_layout = QGridLayout(scroll_area_content)

            # create button_widgets inside the scroll area
            self.create_content_buttons(content_dict, buttons)
            self.content_buttons.append(buttons)
            
            # add button_widgets to scroll area layout
            for i, widget in enumerate(buttons):
                row = i // self.max_row
                col = i % self.max_row
                scroll_area_layout.addWidget(widget, row, col)
            scroll_area_layout.setSpacing(0)

            # add the scroll area to the page layout
            scroll_area_content.setLayout(scroll_area_layout)
            page_layout.addWidget(scroll_area)

            # add page to stack
            self.content_stacks.addWidget(page)
        
        # add stacked widget to layout
        self.vlayout_right.addWidget(self.content_stacks)
    
    def create_content_buttons(self, dict: dict, buttons: list):
        for key in dict.keys():
            # create button
            button = QPushButton()
            button.setFixedSize(self.content_button_width, self.content_button_height)
            button.setToolTip(dict[key]["path"])

            # thmbnail setting
            image_path = dict[key]["image_path"]
            if image_path != None:
                pixmap = QPixmap(image_path)
                if pixmap.isNull():
                    pixmap = QPixmap(image_path, "1")
                pixmap = pixmap.scaled(self.content_button_width - 10, pixmap.height(), Qt.KeepAspectRatio)
                icon = QIcon(pixmap)
                button.setIcon(icon)
                button.setIconSize(pixmap.rect().size())
            
            # label setting
            label = CustomLabel(key)
            label.setFixedWidth(self.content_button_width)
            label.setAlignment(Qt.AlignHCenter)
            # ellpsis
            fm = QFontMetrics(label.font())
            text_width = fm.width(key)
            label_width = label.width()
            if text_width > label_width:
                elided_text = fm.elidedText(key, Qt.ElideRight, label_width)
                label.setText(elided_text)
            
            button_widget = QWidget()
            button_layout = QVBoxLayout(button_widget)
            button_layout.addWidget(button)
            button_layout.addWidget(label)
            button_layout.setSpacing(0)
            
            buttons.append(button_widget)
    
    def files_and_images_dict(self, root_path: str, extensions: list):
        reslut = {}
        for root, dirs, files in os.walk(root_path, followlinks=True):
            for file_name in files:
                if any(file_name.endswith(ext) for ext in extensions):
                    relative_path_with_extension = os.path.relpath(os.path.join(root, file_name), root_path)
                    relative_path = os.path.splitext(relative_path_with_extension)[0]
                    file_name_without_extention = os.path.splitext(file_name)[0]
                    image_extentions = [".png", ".preview.png", ".jpg", ".preview.jpg", ".jpeg", ".preview.jpeg"]
                    image_path = None
                    for img_ext in image_extentions:
                        potential_image_path = os.path.join(root, file_name_without_extention + img_ext)
                        if os.path.exists(potential_image_path):
                            image_path = potential_image_path
                            break
                    value_dict = {"path": relative_path, "image_path": image_path}
                    reslut[file_name_without_extention] = value_dict
        return reslut
    
    def connect_interface(self):
        # toggle button--------------------------------------------------------
        self.toggle_button0.clicked.connect(lambda: self.toggle_button_clicked(0))
        self.toggle_button1.clicked.connect(lambda: self.toggle_button_clicked(1))
        self.toggle_button2.clicked.connect(lambda: self.toggle_button_clicked(2))
        self.toggle_button3.clicked.connect(lambda: self.toggle_button_clicked(3))
        
        # subdir button--------------------------------------------------------
        for buttons in self.subdir_buttons:
            for button in buttons:
                # 既存のシグナルを取得
                try:
                    existing_connection = button.receivers(button.clicked)
                except TypeError:
                    existing_connection = None
                
                # 既存のシグナルがあれば削除
                if existing_connection:
                    button.clicked.disconnect()
                
                subdir = button.text() # get text
                button.clicked.connect(partial(self.subdir_button_clicked, subdir))
        
        # filter: refresh button-----------------------------------------------
        # 既存のシグナルを取得
        try:
            existing_connection = self.refresh_button.receivers(self.refresh_button.clicked)
        except TypeError:
            existing_connection = None
        
        # 既存のシグナルがあれば削除
        if existing_connection:
            self.refresh_button.clicked.disconnect()
        
        self.refresh_button.clicked.connect(self.refresh_button_clicked)
        
        # filter: clear button-------------------------------------------------
        self.clear_button.clicked.connect(self.clear_button_clicked)
        
        # filter: filter line--------------------------------------------------
        self.filter_line.textChanged.connect(self.filter_changed)
        
        # content button-------------------------------------------------------
        for buttons in self.content_buttons:
            for button_widget in buttons:
                button = button_widget.findChild(QPushButton)
                if button:
                    # 既存のシグナルを取得
                    try:
                        existing_connection = button.receivers(button.clicked)
                    except TypeError:
                        existing_connection = None
                
                # 既存のシグナルがあれば削除
                    if existing_connection:
                        button.clicked.disconnect()
                    
                    relative_path = button.toolTip()
                    file_name = os.path.splitext(os.path.basename(relative_path))[0]
                    button.clicked.connect(partial(self.content_button_clicked, relative_path, file_name))
    
    def toggle_button_clicked(self, index):
        # subdir area
        self.subdir_stacks.setCurrentIndex(index)
        
        # filter area and toggle button
        self.all_toggle_button_checked_false()
        if index == 0: 
            self.label.setText("Textual Inversion")
            self.toggle_button0.setChecked(True)
        elif index == 1: 
            self.label.setText("Hypernetworks")
            self.toggle_button1.setChecked(True)
        elif index == 2: 
            self.label.setText("Checkpoints")
            self.toggle_button2.setChecked(True)
        elif index == 3: 
            self.label.setText("Lora")
            self.toggle_button3.setChecked(True)
        else: 
            self.label.setText("Error index")

        # filter clear
        self.filter_line.setText("")
        
        # content area
        self.content_stacks.setCurrentIndex(index)
    
    def all_toggle_button_checked_false(self):
        self.toggle_button0.setChecked(False)
        self.toggle_button1.setChecked(False)
        self.toggle_button2.setChecked(False)
        self.toggle_button3.setChecked(False)
    
    def subdir_button_clicked(self, subdir):
        text = subdir + "\\"
        filter_text = self.filter_line.text()
        if filter_text == text:
            self.filter_line.setText("")
        else:
            self.filter_line.setText(text)
    
    def refresh_button_clicked(self):
        original_title = self.windowTitle()
        self.content_total_count = self.calc_content_total_count()
        self.content_progress = 0

        for page_index in range(self.content_stacks.count()):            
            # subdir
            self.recreate_buttons_per_stack(self.subdir_stacks, page_index)
            # content_button
            self.recreate_buttons_per_stack(self.content_stacks, page_index)
        
        # reset progress
        self.setWindowTitle(original_title)

        # reconnect
        self.connect_interface()
     
    def recreate_buttons_per_stack(self, stacks, page_index):
        page = stacks.widget(page_index)
        scroll_area = page.findChild(QScrollArea)
        layout = scroll_area.widget().layout()
        path = self.paths_list[page_index]

        # delete widget in layout
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                layout.removeWidget(widget)
                widget.hide()
            else:
                layout.removeItem(item)
        
        if stacks == self.subdir_stacks:
            buttons = []
            # re create subir list from path
            subdirs_list = self.subdirs_list(path)
            
            # re create subdir buttons
            self.create_subdir_buttons(subdirs_list, buttons)
            self.subdir_buttons[page_index] = buttons
            
            # add buttons to scroll area layout
            for button in buttons:
                layout.addWidget(button)
                button.show()
            layout.addStretch()
        
        elif stacks == self.content_stacks:
            buttons = []
            # re create content dict from path and extensions
            content_dict = self.files_and_images_dict(path, self.extensions_list)

            # re create content buttons
            self.create_content_buttons(content_dict, buttons)
            self.content_buttons[page_index] = buttons
            
            # add buttons to scroll area layout
            for i, widget in enumerate(buttons):
                row = i // self.max_row
                col = i % self.max_row
                layout.addWidget(widget, row, col)
                widget.show()
                # show progress on window title
                self.content_progress += 1
                self.setWindowTitle(f"Loading: {self.content_progress} / {self.content_total_count}")
            layout.setSpacing(0)
    
    def clear_button_clicked(self):
        self.filter_line.setText("")
    
    def filter_changed(self):
        filtered_text = self.filter_line.text().lower()
        page_index = self.content_stacks.currentIndex()
        page = self.content_stacks.widget(page_index)
        scroll_area = page.findChild(QScrollArea)
        layout = scroll_area.widget().layout()
        buttons = self.content_buttons[page_index]
        
        # delete widgets from layout
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                layout.removeWidget(widget)
                widget.hide()
        
        # filtered widget
        filtered_widgets = []
        for widget in buttons:
            button = widget.findChild(QPushButton)
            if button is not None:
                tooltip = button.toolTip().lower()
                if filtered_text in tooltip:
                    filtered_widgets.append(widget)
        
        while len(filtered_widgets) < self.max_row:
            dummy = QWidget()
            filtered_widgets.append(dummy)
            
        # add filtered widgets to scroll area layout
        for i, widget in enumerate(filtered_widgets):
            row = i // self.max_row
            col = i % self.max_row
            layout.addWidget(widget, row, col)
            widget.show()
        
    def content_button_clicked(self, relative_path, file_name):
        page_index = self.content_stacks.currentIndex()
        # textual inversion
        if page_index == 0:
            insert_text = file_name
            search_text = insert_text
            plain_text = self.main.negative_prompt.toPlainText()
            cursor = self.main.negative_prompt.textCursor()
            current_position = cursor.position()
            if not search_text in plain_text: # insert
                cursor.insertText(insert_text + " ")
            else: # delete
                deleted_text = plain_text.replace(search_text, "", 1)
                self.main.negative_prompt.setPlainText(deleted_text)
            cursor.setPosition(current_position)
            self.main.negative_prompt.setTextCursor(cursor)
        
        # hypernetworks
        elif page_index == 1:
            insert_text = f"<hypernet:{file_name}:1.0>"
            search_text = re.compile(rf"<hypernet:{re.escape(file_name)}:[\d.]+>")
            plain_text = self.main.prompt.toPlainText()
            cursor = self.main.prompt.textCursor()
            current_position = cursor.position()
            if not search_text.search(plain_text): # insert
                cursor.insertText(insert_text + " ")
            else: # delete
                deleted_text = re.sub(search_text, "", plain_text, count=1)
                self.main.prompt.setPlainText(deleted_text)
            cursor.setPosition(current_position)
            self.main.prompt.setTextCursor(cursor)
        
        # checkpoints
        elif page_index == 2:
            relative_path = relative_path.replace("\\", "_")
            self.main.checkpoint.setCurrentText(relative_path)
        
        # lora
        elif page_index == 3:
            insert_text = f"<lora:{file_name}:1.0>"
            search_text = re.compile(rf"<lora:{re.escape(file_name)}:[\d.]+>")
            plain_text = self.main.prompt.toPlainText()
            cursor = self.main.prompt.textCursor()
            current_position = cursor.position()
            if not search_text.search(plain_text): # insert
                cursor.insertText(insert_text + " ")
            else: # delete
                deleted_text = re.sub(search_text, "", plain_text, count=1)
                self.main.prompt.setPlainText(deleted_text)
            cursor.setPosition(current_position)
            self.main.prompt.setTextCursor(cursor)
        
        else:
            print("error page index")

    def calc_content_total_count(self):
        total_count = 0
        for path in self.paths_list:
            for root, dirs, files in os.walk(path, followlinks=True):
                for file_name in files:
                    if any(file_name.endswith(ext) for ext in self.extensions_list):
                        total_count += 1
        return total_count