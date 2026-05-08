const chatIconInput = document.getElementById("chat_icon");
const chatIconPreview = document.getElementById("chat-icon-preview");

if (chatIconInput && chatIconPreview) {
    const allowedTypes = ["image/png", "image/jpeg"];

    chatIconInput.addEventListener("change", () => {
        const selectedFile = chatIconInput.files && chatIconInput.files[0];

        if (!selectedFile) {
            chatIconPreview.innerHTML = "<span>Preview</span>";
            chatIconPreview.classList.remove("ChatCreation_Icon_Preview__filled");
            return;
        }

        if (!allowedTypes.includes(selectedFile.type)) {
            chatIconInput.value = "";
            chatIconPreview.innerHTML = "<span>Preview</span>";
            chatIconPreview.classList.remove("ChatCreation_Icon_Preview__filled");
            return;
        }

        const reader = new FileReader();

        reader.onload = (event) => {
            chatIconPreview.innerHTML = `<img src="${event.target.result}" alt="Chat icon preview">`;
            chatIconPreview.classList.add("ChatCreation_Icon_Preview__filled");
        };

        reader.readAsDataURL(selectedFile);
    });
}