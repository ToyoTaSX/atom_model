document.getElementById('photo-input').addEventListener('change', function(event) {
    const files = event.target.files;
    if (files) {
        const formData = new FormData();
        formData.append('image', files[0]);

        fetch('/api/get_photo_class/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.image_base64) {
                // Создаем элемент img для отображения обработанного изображения
                const imgElement = document.createElement('img');
                imgElement.src = 'data:image/png;base64,' + data.image_base64;

                // Очищаем предыдущие превью и добавляем новое изображение
                const preview = document.getElementById('preview');
                preview.innerHTML = '';
                preview.appendChild(imgElement);
            } else {
                console.error('Ответ сервера не содержит image_base64');
            }
        })
        .catch(error => {
            console.error('Ошибка при отправке или получении изображения:', error);
        });
    }
});
