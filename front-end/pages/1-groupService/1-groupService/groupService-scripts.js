/// 🚧 Check login status IMMEDIATELY ///
const userId   = window.sessionStorage.getItem("userId");
const username = window.sessionStorage.getItem("username");

if (!userId || !username) {
    alert("❌ You haven't logged in yet!");
    window.location.href='../../../0-login/groupService-login.html';
}

/// Logout ///
function logout() {
    const logout = confirm(`Logging out? We'll miss you!`);
    
    if (logout) {
        window.sessionStorage.removeItem("userId");
        window.sessionStorage.removeItem("username");
        
        window.location.href='../../0-home/home.html';
    }
}

/// Display Username ///
document.getElementById("username").textContent = window.sessionStorage.getItem("username");

/// Setup Drag and Drop for Group ///
function setupDragAndDrop(groupElement, groupId) {
    groupElement.setAttribute('draggable', 'true');
    
    // When drag starts
    groupElement.addEventListener('dragstart', (e) => {
        groupElement.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('groupId', groupId);
    });
    
    // When drag ends
    groupElement.addEventListener('dragend', (e) => {
        groupElement.classList.remove('dragging');
    });
}

/// Setup Trash Can Drop Zone ///
const deleteGroupButton = document.getElementById('deleteGroupButton');

deleteGroupButton.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    deleteGroupButton.classList.add('drag-over');
});

deleteGroupButton.addEventListener('dragleave', (e) => {
    deleteGroupButton.classList.remove('drag-over');
});

deleteGroupButton.addEventListener('drop', async (e) => {
    e.preventDefault();
    deleteGroupButton.classList.remove('drag-over');
    
    const groupId = parseInt(e.dataTransfer.getData('groupId'));
    const group = readListAllGroups.find(g => g.id === groupId);
    
    if (group) {
        const confirmDelete = confirm(`⚠️ Are you sure you want to delete group "${group.name}"?\n⚠️ This action cannot be undone.`);
        
        if (confirmDelete) {
            await deleteGroup(groupId);
        }
    }
});

/// List All Groups ///
let readListAllGroups = [];
let currentSelectedGroup = null;

async function listAllGroups() {
    const subButtons = document.getElementById('subButtons');
    
    try {
        const userId = window.sessionStorage.getItem('userId');
        
        const response = await fetch("http://localhost:8000/list/groups", {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${userId}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        console.log("📋 Response: ", data);

        if (response.ok && data.groups) {
            readListAllGroups = data.groups;
            
            if (data.groups.length === 0) {
                subButtons.innerHTML = `
                    <div class="group">
                        No group yet
                    </div>
                `;
            } else {
                subButtons.innerHTML = '';
                
                data.groups.forEach(group => {
                    const groupButton = document.createElement('div');
                    groupButton.className = 'group';
                    groupButton.setAttribute('data-group-id', group.id);
                    groupButton.innerHTML = `${group.name}`;
                    groupButton.onclick = () => selectGroup(group.id);
                    
                    // Setup drag and drop for this group
                    setupDragAndDrop(groupButton, group.id);
                    
                    subButtons.appendChild(groupButton);
                });
            }
        } else {
            subButtons.innerHTML = `
                <div class="group">
                    Load Groups Failed
                </div>
            `;
            console.error("❌ Failed to load groups: ", data);
        }

    } catch (error) {
        console.error("❌ Network/Server Error: ", error);
        subButtons.innerHTML = `<div class="group">Error loading groups</div>`;
    }
}

/// Select group ///
function selectGroup(groupId) {
    document.querySelectorAll('.group').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const selectedGroup = document.querySelector(`[data-group-id="${groupId}"]`);
    if (selectedGroup) {
        selectedGroup.classList.add('active');
    }
    
    const group = readListAllGroups.find(g => g.id === groupId);
    if (group) {
        currentSelectedGroup = group;
        displayGroupDetails(group);
    }
}

/// Format Date ///
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-UK', {
        minute: '2-digit',
        hour: '2-digit',
        
        day: 'numeric',
        month: 'long',
        year: 'numeric',
    });
}

