import base64
import os
import random
import uuid
import shutil
from io import BytesIO

from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from model_api.model.core.detect import run, smart_inference_mode
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont

class DefectDescription:
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color

defects_translate = {
    0: DefectDescription('прилегающий дефект', 'red'),
    1: DefectDescription('дефект целостности', 'blue'),
    2: DefectDescription('дефект геометрии', 'green'),
    3: DefectDescription('дефект постобработки', 'yellow'),
    4: DefectDescription('дефект невыполнения', 'orange')
}

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def get_photo_class(request):
    if 'image' not in request.data:
        return Response({"error": "No image file provided"}, status=status.HTTP_400_BAD_REQUEST)

    dirname = str(uuid.uuid4())
    image = request.data['image']
    image_name = default_storage.save(image.name, image)
    image_path = os.path.join(settings.MEDIA_ROOT, image_name)
    image_size = Image.open(image_path).size

    path_to_res = os.path.join('model_api', 'model', 'core', 'runs', 'detect', dirname)
    path_to_txt_dir = os.path.join(path_to_res, 'labels')
    path_to_out_img = os.path.join(path_to_txt_dir, 'out_img.png')

    try:
        run(
            weights='model_api/model/weights.pt',
            conf_thres=0.1,
            imgsz=image_size,
            source=image_path,
            device='cpu',
            save_txt=True,
            nosave=True,
            name=dirname)
        path_to_txt = os.path.join(path_to_txt_dir, os.listdir(path_to_txt_dir)[0])
        with open(path_to_txt, 'r') as F:
            defects = [get_tuple_from_txt_line(line) for line in F.readlines()]
        out_img = render_bounds(image_path, defects)
        print(image_to_base64(out_img)[:50])
        #out_img.save(path_to_out_img)

    finally:
        if os.path.exists(image_path):
            os.remove(image_path)
            pass
        if os.path.exists(path_to_res):
            #shutil.rmtree(path_to_res)
            pass

    return Response({}, status=status.HTTP_200_OK)

def get_tuple_from_txt_line(line):
    line = line.split()
    cls = [int(line[0])]
    other = list(map(float, line[1:]))
    return tuple(cls + other)

def render_bounds(path_to_image: str, positions: List[Tuple[int, float, float, float, float]]) -> Image:
    """ Выделяет на картинке все рамки с найденными классами объектов """

    image = Image.open(path_to_image)
    draw = ImageDraw.Draw(image)
    # Получение размеров изображения
    img_width, img_height = image.size

    for position in positions:
        class_id, rel_x, rel_y, w, h = position

        # Преобразование относительных координат и размеров в абсолютные
        abs_x, abs_y = rel_x * img_width, rel_y * img_height
        abs_w, abs_h = w * img_width, h * img_height

        # Вычисление координат углов прямоугольника
        left, right = abs_x - abs_w / 2, abs_x + abs_w / 2
        top, bottom = abs_y - abs_h / 2, abs_y + abs_h / 2

        # Рисование прямоугольника на изображении
        color = defects_translate[class_id].color
        draw.rectangle(((left, top), (right, bottom)), outline=color, width=2)

        # Добавление текста
        text = defects_translate[class_id].name
        font_size = int(min(img_width, img_height) * 0.03)
        font = ImageFont.truetype('ArialRegular.ttf', size=font_size)

        # Определение размеров текст
        text_bbox = draw.textbbox((0, 0), text, font)
        text_width, text_height = text_bbox[2] - text_bbox[0], (text_bbox[3] - text_bbox[1]) * 1.5

        # Вычисление позиции текста
        # По горизонтали текст выравнивается с левой стороны bounding box
        # По вертикали текст размещается выше bounding box
        text_x, text_y = left, top - text_height
        text_position = (text_x, text_y)

        draw.text(text_position, text, fill=color, font=font)
    return image

def image_to_base64(img):
    output_buffer = BytesIO()
    img.save(output_buffer, format='png')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str



