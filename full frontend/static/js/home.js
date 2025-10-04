const main_container = document.querySelector(".container")
const openBtn = document.getElementById('open')
const closeBtn = document.getElementById('close')
const sidebar = document.querySelector('.sidebar')

openBtn.addEventListener('click', () => {
  sidebar.classList.toggle('shown')
})

closeBtn.addEventListener('click', () => {
    sidebar.classList.remove('shown')
})


// Main function for fetch
async function getData(url) {
    const accessToken = localStorage.getItem("accessToken");  
    const audios = document.querySelector(".audios")
    const audioNamesList = document.querySelector(".audio_names_list")

    if (!accessToken) {
      console.error("No access token found in localStorage");
      return;
    }

    try {
        const response = await fetch(url, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${accessToken}`,
            "Content-Type": "application/json"
            }
        });   
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        } 
        const result = await response.json();
        audios.innerHTML = "";

        result.forEach(element => {
            const div = document.createElement("div");
            div.className = 'audio'
            div.innerHTML = `
            <header>
                <p>${element.name || "Unnamed audio"} . <a href="/templates/audio_details.html">See full audio</a> </p>
                <a href="#" class="more_button"><svg xmlns="http://www.w3.org/2000/svg" height="24px" 
                viewBox="0 -960 960 960" width="24px" fill="#616666">
                <path d="M240-160q-33 0-56.5-23.5T160-240q0-33 23.5-56.5T240-320q33 0 56.5 23.5T320-240q0 33-23.5 56.5T240-160Zm240 0q-33 0-56.5-23.5T400-240q0-33 23.5-56.5T480-320q33 0 56.5 23.5T560-240q0 33-23.5 56.5T480-160Zm240 0q-33 0-56.5-23.5T640-240q0-33 23.5-56.5T720-320q33 0 56.5 23.5T800-240q0 33-23.5 56.5T720-160ZM240-400q-33 0-56.5-23.5T160-480q0-33 23.5-56.5T240-560q33 0 56.5 23.5T320-480q0 33-23.5 56.5T240-400Zm240 0q-33 0-56.5-23.5T400-480q0-33 23.5-56.5T480-560q33 0 56.5 23.5T560-480q0 33-23.5 56.5T480-400Zm240 0q-33 0-56.5-23.5T640-480q0-33 23.5-56.5T720-560q33 0 56.5 23.5T800-480q0 33-23.5 56.5T720-400ZM240-640q-33 0-56.5-23.5T160-720q0-33 23.5-56.5T240-800q33 0 56.5 23.5T320-720q0 33-23.5 56.5T240-640Zm240 0q-33 0-56.5-23.5T400-720q0-33 23.5-56.5T480-800q33 0 56.5 23.5T560-720q0 33-23.5 56.5T480-640Zm240 0q-33 0-56.5-23.5T640-720q0-33 23.5-56.5T720-800q33 0 56.5 23.5T800-720q0 33-23.5 56.5T720-640Z"/></svg></a>
            </header>
            <div class="costum_audio_player">
                <button class="play_button">
                    <svg xmlns="http://www.w3.org/2000/svg" class="playIcon" height="28px" viewBox="0 -960 960 960" width="28px" fill="#fff">
                      <path d="M320-200v-560l440 280-440 280Z"/>
                    </svg>
                </button>

                <div class="progress-container">
                    <div class="progress"></div>
                </div>

                <div class="time">
                    <span class="currentTime">0:00</span>
                </div>

                <audio src="${element.file}"></audio>
            </div>
            <footer>
                <button class="modify_button">Modify with AI</button>
                <div class="like_container">
                    <button class="like_button"><svg xmlns="http://www.w3.org/2000/svg" height="22px" viewBox="0 -960 960 960" width="22px" fill="#e3e3e3"><path d="m384-334 96-74 96 74-36-122 90-64H518l-38-124-38 124H330l90 64-36 122ZM233-120l93-304L80-600h304l96-320 96 320h304L634-424l93 304-247-188-247 188Zm247-369Z"/></svg></button><span>Like</span>
                </div>
                <div class="edit_buttons">

                    <details class="dropdown">
                        <summary aria-label="Open menu">
                            <svg aria-hidden="true" height="16" fill="#fff" viewBox="0 0 16 16" width="16" class="octicon octicon-triangle-down">
                                <path d="m4.427 7.427 3.396 3.396a.25.25 0 0 0 .354 0l3.396-3.396A.25.25 0 0 0 11.396 7H4.604a.25.25 0 0 0-.177.427Z"></path>
                            </svg>
                        </summary>
                        <div class="dropdown-content">
                            <p>Details</p>
                        </div>
                    </details>
                </div>
            </footer>

            `;
            
            audios.appendChild(div);


            // === Add audio name into sidebar ===
            const nameItem = document.createElement("div");
            nameItem.className = "audio_name_item";
            nameItem.textContent = element.name || "Unnamed audio";
            audioNamesList.appendChild(nameItem);


            const audio = div.querySelector("audio");
            const playBtn = div.querySelector(".play_button");
            const playIcon = div.querySelector(".playIcon path");
            const progressContainer = div.querySelector(".progress-container");
            const progress = div.querySelector(".progress");
            const currentTimeEl = div.querySelector(".currentTime");

            playBtn.addEventListener("click", () => {
                if (audio.paused) {
                    document.querySelectorAll("audio").forEach(a => {
                        if (a !== audio) {
                            a.pause();
                            a.closest(".costum_audio_player")
                              .querySelector(".playIcon path")
                              .setAttribute("d", "M320-200v-560l440 280-440 280Z");
                        }
                    });
                    audio.play();
                    playIcon.setAttribute("d", "M320-200h120v-560H320v560Zm200 0h120v-560H520v560Z"); // pause
                } else {
                    audio.pause();
                    playIcon.setAttribute("d", "M320-200v-560l440 280-440 280Z"); // play
                }
            });

            audio.addEventListener("timeupdate", () => {
                const progressPercent = (audio.currentTime / audio.duration) * 100;
                progress.style.width = `${progressPercent}%`;

                const minutes = Math.floor(audio.currentTime / 60);
                const seconds = Math.floor(audio.currentTime % 60).toString().padStart(2, "0");
                currentTimeEl.textContent = `${minutes}:${seconds}`;
            });

            progressContainer.addEventListener("click", (e) => {
                const width = progressContainer.clientWidth;
                const clickX = e.offsetX;
                const duration = audio.duration;
                audio.currentTime = (clickX / width) * duration;
            });

            audio.addEventListener("ended", () => {
                playIcon.setAttribute("d", "M320-200v-560l440 280-440 280Z"); // back to play
            });
        });
    } catch (error) {
      console.error("Error:", error.message);
    }
}

getData("http://127.0.0.1:8000/stt/audio/my_audios/");
