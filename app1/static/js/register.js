const usernameField = document.querySelector("#usernameField");
const feedBackArea = document.querySelector(".invalid_feedback");
const usernameSuccessOutput = document.querySelector(".usernameSuccessOutput");

const emailField = document.querySelector("#emailField");
const emailFeedBackArea = document.querySelector(".emailFeedBackArea");

const passwordField = document.querySelector("#passwordField");
const showPasswordToggle = document.querySelector(".showPasswordToggle");

const submitBtn = document.querySelector(".submit-btn");

// username validation
usernameField.addEventListener("keyup", (e) => {
    const usernameVal = e.target.value;
    usernameField.classList.remove("is-invalid");
    feedBackArea.style.display = "none";
    usernameSuccessOutput.style.display = "block";
    usernameSuccessOutput.textContent = `Checking ${ usernameVal }`;

    if (usernameVal.length > 0) {
        const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ "username": usernameVal })
        };

        fetch("/authentication/validate-username", requestOptions)
        .then((res) => res.json())
        .then((data) => {
            console.log(data);
            usernameSuccessOutput.style.display = "none";
            if (data.username_error) {
                submitBtn.disabled = true;
                usernameField.classList.add("is-invalid");
                feedBackArea.style.display = "block";
                feedBackArea.innerHTML = `<p>${ data.username_error }</p>`;
            } else {
                submitBtn.removeAttribute("disabled");
            }
        });
    }
});

// email validation
emailField.addEventListener("keyup", (e) => {
    const emailVal = e.target.value;
    emailField.classList.remove("is-invalid");
    emailFeedBackArea.style.display = "none";

    if (emailVal.length > 0) {
        fetch("/authentication/validate-email", {
            method: "POST",
            body: JSON.stringify({ "email": emailVal })
        })
        .then((res) => res.json())
        .then((data) => {
            if (data.email_error) {
                submitBtn.disabled = true;
                emailField.classList.add("is-invalid");
                emailFeedBackArea.style.display = "block";
                emailFeedBackArea.innerHTML = `<p>${ data.email_error }</p>`;
            } else {
                submitBtn.removeAttribute("disabled");
            }
        });
    }
});

// Show Password toggle
const handleToggleInput = (e) => {
    if (showPasswordToggle.textContent == "SHOW") {
        showPasswordToggle.textContent = "HIDE";
        passwordField.setAttribute("type", "text");
    } else {
        showPasswordToggle.textContent = "SHOW";
        passwordField.setAttribute("type", "password");
    }
};

showPasswordToggle.addEventListener("click", handleToggleInput);
