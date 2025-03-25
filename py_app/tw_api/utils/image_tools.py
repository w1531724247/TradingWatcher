# 
from io import BytesIO
from PIL import Image
import base64

def image_to_base64(image: Image):
    # 输入为PIL读取的图片，输出为base64格式
    byte_data = BytesIO()# 创建一个字节流管道
    image.save(byte_data, format="JPEG")# 将图片数据存入字节流管道
    byte_data = byte_data.getvalue()# 从字节流管道中获取二进制
    base64_str = base64.b64encode(byte_data).decode("ascii")# 二进制转base64
    return base64_str

def base64_str_from_image_file(img_path: str):
    image = Image.open(fp=img_path)
    base64_str = image_to_base64(image)
    return base64_str

def base64_to_image(base64_str: str):
    # 输入为base64格式字符串，输出为PIL格式图片
    byte_data = base64.b64decode(base64_str) # base64转二进制
    image = Image.open(BytesIO(byte_data)) # 将二进制转为PIL格式图片
    return image
