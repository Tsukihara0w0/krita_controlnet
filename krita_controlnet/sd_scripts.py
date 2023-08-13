import os
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QWidget, QScrollArea, QStackedWidget
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QComboBox, QCheckBox
from PyQt5.QtWidgets import QPushButton

from .api import *
from .utils import *
from .ui.Label import *
from .ui.PlainTextEdit import *
from .ui.Spinbox import *

class ScriptsWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # sd dir
        self.sd_dir = api.get("sdapi/v1/cmd-flags", "data_dir")
        
        # list of scripts
        scripts = api.get("sdapi/v1/scripts")
        self.scripts_list = list(set(scripts["txt2img"]) | set(scripts["img2img"]))
        """
        対応予定リスト
        ADetailer, tiledVae, tiledDiffusion, CD Tuner, negpip
        UI作ってリストにないやつはhide
        """
        
        self.create_interface()
        self.connect_interface()
        
        
        self.setWindowTitle("Scripts")
        self.resize(940, 600)
        
    def create_interface(self):
        self.layout = QHBoxLayout(self)

        self.create_toggle_button_interface()
        self.create_setting_stacks()
    
    
    def create_toggle_button_interface(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area_content = QWidget()
        scroll_area_layout = QVBoxLayout(scroll_area_content)

        # addjust scroll area size
        scroll_area.setFixedWidth(200)

        # create buttons
        # ADetailer
        self.adetailer_enable = QCheckBox()
        self.adetailer_toggle_button = QPushButton("ADetailer")
        button_height = self.adetailer_toggle_button.sizeHint().height() * 1.5
        self.adetailer_toggle_button.setFixedHeight(button_height)
        adetailer_toggle_layout = QHBoxLayout()
        adetailer_toggle_layout.addWidget(self.adetailer_enable)
        adetailer_toggle_layout.addWidget(self.adetailer_toggle_button)
        adetailer_toggle_layout.addStretch()
        if not "adetailer" in self.scripts_list:
            self.adetailer_enable.hide()
            self.adetailer_toggle_button.hide()
        
        # Tiled Diffusion
        self.tiled_diffusion_enable = QCheckBox()
        self.tiled_diffusion_toggle_button = QPushButton("Tiled Diffusion")
        self.tiled_diffusion_toggle_button.setFixedHeight(button_height)
        tiled_diffusion_layout = QHBoxLayout()
        tiled_diffusion_layout.addWidget(self.tiled_diffusion_enable)
        tiled_diffusion_layout.addWidget(self.tiled_diffusion_toggle_button)
        tiled_diffusion_layout.addStretch()
        if not "tiled diffusion" in self.scripts_list:
            self.tiled_diffusion_enable.hide()
            self.tiled_diffusion_toggle_button.hide()

        # Tiled VAE
        self.tiled_vae_enable = QCheckBox()
        self.tiled_vae_enable.setChecked(True)
        self.tiled_vae_toggle_button = QPushButton("Tiled VAE")
        self.tiled_vae_toggle_button.setFixedHeight(button_height)
        tiled_vae_layout = QHBoxLayout()
        tiled_vae_layout.addWidget(self.tiled_vae_enable)
        tiled_vae_layout.addWidget(self.tiled_vae_toggle_button)
        tiled_vae_layout.addStretch()
        if not "tiled vae" in self.scripts_list:
            self.tiled_vae_enable.hide()
            self.tiled_vae_toggle_button.hide()
        
        # CD Tuner
        self.cd_tuner_enable = QCheckBox()
        self.cd_tuner_toggle_button = QPushButton("CD Tuner")
        self.cd_tuner_toggle_button.setFixedHeight(button_height)
        cd_tuner_layout = QHBoxLayout()
        cd_tuner_layout.addWidget(self.cd_tuner_enable)
        cd_tuner_layout.addWidget(self.cd_tuner_toggle_button)
        cd_tuner_layout.addStretch()
        if not "cd tuner" in self.scripts_list:
            self.cd_tuner_enable.hide()
            self.cd_tuner_toggle_button.hide()
        
        # negpip
        self.negpip_enable = QCheckBox()
        self.negpip_enable.setChecked(True)
        self.negpip_toggle_button = QPushButton("NegPip")
        self.negpip_toggle_button.setFixedHeight(button_height)
        negpip_layout = QHBoxLayout()
        negpip_layout.addWidget(self.negpip_enable)
        negpip_layout.addWidget(self.negpip_toggle_button)
        negpip_layout.addStretch()
        if not "negpip" in self.scripts_list:
            self.negpip_enable.hide()
            self.negpip_toggle_button.hide()
        
        # regional prompter
        self.regional_prompter_enable = QCheckBox()
        self.regional_prompter_toggle_button = QPushButton("Regional Prompter")
        self.regional_prompter_toggle_button.setFixedHeight(button_height)
        regional_prompter_layout = QHBoxLayout()
        regional_prompter_layout.addWidget(self.regional_prompter_enable)
        regional_prompter_layout.addWidget(self.regional_prompter_toggle_button)
        regional_prompter_layout.addStretch()
        if not "regional prompter" in self.scripts_list:
            self.regional_prompter_enable.hide()
            self.regional_prompter_toggle_button.hide()

        # 他あれば追記
        
        
        # add layouts to acroll area layout
        scroll_area_layout.addLayout(adetailer_toggle_layout)
        scroll_area_layout.addLayout(tiled_diffusion_layout)
        scroll_area_layout.addLayout(tiled_vae_layout)
        scroll_area_layout.addLayout(cd_tuner_layout)
        scroll_area_layout.addLayout(negpip_layout)
        scroll_area_layout.addLayout(regional_prompter_layout)
        scroll_area_layout.addStretch()
        
        # set the scroll area content and add to the main layout
        scroll_area.setWidget(scroll_area_content)
        self.layout.addWidget(scroll_area)


    def create_setting_stacks(self):
        self.setting_stacks = QStackedWidget()
        dummy = QWidget()
        self.setting_stacks.addWidget(dummy)
        
        # 各スタックを作成
        self.create_adetailer_stack()
        self.create_tiled_diffusion_stack()
        self.create_tiled_vae_stack()
        self.create_cd_tuner_stack()
        self.create_negpip_stack()
        self.create_regional_prompter_stack()
        
        self.layout.addWidget(self.setting_stacks)
    
    def create_adetailer_stack(self):
        page = QWidget()
        page_layout = QVBoxLayout(page)
        
        # create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area_content = QWidget()
        scroll_area_layout = QVBoxLayout(scroll_area_content)

        # create setting UI
        self.adetailer_label = CustomLabel("ADetailer")
        self.adetailer_label.setPointSize(20)
        scroll_area_layout.addWidget(self.adetailer_label)
        scroll_area_layout.addWidget(create_line())
        
        self.adetailer_model_label = CustomLabel("ADetailer model")
        self.adetailer_model = QComboBox()
        adetailer_addedmodel_path = os.path.join(self.sd_dir, "models", "adetailer")
        adetailer_addedmodel_list = api.file_lists(adetailer_addedmodel_path, [".pt"])
        adetailer_model_list = ["None", "face_yolov8n.pt", "face_yolov8s.pt", "hand_yolov8n.pt", 
                                "person_yolov8n_seg.pt", "person_yolov8s_seg.pt", 
                                "mediapipe_face_full", "mediapipe_face_short", 
                                "mediapipe_face_mesh", "mediapipe_face_mesh_eyes_only"] + adetailer_addedmodel_list
        self.adetailer_model.addItems(adetailer_model_list)
        scroll_area_layout.addWidget(self.adetailer_model_label)
        scroll_area_layout.addWidget(self.adetailer_model)
        
        self.adetailer_prompt_label = CustomLabel("ADetailer prompt")
        self.adetailer_prompt = CustomPlainTextEdit()
        self.adetailer_prompt.setFixedHeight(80)
        self.adetailer_prompt.setPlaceholderText("if blank, the main prompt is used.")
        scroll_area_layout.addWidget(self.adetailer_prompt_label)
        scroll_area_layout.addWidget(self.adetailer_prompt)

        self.adetailer_negative_prompt_label = CustomLabel("ADetailer negative prompt")
        self.adetailer_negative_prompt = CustomPlainTextEdit()
        self.adetailer_negative_prompt.setFixedHeight(80)
        self.adetailer_negative_prompt.setPlaceholderText("if blank, the main negative prompt is used.")
        scroll_area_layout.addWidget(self.adetailer_negative_prompt_label)
        scroll_area_layout.addWidget(self.adetailer_negative_prompt)

        scroll_area_layout.addWidget(create_line())
        
        self.adetailer_model_label_2nd = CustomLabel("ADetailer model 2nd")
        self.adetailer_model_2nd = QComboBox()
        self.adetailer_model_2nd.addItems(adetailer_model_list)
        scroll_area_layout.addWidget(self.adetailer_model_label_2nd)
        scroll_area_layout.addWidget(self.adetailer_model_2nd)

        self.adetailer_prompt_label_2nd = CustomLabel("ADetailer prompt 2nd")
        self.adetailer_prompt_2nd = CustomPlainTextEdit()
        self.adetailer_prompt_2nd.setFixedHeight(80)
        self.adetailer_prompt_2nd.setPlaceholderText("if blank, the main prompt is used.")
        scroll_area_layout.addWidget(self.adetailer_prompt_label_2nd)
        scroll_area_layout.addWidget(self.adetailer_prompt_2nd)

        self.adetailer_negative_prompt_label_2nd = CustomLabel("ADetailer negative prompt 2nd")
        self.adetailer_negative_prompt_2nd = CustomPlainTextEdit()
        self.adetailer_negative_prompt_2nd.setFixedHeight(80)
        self.adetailer_negative_prompt_2nd.setPlaceholderText("if blank, the main negative prompt is used.")
        scroll_area_layout.addWidget(self.adetailer_negative_prompt_label_2nd)
        scroll_area_layout.addWidget(self.adetailer_negative_prompt_2nd)

        scroll_area_layout.addStretch()
        
        # set the scroll area content and add to the page layout
        scroll_area.setWidget(scroll_area_content)
        page_layout.addWidget(scroll_area)

        # add page to the stack
        self.setting_stacks.addWidget(page)
    
    
    def create_tiled_diffusion_stack(self):
        page = QWidget()
        page_layout = QVBoxLayout(page)
        
        # create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area_content = QWidget()
        scroll_area_layout = QVBoxLayout(scroll_area_content)

        # create setting UI
        self.tiled_diffusion_label = CustomLabel("Tiled Diffusion")
        self.tiled_diffusion_label.setPointSize(20)
        scroll_area_layout.addWidget(self.tiled_diffusion_label)
        scroll_area_layout.addWidget(create_line())
        
        self.tiled_diffusion_method_label = CustomLabel("Method")
        self.tiled_diffusion_method = QComboBox()
        self.tiled_diffusion_method.addItems(["MultiDiffusion", "Mixture of Diffusers"])
        scroll_area_layout.addWidget(self.tiled_diffusion_method_label)
        scroll_area_layout.addWidget(self.tiled_diffusion_method)
        
        self.tiled_diffusion_latent_width_label = CustomLabel("Latent tile width")
        self.tiled_diffusion_latent_width = CustomSpinBox(16, 256, 16)
        self.tiled_diffusion_latent_width.setValue(96)
        scroll_area_layout.addWidget(self.tiled_diffusion_latent_width_label)
        scroll_area_layout.addWidget(self.tiled_diffusion_latent_width)

        self.tiled_diffusion_latent_height_label = CustomLabel("Latent tile height")
        self.tiled_diffusion_latent_height = CustomSpinBox(16, 256, 16)
        self.tiled_diffusion_latent_height.setValue(96)
        scroll_area_layout.addWidget(self.tiled_diffusion_latent_height_label)
        scroll_area_layout.addWidget(self.tiled_diffusion_latent_height)
        
        self.tiled_diffusion_latent_overlap_label = CustomLabel("Latent tile overlap")
        self.tiled_diffusion_latent_overlap = CustomSpinBox(0, 256, 4)
        self.tiled_diffusion_latent_overlap.setValue(48)
        scroll_area_layout.addWidget(self.tiled_diffusion_latent_overlap_label)
        scroll_area_layout.addWidget(self.tiled_diffusion_latent_overlap)

        self.tiled_diffusion_latent_batch_label = CustomLabel("Latent tile batch size")
        self.tiled_diffusion_latent_batch = CustomSpinBox(1, 8, 1)
        self.tiled_diffusion_latent_batch.setValue(4)
        scroll_area_layout.addWidget(self.tiled_diffusion_latent_batch_label)
        scroll_area_layout.addWidget(self.tiled_diffusion_latent_batch)
        
        scroll_area_layout.addWidget(create_line())
        scroll_area_layout.addWidget(CustomLabel("t2i設定"))
        
        self.tiled_diffusion_overwrite = QCheckBox("Overwite image size")
        self.tiled_diffusion_overwrite.setChecked(True)
        scroll_area_layout.addWidget(self.tiled_diffusion_overwrite)

        self.tiled_diffusion_width_label = CustomLabel("Image width")
        self.tiled_diffusion_width = CustomSpinBox(256, 16384, 16)
        self.tiled_diffusion_width.setValue(1024)
        scroll_area_layout.addWidget(self.tiled_diffusion_width_label)
        scroll_area_layout.addWidget(self.tiled_diffusion_width)

        self.tiled_diffusion_height_label = CustomLabel("Image height")
        self.tiled_diffusion_height = CustomSpinBox(256, 16384, 16)
        self.tiled_diffusion_height.setValue(1024)
        scroll_area_layout.addWidget(self.tiled_diffusion_height_label)
        scroll_area_layout.addWidget(self.tiled_diffusion_height)
        
        scroll_area_layout.addWidget(create_line())
        scroll_area_layout.addWidget(CustomLabel("i2i設定"))
        
        self.tiled_diffusion_keepsize = QCheckBox("Keep input image size")
        self.tiled_diffusion_keepsize.setChecked(True)
        scroll_area_layout.addWidget(self.tiled_diffusion_keepsize)
        
        self.tiled_diffusion_upscaler_label = CustomLabel("Upscaler")
        self.tiled_diffusion_upscaler = QComboBox()
        upscaler_list = api.get_upscaler_list()
        self.tiled_diffusion_upscaler.addItems(upscaler_list)
        scroll_area_layout.addWidget(self.tiled_diffusion_upscaler_label)
        scroll_area_layout.addWidget(self.tiled_diffusion_upscaler)

        self.tiled_diffusion_scale_label = CustomLabel("Scale Factor")
        self.tiled_diffusion_scale = CustomSpinBox(1, 8 ,0.05)
        self.tiled_diffusion_scale.setValue(2)
        scroll_area_layout.addWidget(self.tiled_diffusion_scale_label)
        scroll_area_layout.addWidget(self.tiled_diffusion_scale)

        self.tiled_diffusion_noise_enable = QCheckBox("Enable Noise Inversion")
        scroll_area_layout.addWidget(self.tiled_diffusion_noise_enable)

        self.tiled_diffusion_noise_step_label = CustomLabel("Inversion steps")
        self.tiled_diffusion_noise_step = CustomSpinBox(1, 200, 1)
        self.tiled_diffusion_noise_step.setValue(10)
        scroll_area_layout.addWidget(self.tiled_diffusion_noise_step_label)
        scroll_area_layout.addWidget(self.tiled_diffusion_noise_step)

        self.tiled_diffusion_noise_retouch_label = CustomLabel("Retouch")
        self.tiled_diffusion_noise_retouch = CustomSpinBox(0, 100, 0.1)
        self.tiled_diffusion_noise_retouch.setValue(1)
        scroll_area_layout.addWidget(self.tiled_diffusion_noise_retouch_label)
        scroll_area_layout.addWidget(self.tiled_diffusion_noise_retouch)

        self.tiled_diffusion_noise_renoise_strength_label = CustomLabel("Renoise strength")
        self.tiled_diffusion_noise_renoise_strength = CustomSpinBox(0, 2, 0.01)
        self.tiled_diffusion_noise_renoise_strength.setValue(1)
        scroll_area_layout.addWidget(self.tiled_diffusion_noise_renoise_strength_label)
        scroll_area_layout.addWidget(self.tiled_diffusion_noise_renoise_strength)

        self.tiled_diffusion_noise_renoise_size_label = CustomLabel("Renoise kernel size")
        self.tiled_diffusion_noise_renoise_size = CustomSpinBox(2, 512, 1)
        self.tiled_diffusion_noise_renoise_size.setValue(64)
        scroll_area_layout.addWidget(self.tiled_diffusion_noise_renoise_size_label)
        scroll_area_layout.addWidget(self.tiled_diffusion_noise_renoise_size)

        scroll_area_layout.addStretch()
        
        # set the scroll area content and add to the page layout
        scroll_area.setWidget(scroll_area_content)
        page_layout.addWidget(scroll_area)

        # add page to the stack
        self.setting_stacks.addWidget(page)
    
    
    def create_tiled_vae_stack(self):
        page = QWidget()
        page_layout = QVBoxLayout(page)
        
        # create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area_content = QWidget()
        scroll_area_layout = QVBoxLayout(scroll_area_content)

        # create setting UI
        self.tiled_vae_label = CustomLabel("Tiled VAE")
        self.tiled_vae_label.setPointSize(20)
        scroll_area_layout.addWidget(self.tiled_vae_label)
        scroll_area_layout.addWidget(create_line())
        
        self.tiled_vae_encoder_size_label = CustomLabel("Encoder Tile Size")
        self.tiled_vae_encoder_size = CustomSpinBox(256, 4096, 16)
        self.tiled_vae_encoder_size.setValue(1536)
        scroll_area_layout.addWidget(self.tiled_vae_encoder_size_label)
        scroll_area_layout.addWidget(self.tiled_vae_encoder_size)

        self.tiled_vae_decoder_size_label = CustomLabel("Decoder Tile Size")
        self.tiled_vae_decoder_size = CustomSpinBox(48, 512, 16)
        self.tiled_vae_decoder_size.setValue(96)
        scroll_area_layout.addWidget(self.tiled_vae_decoder_size_label)
        scroll_area_layout.addWidget(self.tiled_vae_decoder_size)

        self.tiled_vae_move_vae = QCheckBox("Move VAE to GPU (if possible)")
        self.tiled_vae_move_vae.setChecked(True)
        scroll_area_layout.addWidget(self.tiled_vae_move_vae)

        self.tiled_vae_fast_decoder = QCheckBox("Fast Decoder")
        self.tiled_vae_fast_decoder.setChecked(True)
        scroll_area_layout.addWidget(self.tiled_vae_fast_decoder)

        self.tiled_vae_fast_encoder = QCheckBox("Fast Encoder")
        self.tiled_vae_fast_encoder.setChecked(True)
        scroll_area_layout.addWidget(self.tiled_vae_fast_encoder)

        self.tiled_vae_fast_encoder_color = QCheckBox("Fast Encoder Color Fix")
        scroll_area_layout.addWidget(self.tiled_vae_fast_encoder_color)

        scroll_area_layout.addStretch()
        
        # set the scroll area content and add to the page layout
        scroll_area.setWidget(scroll_area_content)
        page_layout.addWidget(scroll_area)

        # add page to the stack
        self.setting_stacks.addWidget(page)

        
    def create_cd_tuner_stack(self):
        page = QWidget()
        page_layout = QVBoxLayout(page)

        # create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area_content = QWidget()
        scroll_area_layout = QVBoxLayout(scroll_area_content)

        # create setting UI
        self.cd_tuner_label = CustomLabel("CD Tuner")
        self.cd_tuner_label.setPointSize(20)
        scroll_area_layout.addWidget(self.cd_tuner_label)
        scroll_area_layout.addWidget(create_line())
        
        self.cd_tuner_detail1_label = CustomLabel("Detail (d1)")
        self.cd_tuner_detail1 = CustomSpinBox(-10, 10, 0.1)
        self.cd_tuner_detail1.setValue(0)
        scroll_area_layout.addWidget(self.cd_tuner_detail1_label)
        scroll_area_layout.addWidget(self.cd_tuner_detail1)
        
        self.cd_tuner_detail2_label = CustomLabel("Detail 2 (d2)")
        self.cd_tuner_detail2 = CustomSpinBox(-10, 10, 0.1)
        self.cd_tuner_detail2.setValue(0)
        scroll_area_layout.addWidget(self.cd_tuner_detail2_label)
        scroll_area_layout.addWidget(self.cd_tuner_detail2)

        self.cd_tuner_contrast_label = CustomLabel("Contrast (con1)")
        self.cd_tuner_contrast = CustomSpinBox(-20, 20, 0.1)
        self.cd_tuner_contrast.setValue(0)
        scroll_area_layout.addWidget(self.cd_tuner_contrast_label)
        scroll_area_layout.addWidget(self.cd_tuner_contrast)

        self.cd_tuner_contrast2_label = CustomLabel("Contrast 2 (con2)")
        self.cd_tuner_contrast2 = CustomSpinBox(-20, 20, 0.1)
        self.cd_tuner_contrast2.setValue(0)
        scroll_area_layout.addWidget(self.cd_tuner_contrast2_label)
        scroll_area_layout.addWidget(self.cd_tuner_contrast2)

        self.cd_tuner_brightness_label = CustomLabel("Brightness (br1)")
        self.cd_tuner_brightness = CustomSpinBox(-20, 20, 0.1)
        self.cd_tuner_brightness.setValue(0)
        scroll_area_layout.addWidget(self.cd_tuner_brightness_label)
        scroll_area_layout.addWidget(self.cd_tuner_brightness)

        self.cd_tuner_col_label = CustomLabel("Cyan-Red (col1)")
        self.cd_tuner_col = CustomSpinBox(-20, 20, 0.1)
        self.cd_tuner_col.setValue(0)
        scroll_area_layout.addWidget(self.cd_tuner_col_label)
        scroll_area_layout.addWidget(self.cd_tuner_col)

        self.cd_tuner_col2_label = CustomLabel("Magenta-Green (col2)")
        self.cd_tuner_col2 = CustomSpinBox(-20, 20, 0.1)
        self.cd_tuner_col2.setValue(0)
        scroll_area_layout.addWidget(self.cd_tuner_col2_label)
        scroll_area_layout.addWidget(self.cd_tuner_col2)

        self.cd_tuner_col3_label = CustomLabel("Yellow-Blue (col3)")
        self.cd_tuner_col3 = CustomSpinBox(-20, 20, 0.1)
        self.cd_tuner_col3.setValue(0)
        scroll_area_layout.addWidget(self.cd_tuner_col3_label)
        scroll_area_layout.addWidget(self.cd_tuner_col3)
        
        self.cd_tuner_hr_detail1_label = CustomLabel("hr-Detail (hd1)")
        self.cd_tuner_hr_detail1 = CustomSpinBox(-10, 10, 0.1)
        self.cd_tuner_hr_detail1.setValue(0)
        scroll_area_layout.addWidget(self.cd_tuner_hr_detail1_label)
        scroll_area_layout.addWidget(self.cd_tuner_hr_detail1)

        self.cd_tuner_hr_detail2_label = CustomLabel("hr-Detail 2 (hd2)")
        self.cd_tuner_hr_detail2 = CustomSpinBox(-10, 10, 0.1)
        self.cd_tuner_hr_detail2.setValue(0)
        scroll_area_layout.addWidget(self.cd_tuner_hr_detail2_label)
        scroll_area_layout.addWidget(self.cd_tuner_hr_detail2)
        
        self.cd_tuner_hr_scaling = QCheckBox("hr-scaling (hrs)")
        scroll_area_layout.addWidget(self.cd_tuner_hr_scaling)
        
        self.cd_tuner_step_label = CustomLabel("Stop Step")
        self.cd_tuner_step = CustomSpinBox(-1, 20, 1)
        self.cd_tuner_step.setValue(-1)
        scroll_area_layout.addWidget(self.cd_tuner_step_label)
        scroll_area_layout.addWidget(self.cd_tuner_step)

        self.cd_tuner_hr_step_label = CustomLabel("Hr-Stop Step")
        self.cd_tuner_hr_step = CustomSpinBox(-1, 20, 1)
        self.cd_tuner_hr_step.setValue(-1)
        scroll_area_layout.addWidget(self.cd_tuner_hr_step_label)
        scroll_area_layout.addWidget(self.cd_tuner_hr_step)
        
        scroll_area_layout.addStretch()

        # set the scroll area content and add to the page layout
        scroll_area.setWidget(scroll_area_content)
        page_layout.addWidget(scroll_area)

        # add page to the stack
        self.setting_stacks.addWidget(page)
    
    
    def create_negpip_stack(self):
        page = QWidget()
        page_layout = QVBoxLayout(page)

        # create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area_content = QWidget()
        scroll_area_layout = QVBoxLayout(scroll_area_content)

        # create setting UI
        self.negpip_label = CustomLabel("NegPip")
        self.negpip_label.setPointSize(20)
        scroll_area_layout.addWidget(self.negpip_label)
        scroll_area_layout.addWidget(create_line())
        
        # UIなし
        
        scroll_area_layout.addStretch()

        # set the scroll area content and add to the page layout
        scroll_area.setWidget(scroll_area_content)
        page_layout.addWidget(scroll_area)

        # add page to the stack
        self.setting_stacks.addWidget(page)
    
    
    def create_regional_prompter_stack(self):
        page = QWidget()
        page_layout = QVBoxLayout(page)

        # create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area_content = QWidget()
        scroll_area_layout = QVBoxLayout(scroll_area_content)

        # create setting UI
        self.regional_prompter_label = CustomLabel("Regional Prompter")
        self.regional_prompter_label.setPointSize(20)
        scroll_area_layout.addWidget(self.regional_prompter_label)
        scroll_area_layout.addWidget(create_line())

        self.regional_prompter_debug = QCheckBox("debug")
        scroll_area_layout.addWidget(self.regional_prompter_debug)

        self.regional_prompter_matrix = CustomLabel("Matrix")
        scroll_area_layout.addWidget(self.regional_prompter_matrix)

        self.regional_prompter_split_mode_label = CustomLabel("Split mode")
        self.regional_prompter_split_mode = QComboBox()
        self.regional_prompter_split_mode.addItems(["Horizontal", "Vertical", "Random"])
        scroll_area_layout.addWidget(self.regional_prompter_split_mode_label)
        scroll_area_layout.addWidget(self.regional_prompter_split_mode)

        self.regional_prompter_prompt_mode_label = CustomLabel("Prompt mode")
        self.regional_prompter_prompt_mode = QComboBox()
        self.regional_prompter_prompt_mode.addItems(["Prompt", "Prompt-Ex"])
        scroll_area_layout.addWidget(self.regional_prompter_prompt_mode_label)
        scroll_area_layout.addWidget(self.regional_prompter_prompt_mode)

        self.regional_prompter_devide_ratio_label = CustomLabel("Devide Ratio")
        self.regional_prompter_devide_ratio = QLineEdit()
        self.regional_prompter_devide_ratio.setText("1:1")
        scroll_area_layout.addWidget(self.regional_prompter_devide_ratio_label)
        scroll_area_layout.addWidget(self.regional_prompter_devide_ratio)

        self.regional_prompter_base_ratio_label = CustomLabel("Base Ratio")
        self.regional_prompter_base_ratio = QLineEdit()
        self.regional_prompter_base_ratio.setText("0.2")
        scroll_area_layout.addWidget(self.regional_prompter_base_ratio_label)
        scroll_area_layout.addWidget(self.regional_prompter_base_ratio)

        self.regional_prompter_use_base_prompt = QCheckBox("Use base prompt")
        self.regional_prompter_use_common_prompt = QCheckBox("Use common prompt")
        self.regional_prompter_use_common_negative_prompt = QCheckBox("Use common negative prompt")
        scroll_area_layout.addWidget(self.regional_prompter_use_base_prompt)
        scroll_area_layout.addWidget(self.regional_prompter_use_common_prompt)
        scroll_area_layout.addWidget(self.regional_prompter_use_common_negative_prompt)

        self.regional_prompter_generation_mode_label = CustomLabel("Generation mode")
        self.regional_prompter_generation_mode = QComboBox()
        self.regional_prompter_generation_mode.addItems(["Attention", "Latent"])
        scroll_area_layout.addWidget(self.regional_prompter_generation_mode_label)
        scroll_area_layout.addWidget(self.regional_prompter_generation_mode)

        self.regional_prompter_disable_convert = QCheckBox("disable convert 'And' to 'Break'")
        scroll_area_layout.addWidget(self.regional_prompter_disable_convert)

        self.regional_prompter_lora_in_negative_text_label = CustomLabel("LoRA in negative textencoder")
        self.regional_prompter_lora_in_negative_text = QLineEdit()
        self.regional_prompter_lora_in_negative_text.setText("0")
        scroll_area_layout.addWidget(self.regional_prompter_lora_in_negative_text_label)
        scroll_area_layout.addWidget(self.regional_prompter_lora_in_negative_text)

        self.regional_prompter_lora_in_negative_unet_label = CustomLabel("LoRA in negative U-net")
        self.regional_prompter_lora_in_negative_unet = QLineEdit()
        self.regional_prompter_lora_in_negative_unet.setText("0")
        scroll_area_layout.addWidget(self.regional_prompter_lora_in_negative_unet_label)
        scroll_area_layout.addWidget(self.regional_prompter_lora_in_negative_unet)

        self.regional_prompter_threshold_label = CustomLabel("threshold")
        self.regional_prompter_threshold = QLineEdit()
        self.regional_prompter_threshold.setText("0.4")
        scroll_area_layout.addWidget(self.regional_prompter_threshold_label)
        scroll_area_layout.addWidget(self.regional_prompter_threshold)

        self.regional_prompter_lora_stop_label = CustomLabel("LoRA stop step")
        self.regional_prompter_lora_stop = QLineEdit()
        self.regional_prompter_lora_stop.setText("0")
        scroll_area_layout.addWidget(self.regional_prompter_lora_stop_label)
        scroll_area_layout.addWidget(self.regional_prompter_lora_stop)

        self.regional_prompter_lora_hr_stop_label = CustomLabel("LoRA Hires stop step")
        self.regional_prompter_lora_hr_stop = QLineEdit()
        self.regional_prompter_lora_hr_stop.setText("0")
        scroll_area_layout.addWidget(self.regional_prompter_lora_hr_stop_label)
        scroll_area_layout.addWidget(self.regional_prompter_lora_hr_stop)
        
        scroll_area_layout.addStretch()

        # set the scroll area content and add to the page layout
        scroll_area.setWidget(scroll_area_content)
        page_layout.addWidget(scroll_area)

        # add page to the stack
        self.setting_stacks.addWidget(page)


    """
    =============================================
    connect
    =============================================
    """
    def connect_interface(self):
        self.connect_toggle_button()
    
    def connect_toggle_button(self):
        self.adetailer_toggle_button.clicked.connect(lambda: self.toggle_stack(1))
        self.tiled_diffusion_toggle_button.clicked.connect(lambda: self.toggle_stack(2))
        self.tiled_vae_toggle_button.clicked.connect(lambda: self.toggle_stack(3))
        self.cd_tuner_toggle_button.clicked.connect(lambda: self.toggle_stack(4))
        self.negpip_toggle_button.clicked.connect(lambda: self.toggle_stack(5))
        self.regional_prompter_toggle_button.clicked.connect(lambda: self.toggle_stack(6))
    
    def toggle_stack(self, index):
        self.setting_stacks.setCurrentIndex(index)
    
    """
    =============================================
    create payload
        mainから呼び出す
    =============================================
    """
    def create_script_payload(self):
        args = {}

        # 各payloadをargsにupdate
        self.add_adetailer_payload(args)
        self.add_tiled_diffusion_payload(args)
        self.add_tiled_vae_payload(args)
        self.add_cd_tuner_payload(args)
        self.add_negpip_payload(args)
        self.add_regional_prompter_payload(args)
        
        return args
    
    
    def add_adetailer_payload(self, args):
        if "adetailer" in self.scripts_list and self.adetailer_enable.isChecked():
            arg = {
                "adetailer": {
                    "args": [
                        {
                            "ad_model": self.adetailer_model.currentText(),
                            "ad_prompt": self.adetailer_prompt.toPlainText(),
                            "ad_negative_prompt": self.adetailer_negative_prompt.toPlainText()
                        },
                        {
                            "ad_model": self.adetailer_model_2nd.currentText(),
                            "ad_prompt": self.adetailer_prompt_2nd.toPlainText(),
                            "ad_negative_prompt": self.adetailer_negative_prompt_2nd.toPlainText()
                        }
                    ]
                }
            }
            args.update(arg)
    
    def add_tiled_diffusion_payload(self, args):
        if "tiled diffusion" in self.scripts_list and self.tiled_diffusion_enable.isChecked():
            arg = {
                "tiled diffusion": {
                    "args": [
                        self.tiled_diffusion_enable.isChecked(),
                        self.tiled_diffusion_method.currentText(),
                        self.tiled_diffusion_overwrite.isChecked(),
                        self.tiled_diffusion_keepsize.isChecked(),
                        self.tiled_diffusion_width.value(),
                        self.tiled_diffusion_height.value(),
                        self.tiled_diffusion_latent_width.value(),
                        self.tiled_diffusion_latent_height.value(),
                        self.tiled_diffusion_latent_overlap.value(),
                        self.tiled_diffusion_latent_batch.value(),
                        self.tiled_diffusion_upscaler.currentText(),
                        self.tiled_diffusion_scale.value(),
                        self.tiled_diffusion_noise_enable.isChecked(),
                        self.tiled_diffusion_noise_step.value(),
                        self.tiled_diffusion_noise_retouch.value(),
                        self.tiled_diffusion_noise_renoise_strength.value(),
                        self.tiled_diffusion_noise_renoise_size.value()
                    ]
                }
            }
            args.update(arg)
    
    def add_tiled_vae_payload(self, args):
        if "tiled vae" in self.scripts_list and self.tiled_vae_enable.isChecked():
            arg = {
                "tiled vae": {
                    "args": [
                        self.tiled_vae_enable.isChecked(),
                        self.tiled_vae_encoder_size.value(),
                        self.tiled_vae_decoder_size.value(),
                        self.tiled_vae_move_vae.isChecked(),
                        self.tiled_vae_fast_decoder.isChecked(),
                        self.tiled_vae_fast_encoder.isChecked(),
                        self.tiled_vae_fast_encoder_color.isChecked()
                    ]
                }
            }
            args.update(arg)
    
    def add_cd_tuner_payload(self, args):
        if self.cd_tuner_hr_scaling.isChecked(): hr_scaling = 1
        else: hr_scaling = 0
        
        if "cd tuner" in self.scripts_list and self.cd_tuner_enable.isChecked():
            arg = {
                "cd tuner": {
                    "args": [
                        self.cd_tuner_detail1.value(),
                        self.cd_tuner_detail2.value(),
                        self.cd_tuner_contrast.value(),
                        self.cd_tuner_contrast2.value(),
                        self.cd_tuner_brightness.value(),
                        self.cd_tuner_col.value(),
                        self.cd_tuner_col2.value(),
                        self.cd_tuner_col3.value(),
                        self.cd_tuner_hr_detail1.value(),
                        self.cd_tuner_hr_detail2.value(),
                        hr_scaling,
                        self.cd_tuner_step.value(),
                        self.cd_tuner_hr_step.value()
                    ]
                }
            }
            args.update(arg)
    
    def add_negpip_payload(self, args):
        if "negpip" in self.scripts_list and self.negpip_enable.isChecked():
            arg = {
                "negpip": {
                    "args": [
                        self.negpip_enable.isChecked()
                    ]
                }
            }
            args.update(arg)

    def add_regional_prompter_payload(self, args):
        if "regional prompter" in self.scripts_list and self.regional_prompter_enable.isChecked():
            arg = {
                "regional prompter": {
                    "args": [
                        self.regional_prompter_enable.isChecked(),
                        self.regional_prompter_debug.isChecked(),
                        "Matrix",
                        self.regional_prompter_split_mode.currentText(),
                        "Mask",
                        self.regional_prompter_prompt_mode.currentText(),
                        self.regional_prompter_devide_ratio.text(),
                        self.regional_prompter_base_ratio.text(),
                        self.regional_prompter_use_base_prompt.isChecked(),
                        self.regional_prompter_use_common_prompt.isChecked(),
                        self.regional_prompter_use_common_negative_prompt.isChecked(),
                        self.regional_prompter_generation_mode.currentText(),
                        self.regional_prompter_disable_convert.isChecked(),
                        self.regional_prompter_lora_in_negative_text.text(),
                        self.regional_prompter_lora_in_negative_unet.text(),
                        self.regional_prompter_threshold.text(),
                        "",
                        self.regional_prompter_lora_stop.text(),
                        self.regional_prompter_lora_hr_stop.text()
                    ]
                }
            }
            args.update(arg)
    
    
    