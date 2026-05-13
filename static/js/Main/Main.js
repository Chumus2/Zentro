const menuToggleButton = document.getElementById("menu-toggle");
const searchDropdown = document.getElementById("search-dropdown");

const chatCardToggleButton = document.getElementById("chatcard-toggle");
const chatCardDropdown = document.getElementById("chatcard-dropdown");

const pinnedToggleButton = document.getElementById("pinned-toggle");
const pinnedDropdown = document.getElementById("pinned-dropdown");

const chatPanelOverlay = document.getElementById("chat-panel-overlay");

const messagesBox = document.querySelector(".Messages_Box");
const messageActionAreas = document.querySelectorAll(".Message_Actions");

const pinnedMessageRows = document.querySelectorAll(".Pinned_Message_Row");

const editButtons = document.querySelectorAll(".Message_Edit_Button");
const editCancelButtons = document.querySelectorAll(".Message_Edit_Cancel");

const replyButtons = document.querySelectorAll(".Message_Reply_Button");
const replyBar = document.getElementById("reply-bar");
const replyBarAuthor = document.getElementById("reply-bar-author");
const replyBarText = document.getElementById("reply-bar-text");
const replyBarCancel = document.getElementById("reply-bar-cancel");
const replyToInput = document.getElementById("reply-to-input");

const filesToggle = document.getElementById("files-toggle");
const filesDropdown = document.getElementById("files-dropdown");

const chooseMediaButton = document.getElementById("choose-media-button");
const mediaInput = document.getElementById("media-input");
const selectedFileDropdown = document.getElementById("selected-file-dropdown");


function toggleMessageEditMode(messageItem, shouldOpen) {
    if (!messageItem) {
        return;
    }

    const textNode = messageItem.querySelector(".Message_Text");
    const editForm = messageItem.querySelector(".Message_Edit_Form");
    const actions = messageItem.querySelector(".Message_Actions");
    const textarea = messageItem.querySelector(".Message_Edit_Textarea");

    if (!textNode || !editForm) {
        return;
    }

    if (shouldOpen) {
        textNode.hidden = true;
        editForm.hidden = false;

        if (actions) {
            actions.hidden = true;
        }

        if (textarea) {
            textarea.focus();
            textarea.setSelectionRange(textarea.value.length, textarea.value.length);
        }
    } else {
        textNode.hidden = false;
        editForm.hidden = true;

        if (actions) {
            actions.hidden = false;
        }
    }
}

function clearReplyState() {
    if (replyToInput) {
        replyToInput.value = "";
    }

    if (replyBar) {
        replyBar.hidden = true;
    }

    if (replyBarAuthor) {
        replyBarAuthor.textContent = "";
    }

    if (replyBarText) {
        replyBarText.textContent = "";
    }
}

function syncOverlayState() {
    if (!chatPanelOverlay) {
        return;
    }

    const isSearchOpen = searchDropdown && searchDropdown.classList.contains("Search_Dropdown__open");
    const isChatCardOpen = chatCardDropdown && chatCardDropdown.classList.contains("ChatCard_Dropdown__open");
    const isPinnedOpen = pinnedDropdown && pinnedDropdown.classList.contains("Pinned_Messages_Dropdown__open");
    const isSelectedFileOpen = selectedFileDropdown && !selectedFileDropdown.hidden;

    if (isSearchOpen || isChatCardOpen || isPinnedOpen || isSelectedFileOpen) {
        chatPanelOverlay.classList.add("Chat_Panel_Overlay__visible");
    } else {
        chatPanelOverlay.classList.remove("Chat_Panel_Overlay__visible");
    }
}

function setupDropdownToggle(button, dropdown, openClass, hiddenClass) {
    if (!button || !dropdown) {
        return;
    }

    dropdown.classList.add(hiddenClass)

    button.addEventListener("click", () => {
        const isOpen = dropdown.classList.contains(openClass);

        if (isOpen) {
            dropdown.classList.remove(openClass);
            dropdown.classList.add(hiddenClass);
            button.setAttribute("aria-expanded", "false");
        } else {
            dropdown.classList.remove(hiddenClass);
            dropdown.classList.add(openClass);
            button.setAttribute("aria-expanded", "true");
        }

        syncOverlayState();
    });
}


setupDropdownToggle(
    menuToggleButton,
    searchDropdown,
    "Search_Dropdown__open",
    "Search_Dropdown__hidden"
);

