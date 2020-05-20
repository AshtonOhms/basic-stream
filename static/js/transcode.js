const transcodeProgress = document.getElementById('transcode-progress');

setTimeout(() => {
    let response = await fetch('status');

    if (response.ok) {
        let status = await response.json();

        transcodeProgress.setAttribute('value', status.time);
        transcodeProgress.setAttribute('max', status.duration);
    } else {
        console.log("Error fetching status: " + response.status);
    }
}, 500);