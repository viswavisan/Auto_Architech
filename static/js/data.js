$(document).ready(function() {
    document.getElementById('upload').addEventListener('click', async () => {
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];
        if (!file) {document.getElementById('error').innerText = 'Please select a file.';return;}
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch('/uploadfile', { method: 'POST', body: formData });
        const result = await response.json();
        document.getElementById('response').innerText = response.ok ? `File uploaded: ${result.filename}` : `Error: ${result.detail || 'Upload failed'}`;
        document.getElementById('error').innerText = response.ok ? '' : 'Upload failed';});

    document.getElementById('wrap').addEventListener('click', () => {document.getElementById('dynamic').style.whiteSpace = wrapCheckbox.checked ? 'normal' : 'nowrap';});
});