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

    // TODO change to use fetch()
    var xhr = new XMLHttpRequest();
    xhr.open(uploadForm.method, uploadForm.getAttribute("action"));
    xhr.upload.addEventListener('progress', uploadProgressHandler, false);
    xhr.send(formData);

    event.preventDefault();
});