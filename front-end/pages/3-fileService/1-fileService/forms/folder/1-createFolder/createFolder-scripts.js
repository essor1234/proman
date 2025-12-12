/// 🚧 Check login status IMMEDIATELY ///
const username = window.sessionStorage.getItem("username");
const userId = window.sessionStorage.getItem("userId");

if (!username || !userId) {
    alert("❌ You haven't logged in yet!");
    window.location.href = "../../../../0-login/fileService-login.html";
}

/// Create File ///
document.getElementById('createFolderForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const projectId = document.getElementById('projectId').value;
    const folderName = document.getElementById('folderName').value;
    
    try {
        const userId = window.sessionStorage.getItem('userId');
        
        const response = await fetch(`http://localhost:8000/create/folder/${projectId}`, {
            method: 'POST',
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

        // Always log raw info first
        console.log("Status:", response.status, response.statusText);
        console.log("URL:", response.url);

        let data;
        const contentType = response.headers.get("content-type");

        // Try to parse JSON only if server actually sent JSON
        if (contentType && contentType.includes("application/json")) {
            data = await response.json();
        } else {
            // Server returned HTML (very common on 404/500 in FastAPI debug mode)
            const text = await response.text();
            console.log("Non-JSON response body:", text.substring(0, 500));
            data = { detail: `Server returned ${response.status} ${response.statusText}` };
            if (response.status === 404) data.detail += " → Route '/files' not found! Check backend URL and server status.";
            if (response.status === 401) data.detail += " → Unauthorized. Your userId token might be invalid.";
        }

        // Now handle based on status
        if (response.ok) {
            alert(`✅ File "${data.name || folderName}" created successfully!`);
            window.location.href = '../../../fileService.html';
            return;
        }

        // Error cases
        let errorMessage = "❌ Unknown error";

        if (response.status === 404) {
            errorMessage = "❌ 404 - Endpoint not found!\n\nMake sure your backend is running on http://localhost:8000 and has a POST /files route.";
        } else if (response.status === 401) {
            errorMessage = "❌ 401 - Unauthorized\n\nYour session might have expired. Try logging in again.";
        } else if (response.status === 422) {
            // Validation errors (FastAPI returns array)
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