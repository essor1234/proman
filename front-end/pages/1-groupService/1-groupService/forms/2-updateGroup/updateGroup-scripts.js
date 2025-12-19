/// 🚧 Check login status IMMEDIATELY ///
const token = window.sessionStorage.getItem("token");

if (!token) {
    alert("❌ You haven't logged in yet!");
    window.location.href='/1-groupService/0-login/groupService-login.html';
}

/// Load group data when page loads ///
window.addEventListener('DOMContentLoaded', async function() {
    const groupId = window.sessionStorage.getItem('groupId');
    const loadingMessage = document.getElementById('loadingMessage');
    const submitButton = document.getElementById('submitButton');
    
    if (!groupId) {
        alert("❌ No group selected! Please select a group first.");
        window.location.href = '../groupService.html';
        return;
    }
    
    // Set the group ID in the readonly field
    document.getElementById('groupId').value = groupId;
    
    // Fetch group details
    try {
        const response = await fetch(`http://localhost:8000/read/group/${groupId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const group = await response.json();
            
            // Fill in the form fields
            document.getElementById('groupNameInput').value = group.name || '';
            document.getElementById('groupDescriptionInput').value = group.description || '';
            
            // Set the correct radio button
            const visibilityRadio = document.querySelector(`input[name="groupTypeInput"][value="${group.visibility}"]`);
            if (visibilityRadio) {
                visibilityRadio.checked = true;
            }
            
            // Hide loading message and enable submit button
            loadingMessage.style.display = 'none';
            submitButton.disabled = false;
            
            console.log("✅ Group data loaded successfully:", group);
        } else {
            const data = await response.json();
            loadingMessage.textContent = `Failed to load group data: ${data.detail || 'Unknown error'}`;
            loadingMessage.style.color = 'red';
            alert(`❌ Failed to load group data: ${data.detail || 'Unknown error'}`);
            
            // Redirect back after 2 seconds
            setTimeout(() => {
                window.location.href = '../groupService.html';
            }, 2000);
        }
    } catch (error) {
        console.error("❌ Error loading group:", error);
        loadingMessage.textContent = 'Unable to load group data. Redirecting...';
        loadingMessage.style.color = 'red';
        alert("⚠️ Unable to load group data. Please try again.");
        
        // Redirect back after 2 seconds
        setTimeout(() => {
            window.location.href = '../../groupService.html';
        }, 2000);
    }
});

/// Update Group ///
document.getElementById('updateGroupForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const groupId = document.getElementById('groupId').value;
    const groupNameInput = document.getElementById('groupNameInput').value;
    const groupDescriptionInput = document.getElementById('groupDescriptionInput').value;
    const groupTypeInput = document.querySelector('input[name="groupTypeInput"]:checked').value;
    const submitButton = document.getElementById('submitButton');

    // Disable button during submission
    submitButton.disabled = true;
    submitButton.textContent = 'Updating...';

    try {
        const response = await fetch(`http://localhost:8000/update/group/${groupId}`, {
            method: 'PUT',
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
        console.log("📦 Response:", data);

        if (response.ok) {
            alert(`✅ Group "${data.name}" has been successfully updated!`);
            
            // Update session storage with new name
            window.sessionStorage.setItem("groupName", data.name);
            
            window.location.href = '../../groupService.html';
        } else {
            let errorMessage = "❌ Failed to update group.";

            if (Array.isArray(data)) {
                errorMessage = data.map(err => err.msg).join(", ");
            } else if (data.detail) {
                errorMessage = data.detail;
            }

            alert(`❌ ${errorMessage}`);
            
            // Re-enable button
            submitButton.disabled = false;
            submitButton.textContent = 'Update Group';
        }

    } catch (error) {
        console.error("❌ Network/Server Error:", error);
        alert("⚠️ Unable to connect to the server.");
        
        // Re-enable button
        submitButton.disabled = false;
        submitButton.textContent = 'Update Group';
    }
});