const uploadForm = document.getElementById('upload-form');
const uploadProgress = document.getElementById('upload-progress');

function uploadProgressHandler(event) {
    if (event.lengthComputable) {
        uploadProgress.setAttribute('value', event.loaded);
        uploadProgress.setAttribute('max', event.total);
    }
}

uploadForm.addEventListener('submit', (event) => {
    const formData = new FormData(uploadForm);

    var xhr = new XMLHttpRequest();
    xhr.open(uploadForm.method, uploadForm.getAttribute("action"));
    xhr.addEventListener('progress', uploadProgressHandler);
    xhr.send(formData);

    event.preventDefault();
});