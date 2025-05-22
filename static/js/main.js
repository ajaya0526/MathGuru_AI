const video = document.getElementById('camera');
const captureBtn = document.getElementById('captureBtn');
const snapshot = document.getElementById('snapshot');
const feedbackAudio = document.getElementById('feedbackAudio');
const expressionOutput = document.getElementById('text');
const resultOutput = document.getElementById('result');
const stepsOutput = document.getElementById('steps');

// Hint system globals
let hintHistory = [], currentHintIndex = -1;
let hintAudioEn = '', hintAudioHi = '';
let finalAnswerEn = '', finalAnswerHi = '';

// Enable webcam
if (video) {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(err => {
            alert("❌ Cannot access webcam.");
            console.error(err);
        });
}

// Capture from camera and send
if (captureBtn) {
    captureBtn.addEventListener('click', () => {
        showLoading();
        const context = snapshot.getContext('2d');
        snapshot.width = video.videoWidth;
        snapshot.height = video.videoHeight;
        context.drawImage(video, 0, 0, snapshot.width, snapshot.height);
        snapshot.toBlob(blob => {
            const formData = new FormData();
            formData.append('image', blob, 'camera.jpg');
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                hideLoading();
                if (data.error) {
                    showError(data.error);
                } else {
                    updateUI(data);
                }
            });
        }, 'image/jpeg');
    });
}

function updateUI(data) {
    expressionOutput.textContent = data.extracted || '---';
    resultOutput.textContent = data.result || '--';
    stepsOutput.textContent = data.steps || '📘 No explanation yet.';

    if (data.audio) {
        const audioPath = '/' + data.audio + '?t=' + Date.now();
        feedbackAudio.src = audioPath;
        feedbackAudio.play();
    }

    // ✅ Load Hint 1 automatically
    if (data.hint) {
        hintHistory = [data.hint];
        currentHintIndex = 0;
        hintAudioEn = '/' + data.audio_en;
        hintAudioHi = '/' + data.audio_hi;
        updateHintDisplay();
    }
}

function updateHintDisplay() {
    document.getElementById('hintText').innerText = hintHistory[currentHintIndex];
    document.getElementById('prevHintBtn').style.display = currentHintIndex > 0 ? 'inline-block' : 'none';
    document.getElementById('hintAudioControls').style.display = 'block';
}

function showError(msg) {
    expressionOutput.textContent = msg;
    resultOutput.textContent = '--';
    stepsOutput.textContent = '❌ No steps.';
}

function showLoading() {
    const modal = document.getElementById('loadingModal');
    if (modal) modal.style.display = 'flex';
}

function hideLoading() {
    const modal = document.getElementById('loadingModal');
    if (modal) modal.style.display = 'none';
}
