import os
import json
import urllib.request
import urllib.parse

class Api:
    def __init__(self):
        # default_config.jsonからurlを取得する
        plugin_dir = os.path.dirname(__file__)
        default_json_path = os.path.join(plugin_dir, "default_config.json")
        with open(default_json_path, "r") as f:
            self.base_url = json.load(f)["url"]
    
    def request(self, endpoint, data=None):
        url = f"{self.base_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}
        if data:
            data = json.dumps(data).encode("utf-8")
            req = urllib.request.Request(url, data, headers)
        else:
            req = urllib.request.Request(url)
        return req
    
    def extract_values(self, data, key):
        if isinstance(data, dict):
            return data[key]
        elif isinstance(data, list):
            result_list = []
            for item in data:
                if isinstance(item, dict):
                    result_list.append(item[key])
                else:
                    result_list.append(item)
            return result_list
        else:
            return None
    
    def get(self, endpoint, key=None):
        req = self.request(endpoint)
        with urllib.request.urlopen(req) as res:
            body = json.loads(res.read().decode())
        if key:
            return self.extract_values(body, key)
        else:
            return body
    
    def post(self, endpoint, data):
        req = self.request(endpoint, data)
        with urllib.request.urlopen(req) as res:
            body = json.loads(res.read().decode())
        return body
    
    """
    =============================================
    webui
    =============================================
    """
    # checkpoint一覧
    def get_checkpoint_list(self):
        checkpoint_list = self.get("sdapi/v1/sd-models")
        # model_nameとtitleの対応辞書を作成
        self.checkpoint_title_dict = dict((checkpoint["model_name"], checkpoint["title"]) for checkpoint in checkpoint_list)
        # 表示用のmodel_nameリストを返す
        return list(self.checkpoint_title_dict.keys())
    
    # checkpointのmodel_name -> titleへの変換
    def convert_checkpoint_to_title(self, model_name):
        if self.checkpoint_title_dict:
            return self.checkpoint_title_dict[model_name]
        else:
            return model_name
    
    # checkpointのmodel_ttile -> nameへの変換
    def convert_checkpoint_to_name(self, model_title):
        if self.checkpoint_title_dict:
            for name, title in self.checkpoint_title_dict.items():
                if title == model_title:
                    return name
            return model_title
        else:
            return model_title
    
    # 今設定されているcheckpoint
    def get_checkpoint_selected(self):
        selected_checkpoint_title = self.get("sdapi/v1/options", "sd_model_checkpoint")
        return self.convert_checkpoint_to_name(selected_checkpoint_title)
    
    # vae一覧
    def get_vae_list(self):
        return self.get("sdapi/v1/sd-vae", "model_name")
    
    # 今設定されているvae
    def get_vae_selected(self):
        return self.get("sdapi/v1/options", "sd_vae")
    
    # sampler一覧
    def get_sampler_list(self):
        return self.get("sdapi/v1/samplers", "name")
    
    # upscaler一覧
    def get_upscaler_list(self):
        return self.get("sdapi/v1/upscalers", "name")
    
    # latent upscale mode一覧
    def get_latent_upscaler_list(self):
        return self.get("sdapi/v1/latent-upscale-modes", "name")
    
    # textual_inversionフォルダ
    def get_textual_inversion_dir(self):
        return self.get("sdapi/v1/cmd-flags", "embeddings_dir")
    
    # hypernetworksフォルダ
    def get_hypernetworks_dir(self):
        return self.get("sdapi/v1/cmd-flags", "hypernetwork_dir")
    
    # checkpointsフォルダ
    def get_checkpoints_dir(self):
        data_dir = self.get("sdapi/v1/cmd-flags", "data_dir")
        checkpoints_dir = os.path.join(data_dir, "models", "Stable-diffusion")
        return checkpoints_dir
    
    # loraフォルダ
    def get_lora_dir(self):
        return self.get("sdapi/v1/cmd-flags", "lora_dir")
    
    """
    =============================================
    controlnet
    =============================================
    """
    # preprocessor一覧
    def get_controlnet_module_list(self):
        return self.get("controlnet/module_list", "module_list")
    
    # model一覧
    def get_controlnet_model_list(self):
        return self.get("controlnet/model_list", "model_list")
    
    # max model num
    def get_controlnet_max_unit(self):
        return self.get("controlnet/settings", "control_net_max_models_num")
    
    """
    =============================================
    Scripts
    =============================================
    """
    # フォルダから特定の拡張子ファイルリストを取得
    def file_lists(self, path, extensions):
        files = []
        for root, dirs, filenames in os.walk(path, followlinks=True):
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    files.append(filename)
        return files

api = Api()