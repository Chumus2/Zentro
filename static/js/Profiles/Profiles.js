const editToggle = document.getElementById("edit-toggle");
const editCancel = document.getElementById("edit-cancel");
const profileActions = document.getElementById("profile-actions");
const avatarLabel = document.getElementById("avatar-label");
const avatarInput = document.getElementById("avatar-input");
const avatarPreview = document.getElementById("avatar-preview");


function enterEditMode() {
    document.querySelectorAll(".Profile_View").forEach(el => el.hidden = true);
    document.querySelectorAll(".Profile_Input").forEach(el => el.hidden = false);
    profileActions.hidden = false;
    avatarLabel.hidden = false;
    editToggle.hidden = true;
}


function exitEditMode() {
    document.querySelectorAll(".Profile_View").forEach(el => el.hidden = false);
    document.querySelectorAll(".Profile_Input").forEach(el => el.hidden = true);
    profileActions.hidden = true;
    avatarLabel.hidden = true;
    editToggle.hidden = false;
}

editToggle.addEventListener("click", enterEditMode);
editCancel.addEventListener("click", exitEditMode);


avatarInput.addEventListener("change", () => {
    const file = avatarInput.files[0];

    if (file) {
        avatarPreview.src = URL.createObjectURL(file);
    }
});