/// Show/Hide Password ///
const passwordInput = document.getElementById('passwordInput');
const showHide      = document.getElementById('showHide');

passwordInput.addEventListener('input', () => {
    if (passwordInput.value.length > 0) {
        showHide.classList.add('visible');
    } else {
        showHide.classList.remove('visible');
    }
});

showHide.addEventListener('click', () => {
    if (passwordInput.type === 'password') {
        passwordInput.type   = 'text';
        showHide.textContent = 'Hide';
    } else {
        passwordInput.type   = 'password';
        showHide.textContent = 'Show';
    }
});

/// Register ///
document.getElementById('registerForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const emailInput    = document.getElementById('emailInput').value;
    const usernameInput = document.getElementById('usernameInput').value;
    const passwordInput = document.getElementById('passwordInput').value;

    try {
        const response = await fetch('http://localhost:8000/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                email: emailInput,
                username: usernameInput,
                password: passwordInput
            })
        });

        const data = await response.json();
        console.log("🔍 Response:", data);

        if (response.ok) {
            alert(`✅ Your account has successfully registered! Let's log in now ${data.username}.`);
            window.location.href = '../fileService-login.html';
        } else {
            let errorMessage = "❌ Failed to register.";

            if (Array.isArray(data)) {
                errorMessage = data.map(err => err.msg).join(", ");
            } else if (data.detail) {
                errorMessage = data.detail;
            }

            alert(`❌ ${errorMessage}`);
        }

    } catch (error) {
        console.error("❌ Network/Server Error:", error);
        alert("⚠️ Unable to connect to the server.");
    }
});