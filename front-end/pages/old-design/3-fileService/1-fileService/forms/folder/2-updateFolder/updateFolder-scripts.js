const username = window.sessionStorage.getItem("username");
const userId = window.sessionStorage.getItem("userId");

if (!username || !userId) {
    alert("❌ You haven't logged in yet!");
    window.location.href = "../../../../0-login/fileService-login.html";
}

const folderId = window.sessionStorage.getItem('folderId');
const projectId = window.sessionStorage.getItem('projectId');

if (!folderId || !projectId) {
    alert('❌ Missing folder or project information!');
    window.location.href = '../../../fileService.html';
}

// Auto-fill the project ID
document.getElementById('projectId').value = projectId;

// Fetch folder data and auto-fill the folder name
async function loadFolderData() {
    try {
        const userId = window.sessionStorage.getItem('userId');
        
        const response = await fetch(`http://localhost:8000/list/folders/${projectId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${userId}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch folder data');
        }

        const folders = await response.json();
        const folderData = folders.find(f => f.id == folderId);

        if (!folderData) {
            throw new Error('Folder not found');
        }

        // Auto-fill the folder name
        document.getElementById('folderName').value = folderData.name || '';

    } catch (error) {
        console.error('Error loading folder data:', error);
        alert('❌ Failed to load folder data: ' + error.message);
    }
}

// Load folder data when page loads
loadFolderData();

/// Update Folder ///
document.getElementById('createFolderForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const folderName = document.getElementById('folderName').value;
    
    try {
        const userId = window.sessionStorage.getItem('userId');
        
        const response = await fetch(`http://localhost:8000/update/project/${projectId}/folder/${folderId}`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${userId}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: folderName,
                userid: userId,
                path: folderName,
            })
        });

        console.log("Status:", response.status, response.statusText);
        console.log("URL:", response.url);

        let data;
        const contentType = response.headers.get("content-type");

        if (contentType && contentType.includes("application/json")) {
            data = await response.json();
        } else {
            const text = await response.text();
            console.log("Non-JSON response body:", text.substring(0, 500));
            data = { detail: `Server returned ${response.status} ${response.statusText}` };
            if (response.status === 404) data.detail += " → Route not found! Check backend URL and server status.";
            if (response.status === 401) data.detail += " → Unauthorized. Your userId token might be invalid.";
        }

        if (response.ok) {
            alert(`✅ Folder "${data.name || folderName}" updated successfully!`);
            window.location.href = '../../../fileService.html';
            return;
        }

        let errorMessage = "❌ Unknown error";

        if (response.status === 404) {
            errorMessage = "❌ 404 - Endpoint not found!\n\nMake sure your backend is running on http://localhost:8000 and has the update folder route.";
        } else if (response.status === 401) {
            errorMessage = "❌ 401 - Unauthorized\n\nYour session might have expired. Try logging in again.";
        } else if (response.status === 422) {
            if (Array.isArray(data.detail)) {
                errorMessage = "Validation Error:\n" + data.detail.map(e => `• ${e.loc.join(" → ")}: ${e.msg}`).join("\n");
            } else {
                errorMessage = data.detail || "Invalid data sent";
            }
        } else if (data.detail) {
            errorMessage = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
        } else {
            errorMessage = `Server Error ${response.status}: ${response.statusText}`;
        }

        alert(errorMessage);

    } catch (error) {
        console.error("Fetch/Network Error:", error);
        alert("⚠️ Cannot reach the server.\n\nIs your backend running on http://localhost:8000?\n\nDetails in console (F12).");
    }
});