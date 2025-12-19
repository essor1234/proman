/// 🚧 Check login status IMMEDIATELY ///
const username = window.sessionStorage.getItem("username");
const userId = window.sessionStorage.getItem("userId");

if (!username || !userId) {
    alert("❌ You haven't logged in yet!");
    window.location.href = "../../../0-login/projectService-login.html";
}

/// Create Project ///
document.getElementById('createProjectForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const groupId = document.getElementById('groupId').value;
    const projectName = document.getElementById('projectName').value;
    
    try {
        const userId = window.sessionStorage.getItem('userId');
        
        const response = await fetch("http://localhost:8000/create/project", {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${userId}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                groupId: groupId,
                name: projectName,
            })
        });

        const data = await response.json();
        console.log("🔍 Response:", data);

        if (response.ok) {
            alert(`✅ Project "${data.name}" has successfully created!`);
            window.location.href = '../../projectService.html';
        } else {
            let errorMessage = "❌ Failed to create project.";

            if (Array.isArray(data)) {
                errorMessage = data.map(err => err.msg).join("\n");
            } else if (data.detail) {
                errorMessage = data.detail;
            }

            alert(`❌ ${errorMessage}`);
        }

    } catch (error) {
        console.error("❌ Network/Server Error: ", error);
        alert("⚠️ Unable to connect to the server.");
    }
});