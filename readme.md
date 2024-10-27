Репозиторий модели хакатона AtomicHack2024

<b>Развертывание</b>

1.Установить <i>requirements.txt</i>

    pip install -r requirements.txt

2.Настроить <i>settings.py</i>
    
    Добавьте свой хост в список
    ALLOWED_HOSTS = []

3.Вставьте файл с весами модели по пути:

    modelbackend/model_api/model/weights.pt

4.Запустите приложение

    python manage.py runserver


<b>Готово</b>
