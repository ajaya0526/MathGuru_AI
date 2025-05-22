// =========================
// Hindi Text-to-Speech Handler
// =========================

function playHindiAudio() {
    const answer = document.getElementById('result')?.innerText?.trim();
    const steps = document.getElementById('steps')?.innerText?.trim();

    let speakText = '';

    if (steps && steps !== 'Waiting for MathGuru response...' && steps !== '--') {
        speakText = steps;
    } else if (answer && answer !== '--') {
        speakText = answer;
    } else {
        alert("⚠️ No valid Hindi text to speak.");
        return;
    }

    if (!('speechSynthesis' in window)) {
        alert("❌ Your browser does not support speech synthesis.");
        return;
    }

    const utterance = new SpeechSynthesisUtterance(speakText);
    utterance.lang = 'hi-IN';
    utterance.pitch = 1.0;
    utterance.rate = 0.9;
    utterance.volume = 1.0;

    // Try selecting a Hindi voice explicitly
    const voices = window.speechSynthesis.getVoices();

    const hindiVoice = voices.find(v =>
        v.lang === 'hi-IN' || v.name.toLowerCase().includes('hindi')
    );

    if (hindiVoice) {
        utterance.voice = hindiVoice;
    } else {
        console.warn("⚠️ Hindi voice not found. Using default.");
    }

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
}

// Some browsers (like Chrome) load voices asynchronously
if (typeof speechSynthesis !== 'undefined') {
    speechSynthesis.onvoiceschanged = () => {
        // Preload voices for better detection
        speechSynthesis.getVoices();
    };
}