setupDropdownToggle(
    chatCardToggleButton,
    chatCardDropdown,
    "ChatCard_Dropdown__open",
    "ChatCard_Dropdown__hidden"
);

setupDropdownToggle(
    pinnedToggleButton,
    pinnedDropdown,
    "Pinned_Messages_Dropdown__open",
    "Pinned_Messages_Dropdown__hidden"
);

setupDropdownToggle(
    filesToggle,
    filesDropdown,
    "Files_Dropdown__open",
    "Files_Dropdown__hidden"
);


if (messagesBox) {
    requestAnimationFrame(() => {
        messagesBox.scrollTop = messagesBox.scrollHeight;
    });
}

if (messageActionAreas.length) {
    messageActionAreas.forEach((actionArea) => {
        const moreButton = actionArea.querySelector(".Message_More_Button");
        const dropdown = actionArea.querySelector(".Message_Dropdown");

        if (!moreButton || !dropdown) {
            return;
        }

        moreButton.addEventListener("click", (event) => {
            event.stopPropagation();

            const isOpen = dropdown.classList.contains("Message_Dropdown__open");

            document.querySelectorAll(".Message_Dropdown__open").forEach((openedDropdown) => {
                if (openedDropdown !== dropdown) {
                    openedDropdown.classList.remove("Message_Dropdown__open");
                }
            });

            if (isOpen) {
                dropdown.classList.remove("Message_Dropdown__open");
            } else {
                dropdown.classList.add("Message_Dropdown__open");
            }
        });

        dropdown.addEventListener("click", (event) => {
            event.stopPropagation();
        });
    });
}

if (editButtons.length) {
    editButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();

            const messageItem = button.closest(".Message_Item");
            const dropdown = button.closest(".Message_Dropdown");

            if (dropdown) {
                dropdown.classList.remove("Message_Dropdown__open");
            }

            toggleMessageEditMode(messageItem, true);
        });
    });
}

if (editCancelButtons.length) {
    editCancelButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            event.preventDefault();

            const messageItem = button.closest(".Message_Item");
            toggleMessageEditMode(messageItem, false);
        });
    });
}

if (replyButtons.length) {
    replyButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();

            const messageItem = button.closest(".Message_Item");
            const dropdown = button.closest(".Message_Dropdown");

            if (!messageItem || !replyToInput || !replyBar || !replyBarAuthor || !replyBarText) {
                return;
            }

            if (dropdown) {
                dropdown.classList.remove("Message_Dropdown__open");
            }

            replyToInput.value = messageItem.dataset.messageId || "";
            replyBarAuthor.textContent = messageItem.dataset.messageAuthor || "User";
            replyBarText.textContent = messageItem.dataset.messageText || "";
            replyBar.hidden = false;
        });
    });
}

if (replyBarCancel) {
    replyBarCancel.addEventListener("click", () => {
        clearReplyState();
    });
}

if (pinnedMessageRows.length) {
    pinnedMessageRows.forEach((row) => {

        row.addEventListener("click", () => {
            const messageId = row.dataset.messageId;
            const targetMessage = document.getElementById(`message-${messageId}`);

            pinnedDropdown.classList.remove("Pinned_Messages_Dropdown__open");
            pinnedDropdown.classList.add("Pinned_Messages_Dropdown__hidden");
            pinnedToggleButton.setAttribute("aria-expanded", "false");
            syncOverlayState();

            if (targetMessage && messagesBox) {
                const boxRect = messagesBox.getBoundingClientRect();
                const messageRect = targetMessage.getBoundingClientRect();
                const scrollTop = messagesBox.scrollTop + (messageRect.top - boxRect.top) - 80;

                messagesBox.scrollTo({
                    top: scrollTop,
                    behavior: "smooth"
                });
            }
        });

    });
}


if (chooseMediaButton && mediaInput) {
    chooseMediaButton.addEventListener("click", () => {
        filesDropdown.classList.remove("Files_Dropdown__open");
        filesDropdown.classList.add("Files_Dropdown__hidden");
        filesToggle.setAttribute("aria-expanded", "false");

        mediaInput.value = "";
        mediaInput.accept = "image/*,video/*";
        mediaInput.click();
    });
}

if (mediaInput && selectedFileDropdown) {
    mediaInput.addEventListener("change", () => {
        const selectedFile = mediaInput.files?.[0];

        if (!selectedFile) {
            return;
        }

        selectedFileDropdown.textContent = selectedFile.name;
        selectedFileDropdown.hidden = false;
        syncOverlayState();
    });
}
