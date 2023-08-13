from PyQt5.QtWidgets import QFrame, QFileDialog
from PyQt5.QtCore import QBuffer, QIODevice
from PyQt5.QtGui import QImage, QColor
from krita import Krita, InfoObject

import base64
import io
import os
import json
import re
import struct
import zlib


# open default json
def open_default_json():
    plugin_dir = os.path.dirname(__file__)
    default_json_path = os.path.join(plugin_dir, "default_config.json")
    with open(default_json_path, "r") as f:
        return json.load(f)

# add a border
def create_line():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    return line

# base64 -> bytes
def decode_base64_to_bytes(data):
    base64_data = data.split(",", 1)[0]
    bytes_date = base64.b64decode(base64_data)
    byte_io = io.BytesIO(bytes_date)
    return byte_io.getvalue()

# bytes -> base64
def encode_bytes_to_base64(data):
    byte_io = io.BytesIO(data)
    base64_data = base64.b64encode(byte_io.getvalue()).decode("utf-8")
    return base64_data

# search layer
def search_layer(node, layer_name):
    for child in node.childNodes():
        if child.name() == layer_name:
            return child
        result = search_layer(child, layer_name)
        if result is not None:
            return result
    return None

# add image to krita layer
def add_image_to_layer(image_data, layer_name, overwrite_layer=False, auto_resize_canvas=False, last_result=False):
    krita = Krita.instance()
    doc = krita.activeDocument()

    root_node = doc.rootNode()
    layers = root_node.childNodes()
    
    
    for index, image_base64 in enumerate(image_data["images"]):
        current_layer_name = layer_name if index == 0 else "{}{}".format(layer_name, index)
        
        output_layer = search_layer(root_node, current_layer_name)
        if output_layer is None or overwrite_layer is False:
            output_layer = doc.createNode(current_layer_name, "paintLayer")
            root_node.addChildNode(output_layer, layers[-1])
        
        image_bytes = decode_base64_to_bytes(image_base64)
        if image_bytes == b"":
            print("empty image")
            continue

        image = QImage.fromData(image_bytes)
        image = image.convertToFormat(QImage.Format_RGB32)

        width = image.width()
        height = image.height()

        converted_image_bytes = image.constBits().asstring(image.byteCount())

        output_layer.setPixelData(converted_image_bytes, 0, 0, width, height)
        
        if last_result:
            # 最終結果のみ出力ON -> ["images"][0]で終了
            break
    
    doc.refreshProjection()

    if auto_resize_canvas:
        doc.resizeImage(0, 0, width, height)

# get image from layer
def get_image_from_layer(layer_name, isMask=False):
    krita = Krita.instance()
    doc = krita.activeDocument()

    root_node = doc.rootNode()
    
    target_layer = search_layer(root_node, layer_name)

    if target_layer is None:
        print(f"Not found layer named {layer_name}")
        return ""
    
    pixel_data = target_layer.projectionPixelData(0, 0, doc.width(), doc.height()).data()
    
    image = QImage(pixel_data, doc.width(), doc.height(), QImage.Format_ARGB32)
    
    for y in range(image.height()):
        for x in range(image.width()):
            color = QColor.fromRgba(image.pixel(x, y))

            if isMask: # mask mode: aplha->black, other->white
                if color.alpha() == 0:
                    image.setPixelColor(x, y, QColor(0, 0, 0, 255))
                else:
                    image.setPixelColor(x, y, QColor(255, 255, 255, 255))
            
            else: # aplha->white
                if color.alpha() == 0:
                    image.setPixelColor(x, y, QColor(255, 255, 255, 255))

    buffer = QBuffer()
    buffer.open(QIODevice.WriteOnly)
    image.save(buffer, "PNG")
    img_data = buffer.data().data()

    img_base64 = encode_bytes_to_base64(img_data)
    return img_base64

# extract seed from png info
def extract_seed(info):
    items = re.split(", |\n", info)

    result = {}
    for item in items:
        parts = item.split(": ")
        key = parts[0].strip()
        value = parts[1].strip() if len(parts) > 1 else None

        result[key] = value
    
    return result["Seed"]

# delete denoising strength from png info
def delete_denoising_strength(info):
    start_index = info.find("Denoising strength:")
    end_index = info.find(",", start_index)

    if start_index == -1 or end_index == -1:
        return info
    
    return info[:start_index] + info[end_index + 1:]


# 画像にparametersを挿入
def add_parameters(file_path, value):
    with open(file_path, 'rb') as f:
        data = f.read()

    # tEXtチャンクのデータを作成
    key = "parameters"
    text_chunk = key.encode('utf-8') + b'\x00' + value.encode('utf-8')
    text_chunk_data = b'tEXt' + text_chunk
    crc = zlib.crc32(text_chunk_data)
    text_chunk_data = struct.pack('>I', len(text_chunk)) + text_chunk_data + struct.pack('>I', crc)

    # IDATチャンクの位置を見つける
    idat_position = data.find(b'IDAT') - 4

    # IDATチャンクの前に新しいチャンクを挿入
    new_data = data[:idat_position] + text_chunk_data + data[idat_position:]

    with open(file_path, 'wb') as f:
        f.write(new_data)

# 画像をエクスポートしてparametersを挿入
def exportDocument_with_parameters(value):  
    doc = Krita.instance().activeDocument()

    # ドキュメントを開いている場合
    if doc is not None:
        file_path, _ = QFileDialog.getSaveFileName(filter="PNG Files (*.png)")
        
        if file_path:
            # エクスポート
            info_object = InfoObject()
            info_object.setProperty("imageType", "png") # PNG形式を指定
            doc.exportImage(file_path, info_object)
        
            # parameters挿入
            add_parameters(file_path, value)
    
    # ドキュメントを開いていない場合、何もしない
    else:
        return None

