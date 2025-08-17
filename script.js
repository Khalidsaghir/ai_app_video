async function generateVideo() {
    const prompt = document.getElementById('prompt').value;
    const num_images = document.getElementById('num_images').value;
    const fps = document.getElementById('fps').value;
    const loading = document.getElementById('loading');
    const message = document.getElementById('message');
    const btn = document.getElementById('generate-btn');
    const container = document.getElementById('video-container');

    // Reset UI
    message.innerHTML = '';
    container.innerHTML = '';
    btn.disabled = true;
    loading.style.display = 'block';

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({prompt, num_images, fps})
        });
        const data = await response.json();

        if(data.video_url){
            message.innerHTML = '<span style="color:green;">Video generated successfully!</span>';
            const video = document.createElement('video');
            video.src = data.video_url;
            video.controls = true;
            video.style.maxWidth = '100%';
            container.appendChild(video);
            video.play();
        } else if(data.error){
            message.innerHTML = `<span style="color:red;">${data.error}</span>`;
        }
    } catch (err) {
        message.innerHTML = `<span style="color:red;">Error: ${err.message}</span>`;
    } finally {
        loading.style.display = 'none';
        btn.disabled = false;
    }
}