/// Display Group Details ///
function displayGroupDetails(group) {
    const contentDiv = document.getElementById('groupDetails');
    
    const groupTypeIcon = group.visibility === 'public' ? '<i class="fas fa-globe"></i>' : '<i class="fas fa-lock"></i>';
    
    window.sessionStorage.setItem("groupId", group.id)
    window.sessionStorage.setItem("groupName", group.name);

    contentDiv.innerHTML = `
        <div class="groupDetails">
            <div class="groupDetailsLabel">Id: <span class="groupDetailsInformation">${group.id}</span></div>
            
            <div class="groupDetailsLabel">Name: <span class="groupDetailsInformation">${group.name}</span></div>
                
            <div class="groupDetailsLabel">Description: <span class="groupDetailsInformation">${group.description || 'No description'}</span></div>
            
            <div class="groupDetailsLabel">Type: <span class="groupDetailsInformation">${groupTypeIcon} ${group.visibility.charAt(0).toUpperCase() + group.visibility.slice(1)}</span></div>
                
            <div class="groupDetailsLabel">Owner Id: <span class="groupDetailsInformation">${group.owner_id}</span></div>
                
            <div class="groupDetailsLabel">Members: <span class="groupDetailsInformation">${group.member_count}</span></div>
                
            <div class="groupDetailsLabel">Date Created: <span class="groupDetailsInformation">${formatDate(group.created_at)}</span></div>
                
            <div class="groupDetailsLabel">Date Updated: <span class="groupDetailsInformation">${formatDate(group.updated_at)}</span></div>

            <div style="display: flex; flex-direction: row; gap: 10px; margin-top: 10px;">
                <div class="updateGroupButton" onclick="window.location.href='forms/2-updateGroup/updateGroup.html'">
                    Update Group
                </div>
            </div>
        </div>
    `;
}

/// Delete Group ///
async function deleteGroup(groupId) {
    try {
        const userId = window.sessionStorage.getItem('userId');
        const group = readListAllGroups.find(g => g.id === groupId);
        
        if (!group) {
            alert("⚠️ Group not found.");
            return;
        }
        
        // Check if group has any projects
        const checkProjectsResponse = await fetch("http://localhost:8000/list/projects", {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${userId}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (checkProjectsResponse.ok) {
            const projectsData = await checkProjectsResponse.json();
            const allProjects = Array.isArray(projectsData) ? projectsData : [];
            
            // Filter projects that belong to this group
            const groupProjects = allProjects.filter(project => project.groupId === groupId);
            
            if (groupProjects.length > 0) {
                alert(
                    `❌ Cannot delete group "${group.name}"!\n\n` +
                    `This group has ${groupProjects.length} project(s).\n` +
                    `Please delete all projects in this group first before deleting the group.`
                );
                return;
            }
        }
        
        // Proceed with deletion if no projects found
        const response = await fetch(`http://localhost:8000/delete/group/${groupId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${userId}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok || response.status === 204) {
            alert(`✅ Group "${group.name}" has been successfully deleted.`);
            
            // If the deleted group was selected, clear the details
            if (currentSelectedGroup && currentSelectedGroup.id === groupId) {
                currentSelectedGroup = null;
                const contentDiv = document.getElementById('groupDetails');
                contentDiv.innerHTML = `
                    <div class="noGroupSelect">
                        Select a group to view its information.
                    </div>
                `;
            }
            
            // Reload the groups list
            await listAllGroups();
        } else {
            const data = await response.json();
            alert(`❌ Failed to delete group: ${data.detail || 'Unknown error'}`);
        }

    } catch (error) {
        console.error("❌ Network/Server Error: ", error);
        alert("⚠️ Unable to connect to the server.");
    }
}

/// Click on Trash Can Button to Delete Currently Selected Group ///
deleteGroupButton.addEventListener('click', async () => {
    if (!currentSelectedGroup) {
        alert("⚠️ Please select a group to delete.");
        return;
    }

    const confirmDelete = confirm(
        `⚠️ Are you sure you want to delete group "${currentSelectedGroup.name}"?\n` +
        `⚠️ This action cannot be undone!`
    );

    if (confirmDelete) {
        await deleteGroup(currentSelectedGroup.id);
    }
});

/// List All Groups When Page Loads ///
listAllGroups();