document.getElementById('photo-input').addEventListener('change', function(event) {
    const preview = document.getElementById('preview');
    preview.innerHTML = ''; // Clear previous previews
    const files = event.target.files;
    if (files) {
        Array.from(files).forEach(file => {
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                preview.appendChild(img);
            }
            reader.readAsDataURL(file);
        });
    }
});