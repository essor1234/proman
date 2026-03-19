const username = window.sessionStorage.getItem("username");
const userId = window.sessionStorage.getItem("userId");

if (!username || !userId) {
    alert("⚠️ You haven't logged in yet!");
    window.location.href = "../0-login/fileService-login.html";
}

document.getElementById("username").textContent = window.sessionStorage.getItem("username");

let allProjects = [];
let allFiles = [];
let allFolders = [];
let currentProject = null;
let currentSelectedItem = null;
let currentItemType = null; // 'file' or 'folder'

/// Logout ///
function logout() {
    const confirmLogout = confirm('Logging out? We will miss you!');
    
    if (confirmLogout) {
        window.sessionStorage.removeItem("userId");
        window.sessionStorage.removeItem("username");
        window.location.href = "../../0-home/home.html";
    }
}

/// Fetch All Projects ///
async function fetchProjects() {
    try {
        const userId = window.sessionStorage.getItem('userId');
        
        const response = await fetch("http://localhost:8000/list/projects/", {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${userId}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        
        if (response.ok) {
            allProjects = Array.isArray(data) ? data : [];
            return true;
        } else {
            console.error("❌ Failed to load projects: ", data);
            return false;
        }
    } catch (error) {
        console.error("❌ Network/Server Error: ", error);
        return false;
    }
}

/// Fetch Files for a Project ///
async function fetchFiles(projectId) {
    try {
        const userId = window.sessionStorage.getItem('userId');
        
        const response = await fetch(`http://localhost:8000/list/files/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${userId}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        
        if (response.ok) {
            return Array.isArray(data) ? data : [];
        } else {
            console.error("❌ Failed to load files: ", data);
            return [];
        }
    } catch (error) {
        console.error("❌ Network/Server Error: ", error);
        return [];
    }
}

/// Fetch Folders for a Project ///
async function fetchFolders(projectId) {
    try {
        const userId = window.sessionStorage.getItem('userId');
        
        const response = await fetch(`http://localhost:8000/list/folders/${projectId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${userId}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        
        if (response.ok) {
            return Array.isArray(data) ? data : [];
        } else {
            console.error("❌ Failed to load folders: ", data);
            return [];
        }
    } catch (error) {
        console.error("❌ Network/Server Error: ", error);
        return [];
    }
}

/// Delete File ///
async function deleteFile(fileId) {
    try {
        const userId = window.sessionStorage.getItem('userId');
        
        const response = await fetch(`http://localhost:8000/delete/file/${fileId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${userId}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok || response.status === 204) {
            alert('✅ File deleted successfully!');
            
            if (currentProject) {
                await displayFilesAndFolders(currentProject);
            }
        } else {
            const data = await response.json();
            alert(`❌ Failed to delete file: ${data.detail || 'Unknown error'}`);
        }

    } catch (error) {
        console.error("❌ Network/Server Error: ", error);
        alert("⚠️ Unable to connect to the server.");
    }
}

/// Delete Folder ///
async function deleteFolder(folderId, projectId) {
    try {
        const userId = window.sessionStorage.getItem('userId');
        
        const response = await fetch(`http://localhost:8000/delete/folder/project/${projectId}/folder/${folderId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${userId}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok || response.status === 204) {
            alert('✅ Folder deleted successfully!');
            
            if (currentProject) {
                await displayFilesAndFolders(currentProject);
            }
        } else {
            const data = await response.json();
            alert(`❌ Failed to delete folder: ${data.detail || 'Unknown error'}`);
        }

    } catch (error) {
        console.error("❌ Network/Server Error: ", error);
        alert("⚠️ Unable to connect to the server.");
    }
}

/// Display Projects List ///
function displayProjects() {
    const container = document.getElementById('mainContentContainer');
    const pathDisplay = document.getElementById('pathDisplay');
    
    pathDisplay.textContent = 'File Service';
    currentProject = null;
    currentSelectedItem = null;
    
    if (allProjects.length === 0) {
        container.innerHTML = `
            <div class="projects">
                <div class="loading">No projects found</div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = '<div class="projects" id="projectsContainer"></div>';
    const projectsContainer = document.getElementById('projectsContainer');
    
    allProjects.forEach(project => {
        const projectDiv = document.createElement('div');
        projectDiv.className = 'project';
        projectDiv.onclick = () => displayFilesAndFolders(project);
        
        projectDiv.innerHTML = `
            <div class="projectLabel">
                <div><i class="fa-solid fa-pen-to-square"></i> Project Name: ${project.name}</div>
                <div class="projectIdLabel"><i class="fa-solid fa-key"></i> Project Id: ${project.id}</div>
            </div>
        `;
        
        projectsContainer.appendChild(projectDiv);
    });
}

/// Display Files and Folders for a Project ///
async function displayFilesAndFolders(project) {
    const container = document.getElementById('mainContentContainer');
    const pathDisplay = document.getElementById('pathDisplay');
    
    currentProject = project;
    currentSelectedItem = null;
    
    pathDisplay.innerHTML = `
        <div style="display: flex; flex-direction: row; align-items: center; gap: 10px">
            <div class="pathSelect" onclick="displayProjects()">
                File Service
            </div>
            <div>></div>
            <div style="font-weight: bold">${project.name}</div>
        </div>
    `;
    
    // Show loading
    container.innerHTML = `
        <div class="filesAndFolders">
            <div style="color: white; text-align: center; padding: 20px;">
                Loading files and folders...
            </div>
        </div>
    `;
    
    // Fetch files and folders
    const files = await fetchFiles(project.id);
    const folders = await fetchFolders(project.id);
    
    if (files.length === 0 && folders.length === 0) {
        container.innerHTML = `
            <div class="filesAndFolders">
                <div style="color: white; text-align: center; padding: 20px;">
                    No files or folders in this project yet
                </div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = '<div class="filesAndFolders" id="itemsContainer"></div>';
    const itemsContainer = document.getElementById('itemsContainer');
    
    // Display folders first
    folders.forEach(folder => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'item';
        itemDiv.setAttribute('itemId', folder.id);
        itemDiv.setAttribute('itemType', 'folder');
        itemDiv.onclick = () => selectItem(folder, 'folder', project);
        
        itemDiv.innerHTML = `
            <div class="itemLabel">
                <div><i class="fa-solid fa-folder"></i> ${folder.name}</div>
                <div class="itemIdLabel"><i class="fa-solid fa-key"></i> Id: ${folder.id}</div>
            </div>
            <div class="itemType">FOLDER</div>
        `;
        
        itemsContainer.appendChild(itemDiv);
    });
    
    // Then display files
    files.forEach(file => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'item';
        itemDiv.setAttribute('itemId', file.id);
        itemDiv.setAttribute('itemType', 'file');
        itemDiv.onclick = () => selectItem(file, 'file', project);
        
        itemDiv.innerHTML = `
            <div class="itemLabel">
                <div><i class="fa-solid fa-file"></i> ${file.name}</div>
                <div class="itemIdLabel"><i class="fa-solid fa-key"></i> Id: ${file.id}</div>
            </div>
            <div class="itemType">FILE</div>
        `;
        
        itemsContainer.appendChild(itemDiv);
    });
}

/// Select Item (File or Folder) ///
function selectItem(item, type, project) {
    currentSelectedItem = item;
    currentItemType = type;
    
    // Update active state
    document.querySelectorAll('.item').forEach(i => {
        i.classList.remove('selected');
    });
    
    const selectedItemEl = document.querySelector(`[itemId="${item.id}"][itemType="${type}"]`);
    if (selectedItemEl) {
        selectedItemEl.classList.add('selected');
    }
    
    displayItemDetails(item, type, project);
}

/// Display Item Details ///
function displayItemDetails(item, type, project) {
    const container = document.getElementById('mainContentContainer');
    const pathDisplay = document.getElementById('pathDisplay');
    
    const itemName = item.name || 'Unnamed';
    const itemIcon = type === 'folder' ? 'fa-folder' : 'fa-file';
    
    pathDisplay.innerHTML = `
        <div style="display: flex; flex-direction: row; align-items: center; gap: 10px">
            <div class="pathSelect" onclick="displayProjects()">
                File Service
            </div>
            <div>></div>
            <div class="pathSelect" onclick="displayFilesAndFolders(allProjects.find(p => p.id === ${project.id}))">
                ${project.name}
            </div>
            <div>></div>
            <div style="font-weight: bold">${itemName}</div>
        </div>
    `;
    
    let detailsHtml = `
        <label>${type === 'folder' ? 'Folder' : 'File'} Id: <label class="value">${item.id}</label></label>
        <label>${type === 'folder' ? 'Folder' : 'File'} Name: <label class="value">${itemName}</label></label>
        <label>Project Id: <label class="value">${project.id}</label></label>
    `;
    
    // Add file-specific details
    if (type === 'file') {
        if (item.content) {
            detailsHtml += `<label>Content: <label class="value">${item.content}</label></label>`;
        }
        if (item.fileType) {
            detailsHtml += `<label>File Type: <label class="value">${item.fileType}</label></label>`;
        }
    }
    
    // Add folder-specific details
    if (type === 'folder') {
        if (item.description) {
            detailsHtml += `<label>Description: <label class="value">${item.description}</label></label>`;
        }
    }
    
    container.innerHTML = `
        <div class="itemDetails">
            <div class="details">
                ${detailsHtml}
            </div>
            
            <div class="itemActions">
                <div class="updateItem" onclick="updateItem(${item.id}, '${type}', ${project.id})">
                    <i class="fa-solid fa-pen-to-square"></i> Update ${type === 'folder' ? 'Folder' : 'File'}
                </div>
                
                <div class="deleteItem" onclick="handleDeleteClick(${item.id}, '${itemName.replace(/'/g, "\\'")}', '${type}', ${project.id})">
                    <i class="fa-solid fa-trash-can"></i> Delete ${type === 'folder' ? 'Folder' : 'File'}
                </div>
            </div>
        </div>
    `;
}

/// Handle Update Click ///
function updateItem(itemId, type, projectId) {
    window.sessionStorage.setItem(type === 'folder' ? 'folderId' : 'fileId', itemId);
    window.sessionStorage.setItem('projectId', projectId);
    
    if (type === 'folder') {
        window.location.href = 'forms/folder/2-updateFolder/updateFolder.html';
    } else {
        window.location.href = 'forms/file/2-updateFile/updateFile.html';
    }
}

/// Handle Delete Click ///
function handleDeleteClick(itemId, itemName, type, projectId) {
    const confirmDelete = confirm(`Are you sure you want to delete "${itemName}"?`);
    
    if (confirmDelete) {
        if (type === 'folder') {
            deleteFolder(itemId, projectId);
        } else {
            deleteFile(itemId);
        }
    }
}

/// Initialize Page ///
async function initializePage() {
    const projectsSuccess = await fetchProjects();
    
    if (projectsSuccess) {
        displayProjects();
    } else {
        document.getElementById('mainContentContainer').innerHTML = `
            <div class="projects">
                <div class="loading">Failed to load data</div>
            </div>
        `;
    }
}

/// Load data when page loads ///
initializePage();