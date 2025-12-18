/// 🚧 Check login status IMMEDIATELY ///
const token = window.sessionStorage.getItem("token");

if (!token) {
    alert("❌ You haven't logged in yet!");
    window.location.href='/1-groupService/0-login/groupService-login.html';
}

/// Create Group ///
document.getElementById('createGroupForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const groupNameInput        = document.getElementById('groupNameInput').value;
    const groupDescriptionInput = document.getElementById('groupDescriptionInput').value;
    const groupTypeInput        = document.querySelector('input[name="groupTypeInput"]:checked').value;

    try {
        const token = window.sessionStorage.getItem('token');
        
        const response = await fetch("http://localhost:8000/create/group", {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: groupNameInput,
                description: groupDescriptionInput,
                visibility: groupTypeInput,
            })
        });

        const data = await response.json();
        console.log("🔍 Response: ", data);

        if (response.ok) {
            alert(`✅ Group "${data.name}" has successfully created!`);
            window.location.href='../../groupService.html';
        } else {
            let errorMessage = "❌ Failed to create group.";

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