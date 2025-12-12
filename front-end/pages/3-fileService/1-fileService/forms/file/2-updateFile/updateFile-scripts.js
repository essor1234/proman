const username = window.sessionStorage.getItem("username");
const userId = window.sessionStorage.getItem("userId");

if (!username || !userId) {
    alert("❌ You haven't logged in yet!");
    window.location.href = "../../../../0-login/fileService-login.html";
}

const fileId = window.sessionStorage.getItem('fileId');
const projectId = window.sessionStorage.getItem('projectId');

if (!fileId || !projectId) {
    alert('❌ Missing file or project information!');
    window.location.href = '../../../fileService.html';
}

// Auto-fill the project ID
document.getElementById('projectId').value = projectId;

// Fetch file data and auto-fill the file name
async function loadFileData() {
    try {
        const userId = window.sessionStorage.getItem('userId');
        
        const response = await fetch(`http://localhost:8000/list/files/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${userId}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch file data');
        }

        const files = await response.json();
        const fileData = files.find(f => f.id == fileId);

        if (!fileData) {
            throw new Error('File not found');
        }

        // Auto-fill the file name
        document.getElementById('fileName').value = fileData.name || '';

    } catch (error) {
        console.error('Error loading file data:', error);
        alert('❌ Failed to load file data: ' + error.message);
    }
}

// Load file data when page loads
loadFileData();

/// Update File ///
document.getElementById('createFileForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const fileName = document.getElementById('fileName').value;
    
    try {
        const userId = window.sessionStorage.getItem('userId');
        
        const response = await fetch(`http://localhost:8000/update/file/${fileId}`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${userId}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: fileName,
                userid: userId,
                path: fileName,
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
            alert(`✅ File "${data.name || fileName}" updated successfully!`);
            window.location.href = '../../../fileService.html';
            return;
        }

        let errorMessage = "❌ Unknown error";

        if (response.status === 404) {
            errorMessage = "❌ 404 - Endpoint not found!\n\nMake sure your backend is running on http://localhost:8000 and has the update file route.";
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