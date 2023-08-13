# krita_controlnet
 
# 概要
kritaでstable diffusion webuiを使用するためのプラグインです。
レイヤー画像をcontrolnetで使用できます。


[sample.mp4](https://github.com/Tsukihara0w0/krita_controlnet/assets/138929225/41708677-5520-43d9-9974-ba0724772fbc)



# 動作環境
- stable diffusion webui v1.5.1
- krita v5.1.5

# 使い方
1. **kritaプラグインを配置**
   [releases](https://github.com/Tsukihara0w0/krita_controlnet/releases)からzipをダウンロードしkritaリソースフォルダのpykritaディレクトリに解凍してください。
   ```
   pykrita/
   ├── krita_controlnet/
   │   ├── __init__.py
   │   ├── main.py
   |   └── ...
   └── krita_controlnet.desktop
   ```
2. **webuiをapiで起動**
   webui-user.batに`COMMANDLINE_ARGS=--api`を追記してください。

3. **kritaプラグインを有効化**
   kritaにて[設定] -> [Kritaの設定を変更] -> [Pythonプラグインマネージャー] からkrita_controlnetを有効化し、kritaを再起動します。

4. 画面右側にドッキングパネルが追加されます。<br>
   お好きな場所に移動させてください。

# 設定
基本的には通常のwebuiと同じ設定項目なので直感的に使えるかと思います。<br>
起動時のデフォルト設定は`krita_controlnet/default_config.json`で変更できます。

- **promptタブ**<br>
  promptとnegative promptです。<br>
  extranetworkとscriptウィンドウも開けます。(対応scriptは後述)

- **configタブ**<br>
  t2i, i2iの主な共通設定です。<br>
  hiresボタンをクリックするとhires.fixの設定が開きます。<br>
  ボタン横のチェックボックスで有効無効の切り替えを行います。

- **i2iタブ**<br>
  i2i設定タブです。<br>
  i2iを使用する場合は、i2i_enableにチェックをいれてください。<br>
  また、参照元となるレイヤー名を記入してください。<br>
  inpaintボタンをクリックするとinpaintの設定が開きます。<br>
  ボタン横のチェックボックスで有効無効の切り替えを行います。

- **controlnetタブ**<br>
  controlnetの設定です。<br>
  unitボタンをクリックすると該当unitの設定が開きます。<br>
  複数unitを使用したい場合はwebuiのほうであらかじめ設定しておいてください。<br>
  また、Run Preprocessorボタンの使用にはcontrolnetのapi.pyを一部書き換える必要があります(後述)。

### 対応script
簡易的にですが下記scriptに対応しています。
- adetailer
- tiled diffusion
- tiled vae
- cd tuner
- negpip
- regional prompter

promptタブのScriptsボタンをクリックすると各設定を行えます。

# 注意点
### Run Preprocessorの使用について
controlnet側のバグ?により通常のままだとRun Preprocessor (💥ボタン)は使用できません。<br>
画像の生成には問題ありませんが、プリプロセッサのみを使用したい場合は下記のようにcontrolnetのapi.pyを書き換える必要があります。<br>
書き換えは自己責任でお願いします。<br>
`stable-diffusion-webui/extensions/sd-webui-controlnet/scripts/api.py`16行目あたり<br>
**before**
```
def encode_to_base64(image):
    if type(image) is str:
        return image
    elif type(image) is Image.Image:
        return api.encode_pil_to_base64(image)
    elif type(image) is np.ndarray:
        return encode_np_to_base64(image)
    else:
        return ""
```
**after**
```
def encode_to_base64(image):
    if type(image) is str:
        return image
    elif type(image) is Image.Image:
        return api.encode_pil_to_base64(image)
    else:
        try:
            image_array = np.asarray(image)
            return encode_np_to_base64(image_array)
        except:
            return ""
```

### 透明ピクセルの取り扱いについて
レイヤーの透明ピクセルの取り扱いは2通りあります。
- マスク用レイヤー<br>
  inpaintやcontrolnetで使用するmaskに設定しているレイヤーの透明ピクセルは全て黒へ、それ以外は白へ変換されてapiに送信されます。<br>
  そのため、色や透明度については特に気にする必要はないです。何かしらで塗った場所がマスクとなります。

- その他のレイヤー
  i2iやcontrolnetのソースとなるレイヤーでの透明ピクセルは全て白へ変換されます。<br>
  デフォルトでは下地(kritaにおける背景レイヤー)は白色だと思うので、見たままの画像が送られるイメージです。<br>
  そのため、controlnetで線画を自分で描いて使用する場合（scribbleやlineartなど）はプリプロセッサにinvertを使用することをお勧めします。
