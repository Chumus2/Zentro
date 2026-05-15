function formatVideoTime(seconds) {
    if (!Number.isFinite(seconds) || seconds < 0) {
        return "0:00";
    }

    const totalSeconds = Math.floor(seconds);
    const minutes = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;

    return `${minutes}:${secs.toString().padStart(2, "0")}`;
}

function syncVideoPlayer(player) {
    const video = player.querySelector("[data-video]");
    const progress = player.querySelector("[data-progress]");
    const currentTime = player.querySelector("[data-current-time]");
    const duration = player.querySelector("[data-duration]");
    const playButtons = player.querySelectorAll("[data-play-toggle]");
    const muteButton = player.querySelector("[data-mute-toggle]");

    if (!video || !progress || !currentTime || !duration) {
        return;
    }

    const isPlaying = !video.paused && !video.ended;
    player.classList.toggle("Video_Playing", isPlaying);

    playButtons.forEach((button) => {
        const icon = button.querySelector("img");

        if (!icon) {
            return;
        }

        icon.src = isPlaying
            ? button.dataset.pauseIcon
            : button.dataset.playIcon;
    });

    if (muteButton) {
        const icon = muteButton.querySelector("img");

        if (icon) {
            icon.src = video.muted
                ? muteButton.dataset.mutedIcon
                : muteButton.dataset.volumeIcon;
        }
    }

    currentTime.textContent = formatVideoTime(video.currentTime);
    duration.textContent = formatVideoTime(video.duration);

    if (video.duration) {
        progress.value = (video.currentTime / video.duration) * 100;
    } else {
        progress.value = 0;
    }
}


function setupVideoPlayers() {
    const players = document.querySelectorAll("[data-video-player]");

    if (!players.length) {
        return;
    }

    players.forEach((player) => {
        const video = player.querySelector("[data-video]");
        const progress = player.querySelector("[data-progress]");
        const playButtons = player.querySelectorAll("[data-play-toggle]");
        const muteButton = player.querySelector("[data-mute-toggle]");
        const fullscreenButton = player.querySelector("[data-fullscreen-toggle]");

        if (!video || !progress) {
            return;
        }

        playButtons.forEach((button) => {
            button.addEventListener("click", () => {
                if (video.paused) {
                    video.play();
                } else {
                    video.pause();
                }
            });
        });

        video.addEventListener("click", () => {
            if (video.paused) {
                video.play();
            } else {
                video.pause();
            }
        });

        video.addEventListener("play", () => syncVideoPlayer(player));
        video.addEventListener("pause", () => syncVideoPlayer(player));
        video.addEventListener("timeupdate", () => syncVideoPlayer(player));
        video.addEventListener("loadedmetadata", () => syncVideoPlayer(player));
        video.addEventListener("volumechange", () => syncVideoPlayer(player));
        video.addEventListener("ended", () => syncVideoPlayer(player));

        progress.addEventListener("input", () => {
            if (!video.duration) {
                return;
            }

            const percent = Number(progress.value);
            video.currentTime = (percent / 100) * video.duration;
        });

        if (muteButton) {
            muteButton.addEventListener("click", () => {
                video.muted = !video.muted;
            });
        }

        if (fullscreenButton) {
            fullscreenButton.addEventListener("click", async () => {
                if (document.fullscreenElement) {
                    await document.exitFullscreen();
                } else {
                    await player.requestFullscreen();
                }
            });
        }

        syncVideoPlayer(player);
    });
}

document.addEventListener("DOMContentLoaded", setupVideoPlayers);
