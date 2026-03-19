const username = window.sessionStorage.getItem("username");
const userId = window.sessionStorage.getItem("userId");

if (!username || !userId) {
    alert("⚠️ You haven't logged in yet!");
    window.location.href = "login.html";
}

document.getElementById("username").textContent = window.sessionStorage.getItem("username");

let allGroups = [];
let allProjects = [];
let currentGroup = null;
let currentSelectedProject = null;

/// Logout ///
function logout() {
    const confirmLogout = confirm(`Logging out? We will miss you!`);
    
    if (confirmLogout) {
        window.sessionStorage.removeItem("userId");
        window.sessionStorage.removeItem("username");
        
        window.location.href = "../../0-home/home.html";
    }
}

/// Fetch All Groups ///
async function fetchGroups() {
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
        
        if (response.ok && data.groups) {
            allGroups = data.groups;
            return true;
        } else {
            console.error("❌ Failed to load groups: ", data);
            return false;
        }
    } catch (error) {
        console.error("❌ Network/Server Error: ", error);
        return false;
    }
}

/// Fetch All Projects ///
async function fetchProjects() {
    try {
        const userId = window.sessionStorage.getItem('userId');
        
        const response = await fetch("http://localhost:8000/list/projects", {
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

/// Delete Project ///
async function deleteProject(projectId) {
    try {
        const userId = window.sessionStorage.getItem('userId');
        const project = allProjects.find(p => p.id === projectId);
        
        if (!project) {
            alert("⚠️ Project not found.");
            return;
        }
        
        // Check if project has any folders
        const checkFoldersResponse = await fetch(`http://localhost:8000/list/folders/${projectId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${userId}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (checkFoldersResponse.ok) {
            const foldersData = await checkFoldersResponse.json();
            const projectFolders = Array.isArray(foldersData) ? foldersData : [];
            
            if (projectFolders.length > 0) {
                alert(
                    `❌ Cannot delete project "${project.name}"!\n\n` +
                    `This project has ${projectFolders.length} folder(s).\n` +
                    `Please delete all folders in this project first before deleting the project.`
                );
                return;
            }
        }
        
        // Proceed with deletion if no folders found
        const response = await fetch(`http://localhost:8000/delete/project/${projectId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${userId}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok || response.status === 204) {
            alert('✅ Project deleted successfully!');
            
            // If the deleted project was selected, clear the details
            if (currentSelectedProject && currentSelectedProject.id === projectId) {
                currentSelectedProject = null;
                
                // Go back to the projects list view for the current group
                if (currentGroup) {
                    await fetchProjects();
                    displayProjects(currentGroup);
                } else {
                    await fetchProjects();
                    displayGroups();
                }
            } else {
                // Reload the current view
                await fetchProjects();
                if (currentGroup) {
                    displayProjects(currentGroup);
                } else {
                    displayGroups();
                }
            }
        } else {
            const data = await response.json();
            alert(`❌ Failed to delete project: ${data.detail || 'Unknown error'}`);
        }

    } catch (error) {
        console.error("❌ Network/Server Error: ", error);
        alert("⚠️ Unable to connect to the server.");
    }
}

/// Get Projects Count by Group ///
function getProjectCountByGroup(groupId) {
    return allProjects.filter(project => project.groupId === groupId).length;
}

/// Get Projects by Group ///
function getProjectsByGroup(groupId) {
    return allProjects.filter(project => project.groupId === groupId);
}

/// Display Groups List ///
function displayGroups() {
    const container = document.getElementById('mainContentContainer');
    const pathDisplay = document.getElementById('pathDisplay');
    
    pathDisplay.textContent = 'Project Service';
    currentGroup = null;
    currentSelectedProject = null;
    
    if (allGroups.length === 0) {
        container.innerHTML = `
            <div class="groups">
                <div class="loading">No groups found</div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = '<div class="groups" id="groupsContainer"></div>';
    const groupsContainer = document.getElementById('groupsContainer');
    
    allGroups.forEach(group => {
        const projectCount = getProjectCountByGroup(group.id);
        
        const groupDiv = document.createElement('div');
        groupDiv.className = 'group';
        groupDiv.onclick = () => displayProjects(group);
        
        groupDiv.innerHTML = `
            <div class="groupLabel">
                <div><i class="fa-solid fa-users"></i> Group Name: ${group.name}</div>
                <div class="groupIdLabel"><i class="fa-solid fa-key"></i> Group Id: ${group.id}</div>
            </div>
            
            <div class="projectNumbers">${projectCount} ${projectCount === 0 || projectCount === 1 ? 'Project' : 'Projects'}</div>
        `;
        
        groupsContainer.appendChild(groupDiv);
    });
}

/// Display Projects for a Group ///
function displayProjects(group) {
    const container = document.getElementById('mainContentContainer');
    const pathDisplay = document.getElementById('pathDisplay');
    
    currentGroup = group;
    currentSelectedProject = null;
    
    pathDisplay.innerHTML = `
        <div style="display: flex; flex-direction: row; align-items: center; gap: 10px">
            <div class="pathSelect" onclick="displayGroups()">
                Project Service
            </div>
            <div>></div>
            <div style="font-weight: bold">${group.name}</div>
        </div>
    `;
    
    const projects = getProjectsByGroup(group.id);
    
    if (projects.length === 0) {
        container.innerHTML = `
            <div class="projects">
                <div style="color: white; text-align: center; padding: 20px;">
                    No projects in this group yet
                </div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = '<div class="projects" id="projectsContainer"></div>';
    const projectsContainer = document.getElementById('projectsContainer');
    
    projects.forEach(project => {
        const projectDiv = document.createElement('div');
        projectDiv.className = 'project';
        projectDiv.setAttribute('projectId', project.id);
        projectDiv.onclick = () => selectProject(project, group);
        
        projectDiv.innerHTML = `
            <div class="projectLabel">
                <div><i class="fa-solid fa-pen-to-square"></i> Project Name: ${project.name}</div>
                <div class="projectIdLabel"><i class="fa-solid fa-key"></i> Project Id: ${project.id}</div>
            </div>
            <div class="project-group">
                Belongs to: Group "${group.name}" - Id: ${project.groupId}
            </div>
        `;
        
        projectsContainer.appendChild(projectDiv);
    });
}

/// Select Project ///
function selectProject(project, group) {
    currentSelectedProject = project;
    
    // Update active state
    document.querySelectorAll('.project').forEach(p => {
        p.classList.remove('active');
    });
    
    const selectedProjectEl = document.querySelector(`[projectId="${project.id}"]`);
    if (selectedProjectEl) {
        selectedProjectEl.classList.add('active');
    }
    
    displayProjectDetails(project, group);
}

/// Display Project Details ///
function displayProjectDetails(project, group) {
    const container = document.getElementById('mainContentContainer');
    const pathDisplay = document.getElementById('pathDisplay');
    
    // Store projectId in sessionStorage for update page
    window.sessionStorage.setItem("projectId", project.id);
    
    pathDisplay.innerHTML = `
        <div style="display: flex; flex-direction: row; align-items: center; gap: 10px">
            <div class="pathSelect" onclick="displayGroups()">
                Project Service
            </div>
            <div>></div>
            <div class="pathSelect" onclick="displayProjects(allGroups.find(g => g.id === ${group.id}))">
                ${group.name}
            </div>
            <div>></div>
            <div style="font-weight: bold">${project.name}</div>
        </div>
    `;
    
    container.innerHTML = `
        <div class="projectDetails">
            <div class="details">
                <label>Project Id: <label class="value">${project.id}</label></label>
                
                <label>Project Name: <label class="value">${project.name}</label></label>
                
                <label>Group Id: <label class="value">${project.groupId}</label></label>
            </div>
            
            <div class="projectActions">
                <div class="updateProject" onclick="window.location.href='forms/2-updateProject/updateProject.html'">
                    <i class="fa-solid fa-pen-to-square"></i> Update Project
                </div>
                
                <div class="deleteProject" onclick="handleDeleteClick(${project.id}, '${project.name.replace(/'/g, "\\'")}')">
                    <i class="fa-solid fa-trash-can"></i> Delete Project
                </div>
            </div>
        </div>
    `;
}

/// Handle Delete Button Click ///
function handleDeleteClick(projectId, projectName) {
    const confirmDelete = confirm(
        `Are you sure you want to delete "${projectName}"?\n` +
        `This will also delete all folders in this project.\n` +
        `This action cannot be undone!`
    );
    
    if (confirmDelete) {
        deleteProject(projectId);
    }
}

/// Initialize Page ///
async function initializePage() {
    const groupsSuccess = await fetchGroups();
    const projectsSuccess = await fetchProjects();
    
    if (groupsSuccess && projectsSuccess) {
        displayGroups();
    } else {
        document.getElementById('mainContentContainer').innerHTML = `
            <div class="groups">
                <div class="loading">Failed to load data</div>
            </div>
        `;
    }
}

/// Load data when page loads ///
initializePage();