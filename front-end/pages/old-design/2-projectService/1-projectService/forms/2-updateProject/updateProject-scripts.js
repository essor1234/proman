/// 🚧 Check login status IMMEDIATELY ///
const username = window.sessionStorage.getItem("username");
const userId = window.sessionStorage.getItem("userId");

if (!username || !userId) {
    alert("⚠ You haven't logged in yet!");
    window.location.href = "../../../0-login/projectService-login.html";
}

/// Load project data when page loads ///
window.addEventListener('DOMContentLoaded', async function() {
    const projectId = window.sessionStorage.getItem('projectId');
    
    if (!projectId) {
        alert("❌ No project ID provided!");
        window.location.href = '../../projectService.html';
        return;
    }
    
    // Set the project ID in the readonly field
    document.getElementById('projectId').value = projectId;
    
    // Fetch project details
    try {
        const userId = window.sessionStorage.getItem('userId');
        const response = await fetch(`http://localhost:8000/read/project/${projectId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${userId}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const project = await response.json();
            
            // Fill in the form fields
            document.getElementById('projectNameInput').value = project.name;
            document.getElementById('groupIdInput').value = project.groupId;
            
            console.log("✅ Project data loaded:", project);
        } else {
            const data = await response.json();
            alert(`❌ Failed to load project data: ${data.detail || 'Unknown error'}`);
            window.location.href = 'projectService.html';
        }
    } catch (error) {
        console.error("❌ Error loading project:", error);
        alert("⚠️ Unable to load project data. Please try again.");
        window.location.href = '../../projectService.html';
    }
});

/// Update Project ///
document.getElementById('updateProjectForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const projectId = document.getElementById('projectId').value;
    const projectNameInput = document.getElementById('projectNameInput').value;
    const groupIdInput = document.getElementById('groupIdInput').value;

    try {
        const userId = window.sessionStorage.getItem('userId');
        
        const response = await fetch(`http://localhost:8000/update/project/${projectId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${userId}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: projectNameInput,
                groupId: parseInt(groupIdInput)
            })
        });

        const data = await response.json();
        console.log("📦 Response:", data);

        if (response.ok) {
            alert(`✅ Project "${data.name}" has successfully updated!`);
            window.location.href = '../../projectService.html';
        } else {
            let errorMessage = "❌ Failed to update project.";

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