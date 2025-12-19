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

/// Login ///
document.getElementById('loginForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const usernameInput = document.getElementById('usernameInput').value;
    const passwordInput = document.getElementById('passwordInput').value;

    try {
        const response = await fetch('http://localhost:8000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                username: usernameInput,
                password: passwordInput,
            })
        });

        const data = await response.json();
        console.log("🔍 Response:", data);

        if (response.ok) {
            window.sessionStorage.setItem("token", data.token);
            
            alert(`✅ Login successful! Welcome, ${usernameInput}!`);

            window.sessionStorage.setItem("username", usernameInput);
            window.location.href = '../1-groupService/groupService.html';
        } else {
            let errorMessage = "❌ Failed to login.";

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