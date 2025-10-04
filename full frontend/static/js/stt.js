
const MIN_RECORD_SECONDS = 5;
const API_UPLOAD_URL = "http://127.0.0.1:8000/stt/audio/upload/";
const token = localStorage.getItem("accessToken");

const heading = document.getElementById("animated-heading");
const mainTexts = document.querySelector(".main_texts");
const menu = document.getElementById("menu-container");
const recordButtons = document.querySelector(".record_buttons");
const recordStatus = document.getElementById("recordStatus");
const paragraph = document.querySelector(".text p");
const button = document.querySelector(".text a");

const messages = document.getElementById("messages");
const messagesText = document.getElementById("messagesText");
const messagesButton = document.getElementById("messagesButton");

const canvas = document.getElementById("audioVisualizer");
const ctx = canvas.getContext("2d");
const customAudioPlayer = document.querySelector(".custom-audio-player");
const audioPlayback = document.getElementById("audioPlayback");
const saveBtn = document.getElementById("saveBtn");

let mediaRecorder, audioChunks = [], audioBlob = null, isRecording = false;
let audioContext, analyser, dataArray, source, animationId, startTime = null;
let timerInterval = null; 


const defaultSVG = `<svg xmlns="http://www.w3.org/2000/svg" height="54px" viewBox="0 -960 960 960" width="54px" fill="#e3e3e3">
    <path d="M480-400q-50 0-85-35t-35-85v-240q0-50 35-85t85-35q50 0 85 35t35 85v240q0 50-35 85t-85 35Zm0-240Zm-40 520v-123q-104-14-172-93t-68-184h80q0 83 58.5 141.5T480-320q83 0 141.5-58.5T680-520h80q0 105-68 184t-172 93v123h-80Zm40-360q17 0 28.5-11.5T520-520v-240q0-17-11.5-28.5T480-800q-17 0-28.5 11.5T440-760v240q0 17 11.5 28.5T480-480Z"/>
</svg>`;

const recordingSVG = `<svg xmlns="http://www.w3.org/2000/svg" height="54px" viewBox="0 -960 960 960" width="54px" fill="#e3e3e3">
    <path d="M320-640v320-320Zm-80 400v-480h480v480H240Zm80-80h320v-320H320v320Z"/>
</svg>`;

function showMessage(text) {
  messages.style.display = 'flex';
  messages.style.opacity = '1';
  messagesText.innerHTML = text;
}
function hideMessage() {
  messages.style.display = 'none';
}
messagesButton.addEventListener("click", hideMessage);

function createSVGButton(id, svg, size = 54) {
  const btn = document.createElement("button");
  btn.id = id;
  btn.innerHTML = svg;
  btn.style.padding = "20px";
  btn.style.background = "transparent";
  btn.style.borderRadius = "12px";
  return btn;
}
function setupUI() {
  mainTexts.style.display = "block"; // ensure intro texts visible

  recordButtons.innerHTML = `
    <button class="after_buttons" id="after_buttons_1">#</button>
    <button id="recordBtn">${defaultSVG}</button>
    <button class="after_buttons" id="after_buttons_2">🗑</button>
  `;

  // Add click listener **after button exists**
  const recordBtn = document.getElementById("recordBtn");
  if (recordBtn) recordBtn.addEventListener("click", toggleRecording);

  // Make sure record button is visible (CSS might hide it initially)
  recordBtn.style.opacity = "1";
  recordBtn.style.transform = "translateY(0)";
}
setupUI();


(function animateHeading() {
  const words = heading.innerText.split(" ");
  heading.innerHTML = "";
  words.forEach((word, index) => {
    const span = document.createElement("span");
    span.innerText = word + " ";
    span.style.animationDelay = `${index * 0.2}s`;
    heading.appendChild(span);
  });
  setTimeout(() => paragraph.style.animationPlayState = "running", words.length * 200 + 300);
  setTimeout(() => button.style.animationPlayState = "running", words.length * 200 + 800);
})();

