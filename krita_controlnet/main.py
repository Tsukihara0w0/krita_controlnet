from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QWidget, QTabWidget
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QComboBox, QCheckBox
from PyQt5.QtWidgets import QPushButton, QRadioButton, QToolButton, QButtonGroup
from PyQt5.QtGui import QRegExpValidator, QTextCursor
from PyQt5.QtCore import QRegExp

from krita import *
from .ui.Label import CustomLabel
from .ui.PlainTextEdit import CustomPlainTextEdit
from .ui.CollapsibleWidget import CollapsibleWidget
from .ui.Spinbox import CustomSpinBox
from .utils import *
from .hanahuda import *
from .sd_scripts import *
from .api import *


class ControlnetDocker(DockWidget):
    def __init__(self):
        super().__init__()
        
        # default_config.jsonを取得
        self.default = open_default_json()
        
        self.parameters = ""
        self.latest_seed = -1
        
        self.create_interface()
        self.connect_interface()
        self.setting_interface()

        self.setWindowTitle("ControlNet")
    
    """
    =============================================
    create interface
    =============================================
    """
    def create_interface(self):
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        self.create_main_panel()
        self.create_prompt_interface()
        self.create_config_interface()
        self.create_i2i_interface()
        self.create_controlnet_interface()
        self.create_tabs()
        
        self.setWidget(self.widget)

    def create_main_panel(self):
        # output layer name
        self.output_layer_label = CustomLabel("output layer name")
        self.output_layer = QLineEdit()
        self.overwrite_checkbox = QCheckBox("同名output layerに上書き")
        self.output_layer_layout = QVBoxLayout()
        self.output_layer_layout.addWidget(self.output_layer_label)
        self.output_layer_layout.addWidget(self.output_layer)
        self.output_layer_layout.addWidget(self.overwrite_checkbox)
        # generate & save button
        self.generate_button = QPushButton("Generate")
        button_height = self.generate_button.sizeHint().height() * 1.5
        self.generate_button.setFixedHeight(button_height)
        self.save_button  = QPushButton("Save")
        self.save_button.setFixedSize(100, button_height)
        self.save_button.setToolTip("生成した最新のメタデータを画像に埋め込んで保存します")
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.save_button)
        self.auto_save_checkbox = QCheckBox("webuiで設定しているディレクトリに自動保存")
        self.auto_resize_checkbox = QCheckBox("キャンバスを自動リサイズ")
        self.auto_resize_checkbox.setToolTip("出力画像サイズにキャンバスサイズを合わせます")
        self.last_result = QCheckBox("最終結果のみ出力")
        self.last_result.setToolTip("preprocessorの結果など複数枚出力される場合\n最終的な結果のみ出力します")
        self.generate_layout = QVBoxLayout()
        self.generate_layout.addLayout(button_layout)
        self.generate_layout.addWidget(self.auto_save_checkbox)
        self.generate_layout.addWidget(self.auto_resize_checkbox)
        self.generate_layout.addWidget(self.last_result)
        self.generate_layout.addStretch()
        
        self.main_panel_layout = QVBoxLayout()
        self.main_panel_layout.addLayout(self.output_layer_layout)
        self.main_panel_layout.addWidget(create_line())
        self.main_panel_layout.addLayout(self.generate_layout)
        self.main_panel = QWidget()
        self.main_panel.setLayout(self.main_panel_layout)
        
        self.layout.addWidget(self.main_panel)
    
    def create_prompt_interface(self):
        # prompt
        self.prompt_label = CustomLabel("Prompt")
        self.prompt = CustomPlainTextEdit()
        self.prompt.setFixedHeight(100)
        self.prompt_layout = QVBoxLayout()
        self.prompt_layout.addWidget(self.prompt_label)
        self.prompt_layout.addWidget(self.prompt)
        # negative prompt
        self.negative_prompt_label = CustomLabel("Negative Prompt")
        self.negative_prompt = CustomPlainTextEdit()
        self.negative_prompt.setFixedHeight(100)
        self.negative_prompt_layout = QVBoxLayout()
        self.negative_prompt_layout.addWidget(self.negative_prompt_label)
        self.negative_prompt_layout.addWidget(self.negative_prompt)
        # hanafuda
        self.hanahuda_button = QToolButton()
        self.hanahuda_button.setText("🎴")
        # script
        self.scripts_button = QToolButton()
        self.scripts_button.setText("Scripts")
        self.tool_buttons_layout = QHBoxLayout()
        self.tool_buttons_layout.addWidget(self.hanahuda_button)
        self.tool_buttons_layout.addWidget(self.scripts_button)
        self.tool_buttons_layout.addStretch()
        
        self.prompt_tab_layout = QVBoxLayout()
        self.prompt_tab_layout.addLayout(self.prompt_layout)
        self.prompt_tab_layout.addWidget(create_line())
        self.prompt_tab_layout.addLayout(self.negative_prompt_layout)
        self.prompt_tab_layout.addWidget(create_line())
        self.prompt_tab_layout.addLayout(self.tool_buttons_layout)
        self.prompt_tab_layout.addStretch(1)
        
        self.prompt_widget = QWidget()
        self.prompt_widget.setLayout(self.prompt_tab_layout)
    
    def create_config_interface(self):
        # checkpoint
        self.checkpoint_label = CustomLabel("Checkpoint")
        self.checkpoint = QComboBox()
        self.checkpoint.addItems(api.get_checkpoint_list())
        self.checkpoint_layout = QHBoxLayout()
        self.checkpoint_layout.addWidget(self.checkpoint_label)
        self.checkpoint_layout.addWidget(self.checkpoint)
        # vae
        self.vae_label = CustomLabel("VAE")
        self.vae = QComboBox()
        self.vae.addItems(api.get_vae_list())
        self.vae_layout = QHBoxLayout()
        self.vae_layout.addWidget(self.vae_label)
        self.vae_layout.addWidget(self.vae)
        # clip skip
        self.clip_label = CustomLabel("Clip Skip")
        self.clip = CustomSpinBox(1, 12, 1)
        self.clip_layout = QHBoxLayout()
        self.clip_layout.addWidget(self.clip_label)
        self.clip_layout.addWidget(self.clip)
        # sampler
        self.sampler_label = CustomLabel("Smapling method")
        self.sampler = QComboBox()
        self.sampler.addItems(api.get_sampler_list())
        self.sampler_layout = QHBoxLayout()
        self.sampler_layout.addWidget(self.sampler_label)
        self.sampler_layout.addWidget(self.sampler)
        # steps
        self.steps_label = CustomLabel("Sampling steps")
        self.steps = CustomSpinBox(1, 150 ,1)
        self.steps_layout = QHBoxLayout()
        self.steps_layout.addWidget(self.steps_label)
        self.steps_layout.addWidget(self.steps)
        # width
        self.width_label = CustomLabel("Width")
        self.width = CustomSpinBox(64, 2048, 8)
        self.width_layout = QHBoxLayout()
        self.width_layout.addWidget(self.width_label)
        self.width_layout.addWidget(self.width)
        # height
        self.height_label = CustomLabel("Height")
        self.height = CustomSpinBox(64, 2048, 8)
        self.height_layout = QHBoxLayout()
        self.height_layout.addWidget(self.height_label)
        self.height_layout.addWidget(self.height)
        # hires
        # upscaler
        self.hires_upscaler_label = CustomLabel("Upscaler")
        self.hires_upscaler = QComboBox()
        self.hires_upscaler_list = api.get_upscaler_list() # upscaler list
        self.hires_upscaler_latent_list = api.get_latent_upscaler_list() # latent list
        self.hires_upscaler.addItems(self.hires_upscaler_latent_list + self.hires_upscaler_list)
        self.hires_upscaler_layout = QHBoxLayout()
        self.hires_upscaler_layout.addWidget(self.hires_upscaler_label)
        self.hires_upscaler_layout.addWidget(self.hires_upscaler)
        # hires steps
        self.hires_steps_label = CustomLabel("Hires steps")
        self.hires_steps = CustomSpinBox(0, 150, 1)
        self.hires_steps_layout = QHBoxLayout()
        self.hires_steps_layout.addWidget(self.hires_steps_label)
        self.hires_steps_layout.addWidget(self.hires_steps)
        # denoising strength
        self.hires_denoise_label = CustomLabel("Denoising strength")
        self.hires_denoise = CustomSpinBox(0, 1, 0.01)
        self.hires_denoise_layout = QHBoxLayout()
        self.hires_denoise_layout.addWidget(self.hires_denoise_label)
        self.hires_denoise_layout.addWidget(self.hires_denoise)
        # upscalerby
        self.hires_upscaleby_label = CustomLabel("Upscale by")
        self.hires_upscaleby = CustomSpinBox(1, 4, 0.05)
        self.hires_upscaleby_layout = QHBoxLayout()
        self.hires_upscaleby_layout.addWidget(self.hires_upscaleby_label)
        self.hires_upscaleby_layout.addWidget(self.hires_upscaleby)
        # resize from ~~ to ~~
        self.hires_resize_result = CustomLabel("", False)
        # hires collapsible widget
        self.hires_layout = QVBoxLayout()
        self.hires_layout.addLayout(self.hires_upscaler_layout)
        self.hires_layout.addWidget(create_line())
        self.hires_layout.addLayout(self.hires_steps_layout)
        self.hires_layout.addWidget(create_line())
        self.hires_layout.addLayout(self.hires_denoise_layout)
        self.hires_layout.addWidget(create_line())
        self.hires_layout.addLayout(self.hires_upscaleby_layout)
        self.hires_layout.addWidget(self.hires_resize_result)
        self.hires_layout.addStretch(1)
        self.hires_widget = QWidget()
        self.hires_widget.setLayout(self.hires_layout)
        self.hires = CollapsibleWidget("Hires.fix", self.hires_widget)
        # cfg scale
        self.cfg_label = CustomLabel("CFG Scale")
        self.cfg = CustomSpinBox(1, 30 ,0.5)
        self.cfg.setDecimals(1)
        self.cfg_layout = QHBoxLayout()
        self.cfg_layout.addWidget(self.cfg_label)
        self.cfg_layout.addWidget(self.cfg)
        # seed
        self.seed_label = CustomLabel("Seed")
        self.seed_random_button = QToolButton()
        self.seed_random_button.setText("🎲")
        self.seed_random_button.setToolTip("set -1 seed")
        self.seed_reuse_button = QToolButton()
        self.seed_reuse_button.setText("♻")
        self.seed_reuse_button.setToolTip("reuse the latest seed")
        self.seed = QLineEdit()
        self.seed.setValidator(QRegExpValidator(QRegExp("[-]?[0-9]*"))) # 正規表現により数字のみ入力可能にする
        self.seed_layout = QHBoxLayout()
        self.seed_layout.addWidget(self.seed_label)
        self.seed_layout.addWidget(self.seed_random_button)
        self.seed_layout.addWidget(self.seed_reuse_button)
        self.seed_layout.addWidget(self.seed)

        self.config_layout = QVBoxLayout()
        self.config_layout.addLayout(self.checkpoint_layout)
        self.config_layout.addWidget(create_line())
        self.config_layout.addLayout(self.vae_layout)
        self.config_layout.addWidget(create_line())
        self.config_layout.addLayout(self.clip_layout)
        self.config_layout.addWidget(create_line())
        self.config_layout.addLayout(self.sampler_layout)
        self.config_layout.addWidget(create_line())
        self.config_layout.addLayout(self.steps_layout)
        self.config_layout.addWidget(create_line())
        self.config_layout.addWidget(self.hires)
        self.config_layout.addWidget(create_line())
        self.config_layout.addLayout(self.width_layout)
        self.config_layout.addLayout(self.height_layout)
        self.config_layout.addWidget(create_line())
        self.config_layout.addLayout(self.cfg_layout)
        self.config_layout.addWidget(create_line())
        self.config_layout.addLayout(self.seed_layout)
        self.config_layout.addStretch(1)

        self.config_widget = QWidget()
        self.config_widget.setLayout(self.config_layout)
    
    def create_i2i_interface(self):
        # i2i enable
        self.i2i_enable = QCheckBox("i2i enable")
        # i2i layer name
        self.i2i_layer_label = CustomLabel("i2i Layer Name")
        self.i2i_layer = QLineEdit()
        self.i2i_layer_layout = QHBoxLayout()
        self.i2i_layer_layout.addWidget(self.i2i_layer_label)
        self.i2i_layer_layout.addWidget(self.i2i_layer)
        # resize mode
        self.i2i_resize_mode_label = CustomLabel("Resize Mode")
        self.i2i_resize_button0 = QRadioButton("Just Resize")
        self.i2i_resize_button0.setChecked(True)
        self.i2i_resize_button1 = QRadioButton("Crop and resize")
        self.i2i_resize_button2 = QRadioButton("Resized and fill")
        self.i2i_resize_button3 = QRadioButton("Just resize(latent upscale)")
        self.i2i_resize_button_group = QButtonGroup()
        self.i2i_resize_button_group.addButton(self.i2i_resize_button0)
        self.i2i_resize_button_group.addButton(self.i2i_resize_button1)
        self.i2i_resize_button_group.addButton(self.i2i_resize_button2)
        self.i2i_resize_button_group.addButton(self.i2i_resize_button3)
        self.i2i_resize_mode_layout = QGridLayout()
        self.i2i_resize_mode_layout.addWidget(self.i2i_resize_mode_label, 0, 0)
        self.i2i_resize_mode_layout.addWidget(self.i2i_resize_button0, 0, 1)
        self.i2i_resize_mode_layout.addWidget(self.i2i_resize_button1, 0, 2)
        self.i2i_resize_mode_layout.addWidget(self.i2i_resize_button2, 1, 1)
        self.i2i_resize_mode_layout.addWidget(self.i2i_resize_button3, 1, 2)
        # resize to
        self.i2i_resizeto_label = CustomLabel("Resize to")
        self.i2i_width_label = CustomLabel("Width")
        self.i2i_width = CustomSpinBox(64, 2048, 8)
        self.i2i_width_layout = QHBoxLayout()
        self.i2i_width_layout.addWidget(self.i2i_width_label)
        self.i2i_width_layout.addWidget(self.i2i_width)
        self.i2i_height_label = CustomLabel("Height")
        self.i2i_height = CustomSpinBox(64, 2048, 8)
        self.i2i_height_layout = QHBoxLayout()
        self.i2i_height_layout.addWidget(self.i2i_height_label)
        self.i2i_height_layout.addWidget(self.i2i_height)
        self.i2i_resizeto_layout = QVBoxLayout()
        self.i2i_resizeto_layout.addWidget(self.i2i_resizeto_label)
        self.i2i_resizeto_layout.addLayout(self.i2i_width_layout)
        self.i2i_resizeto_layout.addLayout(self.i2i_height_layout)
        # denoising strength
        self.i2i_denoise_label = CustomLabel("Denoising strength")
        self.i2i_denoise = CustomSpinBox(0 ,1, 0.01)
        self.i2i_denoise_layout = QHBoxLayout()
        self.i2i_denoise_layout.addWidget(self.i2i_denoise_label)
        self.i2i_denoise_layout.addWidget(self.i2i_denoise)
        # inpaint widget
        # mask layer name
        self.inpaint_mask_label = CustomLabel("Mask Layer Name")
        self.inpaint_mask = QLineEdit()
        self.inpaint_mask_layout = QHBoxLayout()
        self.inpaint_mask_layout.addWidget(self.inpaint_mask_label)
        self.inpaint_mask_layout.addWidget(self.inpaint_mask)
        # mask blur
        self.inpaint_mask_blur_label = CustomLabel("Mask blur")
        self.inpaint_mask_blur = CustomSpinBox(0, 64, 1)
        self.inpaint_mask_blur_layout = QHBoxLayout()
        self.inpaint_mask_blur_layout.addWidget(self.inpaint_mask_blur_label)
        self.inpaint_mask_blur_layout.addWidget(self.inpaint_mask_blur)
        # mask mode
        self.inpaint_mask_mode_label = CustomLabel("Mask mode")
        self.inpaint_mask_mode_button0 = QRadioButton("Inpaint masked")
        self.inpaint_mask_mode_button1 = QRadioButton("Inpaint not masked")
        self.inpaint_mask_mode_group = QButtonGroup()
        self.inpaint_mask_mode_group.addButton(self.inpaint_mask_mode_button0)
        self.inpaint_mask_mode_group.addButton(self.inpaint_mask_mode_button1)
        self.inpaint_mask_mode_layout = QHBoxLayout()
        self.inpaint_mask_mode_layout.addWidget(self.inpaint_mask_mode_label)
        self.inpaint_mask_mode_layout.addWidget(self.inpaint_mask_mode_button0)
        self.inpaint_mask_mode_layout.addWidget(self.inpaint_mask_mode_button1)
        # masked content
        self.inpaint_masked_content_label = CustomLabel("Masked content")
        self.inpaint_masked_content_button0 = QRadioButton("fill")
        self.inpaint_masked_content_button1 = QRadioButton("original")
        self.inpaint_masked_content_button2 = QRadioButton("latent noise")
        self.inpaint_masked_content_button3 = QRadioButton("latent nothing")
        self.inpaint_masked_content_button_group = QButtonGroup()
        self.inpaint_masked_content_button_group.addButton(self.inpaint_masked_content_button0)
        self.inpaint_masked_content_button_group.addButton(self.inpaint_masked_content_button1)
        self.inpaint_masked_content_button_group.addButton(self.inpaint_masked_content_button2)
        self.inpaint_masked_content_button_group.addButton(self.inpaint_masked_content_button3)
        self.inpaint_masked_content_layout = QGridLayout()
        self.inpaint_masked_content_layout.addWidget(self.inpaint_masked_content_label, 0, 0)
        self.inpaint_masked_content_layout.addWidget(self.inpaint_masked_content_button0, 0, 1)
        self.inpaint_masked_content_layout.addWidget(self.inpaint_masked_content_button1, 0, 2)
        self.inpaint_masked_content_layout.addWidget(self.inpaint_masked_content_button2, 1, 1)
        self.inpaint_masked_content_layout.addWidget(self.inpaint_masked_content_button3, 1, 2)
        # inpaint area
        self.inpaint_area_label = CustomLabel("Inapint area")
        self.inpaint_area_button0 = QRadioButton("Whole picture")
        self.inpaint_area_button1 = QRadioButton("Only masked")
        self.inpaint_area_button_group = QButtonGroup()
        self.inpaint_area_button_group.addButton(self.inpaint_area_button0)
        self.inpaint_area_button_group.addButton(self.inpaint_area_button1)
        self.inpaint_area_layout = QHBoxLayout()
        self.inpaint_area_layout.addWidget(self.inpaint_area_label)
        self.inpaint_area_layout.addWidget(self.inpaint_area_button0)
        self.inpaint_area_layout.addWidget(self.inpaint_area_button1)
        # only masked padding, pixels
        self.inpaint_padding_label = CustomLabel("Only masked padding, pixels")
        self.inpaint_padding = CustomSpinBox(0, 256, 4)
        self.inpaint_padding_layout = QHBoxLayout()
        self.inpaint_padding_layout.addWidget(self.inpaint_padding_label)
        self.inpaint_padding_layout.addWidget(self.inpaint_padding)
        # inpaint collapsiblewidget
        self.inpaint_widget = QWidget()
        self.inpaint_layout = QVBoxLayout()
        self.inpaint_layout.addLayout(self.inpaint_mask_layout)
        self.inpaint_layout.addWidget(create_line())
        self.inpaint_layout.addLayout(self.inpaint_mask_blur_layout)
        self.inpaint_layout.addWidget(create_line())
        self.inpaint_layout.addLayout(self.inpaint_mask_mode_layout)
        self.inpaint_layout.addWidget(create_line())
        self.inpaint_layout.addLayout(self.inpaint_masked_content_layout)
        self.inpaint_layout.addWidget(create_line())
        self.inpaint_layout.addLayout(self.inpaint_area_layout)
        self.inpaint_layout.addWidget(create_line())
        self.inpaint_layout.addLayout(self.inpaint_padding_layout)
        self.inpaint_layout.addStretch(1)
        self.inpaint_widget.setLayout(self.inpaint_layout)
        self.inpaint = CollapsibleWidget("inpaint", self.inpaint_widget)

        self.i2i_layout = QVBoxLayout()
        self.i2i_layout.addWidget(self.i2i_enable)
        self.i2i_layout.addLayout(self.i2i_layer_layout)
        self.i2i_layout.addWidget(create_line())
        self.i2i_layout.addLayout(self.i2i_resize_mode_layout)
        self.i2i_layout.addWidget(create_line())
        self.i2i_layout.addLayout(self.i2i_resizeto_layout)
        self.i2i_layout.addWidget(create_line())
        self.i2i_layout.addLayout(self.i2i_denoise_layout)
        self.i2i_layout.addWidget(create_line())
        self.i2i_layout.addWidget(self.inpaint)
        self.i2i_layout.addStretch(1)

        self.i2i_widget = QWidget()
        self.i2i_widget.setLayout(self.i2i_layout)
    
    def create_controlnet_interface(self):
        self.max_unit = api.get_controlnet_max_unit()
        self.units = []
        
        self.controlnet_model_list = api.get_controlnet_model_list()
        # self.controlnet_module_list = api.get_controlnet_module_list()
        # apiで取得できるやつがwebui表示と違う
        # webuiに合わせるために直打ち
        self.controlnet_module_list = [
            "none", "invert", "canny", 
            "depth_leres", "depth_leres++", "depth_midas", "depth_zoe", 
            "inpaint_global_harmonious", "inpaint_only", "inpaint_only+lama", 
            "lineart_anime", "lineart_anime_denoise", "lineart_coarse", "lineart_realistic", "lineart_standard", 
            "mediapipe_face", "mlsd", "normal_bae", "normal_midas", 
            "openpose", "openpose_face", "openpose_faceonly", "openpose_full", "openpose_hand", 
            "reference_adain", "reference_adain+attn", "reference_only", 
            "scribble_hed", "scribble_pidinet", "scribble_xdog", 
            "seg_ofade20k", "seg_ofcoco", "seg_ufade20k", "shuffle", 
            "softedge_hed", "softedge_hedsafe", "softedge_pidinet", "softedge_pidisafe", 
            "t2ia_color_grid", "t2ia_sketch_pidi", "t2ia_style_clipvision", 
            "threshold", "tile_colorfix", "tile_colorfix+sharp", "tile_resample"
        ]

        self.controlnet_widget = QScrollArea()
        self.controlnet_widget.setWidgetResizable(True)
        self.controlnet_widget.setFixedHeight(600)
        self.controlnet_scroll_area_content = QWidget()
        self.controlnet_scroll_area_layout = QVBoxLayout(self.controlnet_scroll_area_content)
        for unit_index in range(0, self.max_unit):
            unit = {} # unit毎に情報を格納する辞書
            # layer
            unit["layer_label"] = CustomLabel("Layer Name")
            unit["layer"] = QLineEdit()
            unit["layer_layout"] = QHBoxLayout()
            unit["layer_layout"].addWidget(unit["layer_label"])
            unit["layer_layout"].addWidget(unit["layer"])
            # mask layer
            unit["mask_enable"] = QCheckBox()
            unit["mask_label"] = CustomLabel("Mask Layer Name")
            unit["mask"] = QLineEdit()
            unit["mask_layout"] = QHBoxLayout()
            unit["mask_layout"].addWidget(unit["mask_enable"])
            unit["mask_layout"].addWidget(unit["mask_label"])
            unit["mask_layout"].addWidget(unit["mask"])
            # preprocessor
            unit["module_label"] = CustomLabel("Preprocessor")
            unit["module_button"] = QToolButton()
            unit["module_button"].setText("💥")
            unit["module_button"].setToolTip("Run Preprocessor")
            unit["module"] = QComboBox()
            unit["module"].addItems(self.controlnet_module_list)
            unit["module_layout"] = QHBoxLayout()
            unit["module_layout"].addWidget(unit["module_label"])
            unit["module_layout"].addWidget(unit["module_button"])
            unit["module_layout"].addWidget(unit["module"])
            # threshold
            unit["threshold_a_label"] = CustomLabel("threshold_a")
            unit["threshold_a"] = CustomSpinBox(0, 10, 0.1)
            unit["threshold_a_layout"] = QVBoxLayout()
            unit["threshold_a_layout"].addWidget(unit["threshold_a_label"])
            unit["threshold_a_layout"].addWidget(unit["threshold_a"])
            unit["threshold_b_label"] = CustomLabel("threshold_b")
            unit["threshold_b"] = CustomSpinBox(0, 10, 0.1)
            unit["threshold_b_layout"] = QVBoxLayout()
            unit["threshold_b_layout"].addWidget(unit["threshold_b_label"])
            unit["threshold_b_layout"].addWidget(unit["threshold_b"])
            unit["threshold_layout"] = QHBoxLayout()
            unit["threshold_layout"].addLayout(unit["threshold_a_layout"])
            unit["threshold_layout"].addLayout(unit["threshold_b_layout"])
            # preprocessor resolution
            unit["module_res_label"] = CustomLabel("Preproceessor Resolution")
            unit["module_res"] = CustomSpinBox(64, 2048, 1)
            unit["module_res_layout"] = QHBoxLayout()
            unit["module_res_layout"].addWidget(unit["module_res_label"])
            unit["module_res_layout"].addWidget(unit["module_res"])
            # model
            unit["model_label"] = CustomLabel("Model")
            unit["model"] = QComboBox()
            unit["model"].addItems(self.controlnet_model_list)
            unit["model_layout"] = QHBoxLayout()
            unit["model_layout"].addWidget(unit["model_label"])
            unit["model_layout"].addWidget(unit["model"])
            # weight
            unit["weight_label"] = CustomLabel("Weight")
            unit["weight"] = CustomSpinBox(0, 2, 0.05, "vertical")
            unit["weight_layout"] = QVBoxLayout()
            unit["weight_layout"].addWidget(unit["weight_label"])
            unit["weight_layout"].addWidget(unit["weight"])
            # start step
            unit["start_label"] = CustomLabel("Starting Step")
            unit["start"] = CustomSpinBox(0, 1, 0.01, "vertical")
            unit["start_layout"] = QVBoxLayout()
            unit["start_layout"].addWidget(unit["start_label"])
            unit["start_layout"].addWidget(unit["start"])
            # end step
            unit["end_label"] = CustomLabel("Ending Step")
            unit["end"] = CustomSpinBox(0, 1, 0.01, "vertical")
            unit["end_layout"] = QVBoxLayout()
            unit["end_layout"].addWidget(unit["end_label"])
            unit["end_layout"].addWidget(unit["end"])
            # weight, start, endは横に並べる
            unit["cnconf_layout"] = QHBoxLayout()
            unit["cnconf_layout"].addLayout(unit["weight_layout"])
            unit["cnconf_layout"].addLayout(unit["start_layout"])
            unit["cnconf_layout"].addLayout(unit["end_layout"])
            # control mode
            unit["mode_label"] = CustomLabel("Control Mode")
            unit["mode_button0"] = QRadioButton("Balanced")
            unit["mode_button1"] = QRadioButton("My prompt is more important")
            unit["mode_button2"] = QRadioButton("ControlNet is more important")
            unit["mode_button_group"] = QButtonGroup()
            unit["mode_button_group"].addButton(unit["mode_button0"])
            unit["mode_button_group"].addButton(unit["mode_button1"])
            unit["mode_button_group"].addButton(unit["mode_button2"])
            unit["mode_layout"] = QVBoxLayout()
            unit["mode_layout"].addWidget(unit["mode_label"])
            unit["mode_layout"].addWidget(unit["mode_button0"])
            unit["mode_layout"].addWidget(unit["mode_button1"])
            unit["mode_layout"].addWidget(unit["mode_button2"])
            # resize mode
            unit["resize_mode_label"] = CustomLabel("Resize Mode")
            unit["resize_button0"] = QRadioButton("Just Resize")
            unit["resize_button1"] = QRadioButton("Crop and Resize")
            unit["resize_button2"] = QRadioButton("Resize and Fill")
            unit["resize_button_group"] = QButtonGroup()
            unit["resize_button_group"].addButton(unit["resize_button0"])
            unit["resize_button_group"].addButton(unit["resize_button1"])
            unit["resize_button_group"].addButton(unit["resize_button2"])
            unit["resize_mode_layout"] = QGridLayout()
            unit["resize_mode_layout"].addWidget(unit["resize_mode_label"], 0, 0)
            unit["resize_mode_layout"].addWidget(unit["resize_button0"], 1, 0)
            unit["resize_mode_layout"].addWidget(unit["resize_button1"], 1, 1)
            unit["resize_mode_layout"].addWidget(unit["resize_button2"], 1, 2)
            # option
            unit["option_lowvram"] = QCheckBox("Low VRAM")
            unit["option_perfect"] = QCheckBox("Pixel Perfect")
            unit["option_layout"] = QHBoxLayout()
            unit["option_layout"].addWidget(unit["option_lowvram"])
            unit["option_layout"].addWidget(unit["option_perfect"])
            
            unit["content_layout"] = QVBoxLayout()
            unit["content_layout"].addLayout(unit["layer_layout"])
            unit["content_layout"].addWidget(create_line())
            unit["content_layout"].addLayout(unit["mask_layout"])
            unit["content_layout"].addWidget(create_line())
            unit["content_layout"].addLayout(unit["module_layout"])
            unit["content_layout"].addLayout(unit["module_res_layout"])
            unit["content_layout"].addLayout(unit["threshold_layout"])
            unit["content_layout"].addWidget(create_line())
            unit["content_layout"].addLayout(unit["model_layout"])
            unit["content_layout"].addWidget(create_line())
            unit["content_layout"].addLayout(unit["cnconf_layout"])
            unit["content_layout"].addWidget(create_line())
            unit["content_layout"].addLayout(unit["mode_layout"])
            unit["content_layout"].addWidget(create_line())
            unit["content_layout"].addLayout(unit["resize_mode_layout"])
            unit["content_layout"].addWidget(create_line())
            unit["content_layout"].addLayout(unit["option_layout"])
            unit["content_layout"].addWidget(create_line())
            
            unit["content_widget"] = QWidget()
            unit["content_widget"].setLayout(unit["content_layout"])
            
            unit["widget"] = CollapsibleWidget(f"Unit {unit_index}", unit["content_widget"])
            self.controlnet_scroll_area_layout.addWidget(unit["widget"])
            self.units.append(unit) # unitの情報をリストに追加
        self.controlnet_scroll_area_layout.addStretch(1)
        
        self.controlnet_widget.setWidget(self.controlnet_scroll_area_content)

    def create_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(self.prompt_widget, "prompt")
        self.tabs.addTab(self.config_widget, "config")
        self.tabs.addTab(self.i2i_widget, "i2i")
        self.tabs.addTab(self.controlnet_widget, "controlnet")
        
        self.layout.addWidget(self.tabs)
        self.layout.addStretch(1)
    
    """
    =============================================
    connect:
        clicked: generate, hanahuda, seed_random, seed_reuse
        changed: checkpoint, vae, width, height, hires_upscaleby
    =============================================
    """
    def connect_interface(self):
        # generate_button
        self.generate_button.clicked.connect(self.generate_button_clicked)
        
        # save_button
        self.save_button.clicked.connect(self.save_button_clicked)
        
        # hanahuda_button
        self.hanahuda_window = HanhudaWindow(self)
        self.hanahuda_button.clicked.connect(lambda: self.hanahuda_window.show())
        
        # script_button
        self.scripts_window = ScriptsWindow()
        self.scripts_button.clicked.connect(lambda: self.scripts_window.show())
        
        # seed
        self.seed_random_button.clicked.connect(self.seed_random_clicked)
        self.seed_reuse_button.clicked.connect(self.seed_reuse_clicked)
        
        # checkpoint
        self.checkpoint.currentTextChanged.connect(self.checkpoint_changed)
        
        # vae
        self.vae.currentTextChanged.connect(self.vae_changed)
        
        # widht, height, hires_upscaleby
        self.width.valueChanged(self.calc_hires_result_size)
        self.height.valueChanged(self.calc_hires_result_size)
        self.hires_upscaleby.valueChanged(self.calc_hires_result_size)
        
        # controlnet module button
        for unit_index, unit in enumerate(self.units):
            unit["module_button"].clicked.connect(partial(self.controlnet_module_button_clicked, unit_index))
            unit["module"].currentTextChanged.connect(partial(self.controlnet_module_changed, unit_index))
            unit["option_perfect"].stateChanged.connect(partial(self.controlnet_perfect_changed, unit_index))
    
    def generate_button_clicked(self):
        krita = Krita.instance()
        doc = krita.activeDocument()
        if doc is None:
            return print("document is not open!!")
        
        self.payload = {} # init payload
        self.create_payload()
        self.add_payload()
        
        if self.i2i_enable.isChecked():
            # send to i2i api
            response = api.post("sdapi/v1/img2img", self.payload)
        else:
            # send to t2i api
            response = api.post("sdapi/v1/txt2img", self.payload)
        
        # add image to layer
        output_layer = self.output_layer.text()
        overwrite = self.overwrite_checkbox.isChecked()
        auto_resize = self.auto_resize_checkbox.isChecked()
        last_result = self.last_result.isChecked()
        add_image_to_layer(response, output_layer, overwrite, auto_resize, last_result)
        
        # png info
        img_payload = {"image": "data:image/png;base64," + response["images"][0]}
        response2 = api.post("sdapi/v1/png-info", img_payload)
        self.parameters = response2["info"]
        if not self.i2i_enable.isChecked() and not self.hires.isChecked(): self.parameters = delete_denoising_strength(self.parameters)
        self.latest_seed = extract_seed(self.parameters)
    
    def save_button_clicked(self):
        krita = Krita.instance()
        doc = krita.activeDocument()
        if doc is None:
            return print("document is not open!!")
        
        exportDocument_with_parameters(self.parameters)
            
    """
    =============================================
    payload setting
    =============================================
    """
    def create_payload(self):
        payload = {
            "prompt": self.prompt.toPlainText(),
            "negative_prompt": self.negative_prompt.toPlainText(),
            "seed": int(self.seed.text()),
            "sampler_name": self.sampler.currentText(),
            "steps": self.steps.value(),
            "width": self.width.value(),
            "height": self.height.value(),
            "cfg_scale": self.cfg.value(),
            "save_images": self.auto_save_checkbox.isChecked(),
            "override_settings": {
                "CLIP_stop_at_last_layers": self.clip.value()
            },
            "alwayson_scripts": {}
        }
        self.payload.update(payload)
    
    def add_payload(self):
        self.add_i2i_payload()
        self.add_t2i_payload()
        if "controlnet" in self.scripts_window.scripts_list: self.add_controlnet_payload()
        self.add_script_payload()
    
    def add_i2i_payload(self):
        # i2i setting
        if not self.i2i_enable.isChecked(): return
        i2i_image = get_image_from_layer(self.i2i_layer.text(), isMask=False)
        i2i_payload = {
            "init_images": [i2i_image],
            "resize_mode": self.determine_i2i_resize_mode(),
            "denoising_strength": self.i2i_denoise.value(),
            "width": self.i2i_width.value(),
            "height": self.i2i_height.value()
        }
        self.payload.update(i2i_payload)

        # inpaint setting
        if not self.inpaint.isChecked(): return
        inpaint_mask = get_image_from_layer(self.inpaint_mask.text(), isMask=True)
        inpaint_payload = {
            "mask": inpaint_mask,
            "mask_blur": self.inpaint_mask_blur.value(),
            "inpainting_mask_invert": self.determine_inpaint_mask_mode(),
            "inpainting_fill": self.determine_inpaint_masked_content(),
            "inpaint_full_res": self.determine_inpaint_area(),
            "inpaint_full_res_padding": self.inpaint_padding.value()
        }
        self.payload.update(inpaint_payload)
    
    def add_t2i_payload(self):
        # hires setting
        if not self.hires.isChecked(): return
        hires_payload = {
            "enable_hr": self.hires.isChecked(),
            "denoising_strength": self.hires_denoise.value(),
            "hr_scale": self.hires_upscaleby.value(),
            "hr_second_pass_steps": self.hires_steps.value(),
            "hr_upscaler": self.hires_upscaler.currentText(),
            "hr_sampler_name": self.sampler.currentText(),
        }
        self.payload.update(hires_payload)
    
    def add_controlnet_payload(self):
        payload_list = []
        for unit in self.units:
            payload = {}
            if unit["widget"].isChecked():
                payload = {
                    "input_image": get_image_from_layer(unit["layer"].text()),
                    "module": unit["module"].currentText(),
                    "model": unit["model"].currentText(),
                    "weight": unit["weight"].value(),
                    "resize_mode": self.determine_controlnet_resize_mode(unit),
                    "lowvram": unit["option_lowvram"].isChecked(),
                    "processor_res": unit["module_res"].value(),
                    "guidance_start": unit["start"].value(),
                    "guidance_end": unit["end"].value(),
                    "control_mode": self.determine_controlnet_mode(unit),
                    "pixel_perfect": unit["option_perfect"].isChecked(),
                    "threshold_a": unit["threshold_a"].value(),
                    "threshold_b": unit["threshold_b"].value()
                }
                if unit["mask_enable"].isChecked():
                    payload.update({"mask": get_image_from_layer(unit["mask"].text(), isMask=True)})
            else:
                payload = {"enabled": False}
            
            payload_list.append(payload)
        
        cn_args = {
            "alwayson_scripts": {
                "ControlNet":{
                    "args": payload_list
                }
            }
        }
        self.payload.update(cn_args)
    
    def add_script_payload(self):
        scripts_args = self.scripts_window.create_script_payload()
        self.payload["alwayson_scripts"].update(scripts_args)
    
    """
    =============================================
    connected func
    =============================================
    """
    def checkpoint_changed(self, selected_checkpoint_name):
        selected_checkpoint_title = api.convert_checkpoint_to_title(selected_checkpoint_name)
        option_payload = {"sd_model_checkpoint": selected_checkpoint_title}
        api.post("sdapi/v1/options", option_payload)
    
    def vae_changed(self, selected_vae_name):
        option_payload = {"sd_vae": selected_vae_name}
        api.post("sdapi/v1/options", option_payload)
    
    def seed_random_clicked(self):
        self.seed.setText("-1")
    
    def seed_reuse_clicked(self):
        self.seed.setText(str(self.latest_seed))
    
    def calc_hires_result_size(self):
        scale = self.hires_upscaleby.value()
        width = self.width.value()
        height = self.height.value()
        new_width = int(width * scale)
        new_height = int(height * scale)
        text = f"from: {width} x {height} to: {new_width} x {new_height}"
        self.hires_resize_result.setText(text)
    
    def controlnet_module_button_clicked(self, unit_index):
        krita = Krita.instance()
        doc = krita.activeDocument()
        if doc is None:
            return print("document is not open!!")
        
        unit = self.units[unit_index]
        module = unit["module"].currentText()
        input_image = get_image_from_layer(unit["layer"].text())
        module_res = unit["module_res"].value()
        threshold_a = unit["threshold_a"].value()
        threshold_b = unit["threshold_b"].value()
        payload = {
            "controlnet_module": module,
            "controlnet_input_images": [input_image],
            "controlnet_processor_res": module_res,
            "controlnet_threshold_a": threshold_a,
            "controlnet_threshold_b": threshold_b
        }
        
        response = api.post("controlnet/detect", payload)
        add_image_to_layer(response, module, True, False, True)
    
    def controlnet_module_changed(self, unit_index):
        unit = self.units[unit_index]
        module = unit["module"].currentText()
        res = unit["module_res"]
        res_label = unit["module_res_label"]
        a = unit["threshold_a"]
        b = unit["threshold_b"]
        a_label = unit["threshold_a_label"]
        b_label = unit["threshold_b_label"]
        perfect = unit["option_perfect"]
        
        # res, a, bなし
        if module in ["none", "inpaint_global_harmonious", "inpaint_only", "inpaint_only+lama"]:
            self.toggle_visiblity(hide=[res, a, b, res_label, a_label, b_label])

        # resあり a, bなし
        elif module in ["invert", "depth_midas", "depth_zoe", "lineart_anime", "lineart_anime_denoise", 
                      "lineart_coarse", "lineart_realistic", "lineart_standard", "normal_bae", 
                      "openpose", "openpose_face", "openpose_faceonly", "openpose_full", "openpose_hand", 
                      "scribble_hed", "scribble_pidinet", "seg_ofade20k", "seg_ofcoco", "seg_ufade20k", 
                      "shuffle", "softedge_hed", "softedge_hedsafe", "softedge_pidinet", "softedge_pidisafe", 
                      "t2ia_color_grid", "t2ia_sketch_pidi", "t2ia_style_clipvision"
                      ]:
            self.toggle_visiblity(show=[], hide=[a, b, a_label, b_label])
            if perfect.isChecked(): pass
            else: self.toggle_visiblity(show=[res, res_label])
        
        elif module == "canny":
            a.setConf(1, 255, 0.1, 100)
            b.setConf(1, 255, 0.1, 200)
            a_label.setText("Canny Low Threshold")
            b_label.setText("Canny High Threshold")
            self.toggle_visiblity(show=[a, b, a_label, b_label])
            if perfect.isChecked():
                self.toggle_visiblity(hide=[res, res_label])
            else:
                self.toggle_visiblity(show=[res, res_label])
        
        elif module in ["depth_leres", "depth_leres++"]:
            a.setConf(0, 100, 0.1, 0)
            b.setConf(0, 100, 0.1, 0)
            a_label.setText("Remove Near %")
            b_label.setText("Remove Background %")
            self.toggle_visiblity(show=[a, b, a_label, b_label])
            if perfect.isChecked():
                self.toggle_visiblity(hide=[res, res_label])
            else:
                self.toggle_visiblity(show=[res, res_label])
        
        elif module == "mediapipe_face":
            a.setConf(1, 10, 1, 1)
            b.setConf(0.01, 1, 0.01, 0.5)
            a_label.setText("Max Faces")
            b_label.setText("Min Face Confidence")
            self.toggle_visiblity(show=[a, b, a_label, b_label])
            if perfect.isChecked():
                self.toggle_visiblity(hide=[res, res_label])
            else:
                self.toggle_visiblity(show=[res, res_label])
        
        elif module == "mlsd":
            a.setConf(0.01, 2, 0.01, 0.1)
            b.setConf(0.01, 20, 0.01, 0.1)
            a_label.setText("MLSD Value Threshold")
            b_label.setText("MLSD Distance Threshold")
            self.toggle_visiblity(show=[a, b, a_label, b_label])
            if perfect.isChecked():
                self.toggle_visiblity(hide=[res, res_label])
            else:
                self.toggle_visiblity(show=[res, res_label])
        
        elif module == "normal_midas":
            a.setConf(0, 1, 0.01, 0.4)
            a_label.setText("Normal Background Threshold")
            self.toggle_visiblity(show=[a, a_label], hide=[b, b_label])
            if perfect.isChecked():
                self.toggle_visiblity(hide=[res, res_label])
            else:
                self.toggle_visiblity(show=[res, res_label])
        
        elif module in ["reference_adain", "reference_adain+attn", "reference_only"]:
            a.setConf(0, 1, 0.01, 0.5)
            a_label.setText('Style Fidelity (only for "Balanced" mode)')
            self.toggle_visiblity(show=[a, a_label], hide=[b, b_label])
            if perfect.isChecked():
                self.toggle_visiblity(hide=[res, res_label])
            else:
                self.toggle_visiblity(show=[res, res_label])
        
        elif module == "scribble_xdog":
            a.setConf(1, 64, 1, 32)
            a_label.setText("XDoG Threshold")
            self.toggle_visiblity(show=[a, a_label], hide=[b, b_label])
            if perfect.isChecked():
                self.toggle_visiblity(hide=[res, res_label])
            else:
                self.toggle_visiblity(show=[res, res_label])
        
        elif module == "threshold":
            a.setConf(0, 255, 1, 127)
            a_label.setText("Binarization Threshold")
            self.toggle_visiblity(show=[a, a_label], hide=[b, b_label])
            if perfect.isChecked():
                self.toggle_visiblity(hide=[res, res_label])
            else:
                self.toggle_visiblity(show=[res, res_label])
        
        elif module == "tile_colorfix":
            a.setConf(3, 32, 1, 8)
            a_label.setText("Variation")
            self.toggle_visiblity(show=[a, a_label], hide=[res, b, res_label, b_label])
        
        elif module == "tile_colorfix+sharp":
            a.setConf(3, 32, 1, 8)
            b.setConf(0, 2, 0.01, 1)
            a_label.setText("Variation")
            b_label.setText("Sharpness")
            self.toggle_visiblity(show=[a, b, a_label, b_label], hide=[res, res_label])
        
        elif module == "tile_resample":
            a.setConf(1, 8, 0.01, 1)
            a_label.setText("Down Sampling Rate")
            self.toggle_visiblity(show=[a, a_label], hide=[res, b, res_label, b_label])
        
        else:
            print("module not in list")
    
    def controlnet_perfect_changed(self, unit_index, state):
        unit = self.units[unit_index]
        module = unit["module"].currentText()
        res = unit["module_res"]
        res_label = unit["module_res_label"]
        if module not in ["none", "tile_colorfix", "tile_colorfix+sharp", "tile_resample"]:
            if state == 0: # disabale
                self.toggle_visiblity(show=[res, res_label])
            if state == 2: # enable
                self.toggle_visiblity(hide=[res, res_label])
    
    def toggle_visiblity(self, show=[], hide=[]):
        for item in show:
            item.show()
        for item in hide:
            item.hide()
    
    """
    =============================================
    determine button value
    =============================================
    """
    def determine_i2i_resize_mode(self):
        if self.i2i_resize_button0.isChecked(): return 0
        if self.i2i_resize_button1.isChecked(): return 1
        if self.i2i_resize_button2.isChecked(): return 2
        if self.i2i_resize_button3.isChecked(): return 3
        else: return 0
    
    def determine_inpaint_mask_mode(self):
        if self.inpaint_mask_mode_button0.isChecked(): return 0
        if self.inpaint_mask_mode_button1.isChecked(): return 1
        else: return 0
    
    def determine_inpaint_masked_content(self):
        if self.inpaint_masked_content_button0.isChecked(): return 0
        if self.inpaint_masked_content_button1.isChecked(): return 1
        if self.inpaint_masked_content_button2.isChecked(): return 2
        if self.inpaint_masked_content_button3.isChecked(): return 3
        else: return 0
    
    def determine_inpaint_area(self):
        if self.inpaint_area_button0.isChecked(): return True
        if self.inpaint_area_button1.isChecked(): return False
        else: return False
    
    def determine_controlnet_mode(self, unit):
        if unit["mode_button0"].isChecked(): return 0
        if unit["mode_button1"].isChecked(): return 1
        if unit["mode_button2"].isChecked(): return 2
        else: return 0
    
    def determine_controlnet_resize_mode(self, unit):
        if unit["resize_button0"].isChecked(): return 0
        if unit["resize_button1"].isChecked(): return 1
        if unit["resize_button2"].isChecked(): return 2
        else: return 0
    
    """
    =============================================
    setting:
        default value set to interface
    =============================================
    """
    def setting_interface(self):
        self.auto_resize_checkbox.setChecked(True)
        self.overwrite_checkbox.setChecked(True)
        self.last_result.setChecked(True)
        
        # prompt
        self.prompt.setPlainText(self.default["prompt"])
        prompt_cursor = self.prompt.textCursor()
        prompt_cursor.movePosition(QTextCursor.End)
        self.prompt.setTextCursor(prompt_cursor)
        
        self.negative_prompt.setPlainText(self.default["negative prompt"])
        neagtive_prompt_cursor = self.negative_prompt.textCursor()
        neagtive_prompt_cursor.movePosition(QTextCursor.End)
        self.negative_prompt.setTextCursor(neagtive_prompt_cursor)
        
        self.output_layer.setText("output")
        
        # checkpoint
        selected_checkpoint_name = api.get_checkpoint_selected()
        self.checkpoint.setCurrentText(selected_checkpoint_name)

        # vae
        selected_vae = api.get_vae_selected()
        self.vae.setCurrentText(selected_vae)
        
        # config
        self.clip.setValue(self.default["clip skip"])
        self.sampler.setCurrentText(self.default["sampler"])
        self.steps.setValue(self.default["sampling steps"])
        self.width.setValue(self.default["width"])
        self.height.setValue(self.default["height"])
        self.cfg.setValue(self.default["cfg scale"])
        self.seed.setText(str(self.default["seed"]))
        self.hires_upscaler.setCurrentText(self.default["hires upscaler"])
        self.hires_steps.setValue(self.default["hires steps"])
        self.hires_denoise.setValue(self.default["hires denoising strength"])
        self.hires_upscaleby.setValue(self.default["hires upscale by"])

        # i2i
        self.i2i_width.setValue(self.default["i2i width"])
        self.i2i_height.setValue(self.default["i2i height"])
        self.i2i_denoise.setValue(self.default["i2i denoising strength"])
        self.inpaint_mask_blur.setValue(self.default["inpaint mask blur"])
        self.inpaint_padding.setValue(self.default["inpaint only masked padding, pixels"])
        self.i2i_resize_button0.setChecked(True) # -> just resize
        self.inpaint_mask_mode_button0.setChecked(True) # -> inpaint masked
        self.inpaint_masked_content_button1.setChecked(True) # -> original
        self.inpaint_area_button0.setChecked(True) # -> whole picture
        
        # controlnet
        for unit in self.units:
            unit["module"].setCurrentText(self.default["controlnet preprocessor"])
            unit["model"].setCurrentText(self.default["controlnet model"])
            unit["weight"].setValue(self.default["controlnet weight"])
            unit["start"].setValue(self.default["controlnet starting step"])
            unit["end"].setValue(self.default["controlnet ending step"])
            unit["module_res"].setValue(self.default["controlnet preprocessor resolution"])
            unit["mode_button0"].setChecked(True) # -> balanced
            unit["resize_button1"].setChecked(True) # -> crop and resize

    def canvasChanged(self, canvas):
        pass

Krita.instance().addDockWidgetFactory(DockWidgetFactory("mydocker", DockWidgetFactoryBase.DockRight, ControlnetDocker))