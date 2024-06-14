import os
import random

from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def get_photo_class(request):
    if 'image' not in request.data:
        return Response({"error": "No image file provided"}, status=status.HTTP_400_BAD_REQUEST)

    image = request.data['image']
    image_name = default_storage.save(image.name, image)
    image_path = os.path.join(settings.MEDIA_ROOT, image_name)

    try:
        classes = ['Идеальный шов', 'Непроваренный шов', 'Трещина']
        response_data = {
            "class": random.choice(classes),
        }
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)
            pass

    return Response(response_data, status=status.HTTP_200_OK)