// ===================
// Audio Visualizer
// ===================
function startVisualizer(stream) {
  audioContext = new (window.AudioContext || window.webkitAudioContext)();
  analyser = audioContext.createAnalyser();
  source = audioContext.createMediaStreamSource(stream);
  source.connect(analyser);
  analyser.fftSize = 256;
  const bufferLength = analyser.frequencyBinCount;
  dataArray = new Uint8Array(bufferLength);

  function draw() {
    animationId = requestAnimationFrame(draw);
    analyser.getByteFrequencyData(dataArray);
    ctx.fillStyle = "#08090A";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    const barWidth = (canvas.width / bufferLength) * 2.5;
    let x = 0;
    for (let i = 0; i < bufferLength; i++) {
      const barHeight = dataArray[i] / 2;
      ctx.fillStyle = "#fff";
      ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
      x += barWidth + 1;
    }
  }
  draw();
}
function stopVisualizer() {
  cancelAnimationFrame(animationId);
  if (audioContext) audioContext.close();
  ctx.clearRect(0, 0, canvas.width, canvas.height);
}



async function toggleRecording() {
  const recordBtn = document.getElementById("recordBtn");
  const recordTimer = document.getElementById("recordTimer");

  if (!isRecording) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
      mediaRecorder.onstop = () => {
        audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        const audioUrl = URL.createObjectURL(audioBlob);
        audioPlayback.src = audioUrl;
        customAudioPlayer.style.display = 'flex';
        saveBtn.style.display = "inline-block";
        stopVisualizer();

        // ✅ Reset button and timer
        recordBtn.innerHTML = defaultSVG;
        clearInterval(timerInterval);
        recordTimer.textContent = "";
      };

      mediaRecorder.start();
      startVisualizer(stream);
      startTime = Date.now();

      // ✅ Start timer
      recordTimer.textContent = "00:00";
      timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const minutes = String(Math.floor(elapsed / 60)).padStart(2, "0");
        const seconds = String(elapsed % 60).padStart(2, "0");
        recordTimer.textContent = `${minutes}:${seconds}`;
      }, 1000);

      showMessage("🎙 Recording started...");
      recordBtn.innerHTML = recordingSVG; // switch icon
      isRecording = true;
    } catch (err) {
      console.error("Mic error:", err);
      recordStatus.textContent = "⚠️ Microphone access denied!";
    }
  } else {
    const elapsed = (Date.now() - startTime) / 1000;
    if (elapsed < MIN_RECORD_SECONDS) {
      showMessage(`⏳ Record at least ${MIN_RECORD_SECONDS}s (you recorded ${elapsed.toFixed(1)}s).`);
      return;
    }
    mediaRecorder.stop();
    showMessage("✅ Recording stopped. Play below & Save.");
    isRecording = false;
  }
}

document.getElementById("recordBtn").addEventListener("click", toggleRecording);

saveBtn.addEventListener("click", async () => {
  if (!audioBlob) return;
  const formData = new FormData();
  formData.append("file", audioBlob, "recording.mp3");
  recordStatus.textContent = "Uploading...";
  try {
    const response = await fetch(API_UPLOAD_URL, {
      method: "POST",
      headers: { "Authorization": `Bearer ${token}` },
      body: formData
    });
    if (response.ok) {
      const data = await response.json();
      console.log("Transcription:", data.transcription);
      recordStatus.textContent = "✅ Uploaded successfully!";
      showMessage("Uploaded successfully!");
    } else {
      const errorText = await response.text();
      showMessage(`❌ Upload failed (${response.status}), you must be logged in to upload/transcript audio`)
      // recordStatus.textContent = `❌ Upload failed (${response.status})`;
      console.error("Upload error:", errorText);
    }
  } catch (err) {
    console.error("Network error:", err);
    recordStatus.textContent = "⚠️ Upload error!";
  }
});


async function loadHTML(id, path) {
  try {
    const res = await fetch(path);
    if (!res.ok) throw new Error(`Failed to load ${path}`);
    document.getElementById(id).innerHTML = await res.text();
  } catch (e) {
    console.error(e);
  }
}
loadHTML("navbar-container", "/templates/navbar.html");
loadHTML("menu-container", "/templates/menu.html");







