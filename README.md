# 🚀 Microservices Project

A scalable microservices-based application with separate services for account management, project management, group management, and file/folder operations, all orchestrated through an API gateway.

---

## 📁 Project Structure

```
D:.
├── docker-compose.yaml
├── README.md
├── requirements.txt
│
├── front-end/
│
└── server/
    ├── account_management_service/
    ├── folder_and_file_management_service/
    ├── group_service/
    ├── project_service/
    └── gate_way/
```

---

## 🎯 Service Mission & Responsibilities

### 🌐 **gateway (API Gateway)**
**Mission:** Acts as the single entry point for all client requests. Routes incoming requests to appropriate microservices and handles cross-cutting concerns.

**Responsibilities:**
- Request routing and load balancing
- API composition and aggregation
- Authentication/Authorization validation
- Rate limiting and request throttling
- API versioning management

**Directory Structure:**
```
gate_way/
├── DockerFile
├── requirements.txt
└── app/
    ├── main.py
    ├── controllers/
    ├── routes/
    └── utils/
```

---

### 👤 **account_management_service**
**Mission:** Manages all user-related operations including authentication, authorization, and user profile management.

**Responsibilities:**
- User registration and login
- Password hashing and authentication 
- JWT token generation and validation (Not yet)
- User profile CRUD operations
- Role and permission management (Not yet)
- Session management

**Directory Structure:**
```
account_management_service/
├── DockerFile
├── requirements.txt
└── app/
    ├── main.py
    ├── controllers/      # Business logic for account operations
    ├── core/            # Config, middleware, security
    ├── models/          # User database models
    ├── repositories/    # Database queries for users
    ├── routes/          # API endpoints for authentication
    ├── schemas/         # Request/response validation
    └── utils/           # Password hashing, token generation
```

---

### 📂 **folder_and_file_management_service**
**Mission:** Handles all file and folder operations including uploads, downloads, organization, and storage management.

**Responsibilities:**
- File upload and download
- Folder creation and hierarchy management (Not yet)
- File metadata storage and retrieval 
- Storage quota management (Not yet)
- File versioning and access control (Not yet)
- File search and filtering (Not yet)

**Directory Structure:**
```
folder_and_file_management_service/
├── DockerFile
├── requirements.txt
└── app/
    ├── main.py
    ├── controllers/      # File operation handlers
    ├── core/            # Storage configuration
    ├── models/          # File/folder database models
    ├── repositories/    # File metadata queries
    ├── routes/          # File operation endpoints
    ├── schemas/         # File/folder validation schemas
    └── utils/           # File upload, compression utilities
```

---

### 👥 **group_service**
**Mission:** Manages user groups, team collaboration, and group-based permissions.

**Responsibilities:**
- Group creation and management 
- Member invitation and management
- Group roles and permissions (Not yet)
- Group activity tracking (Not yet)
- Access control for group resources
- Group metadata and settings (Not yet)

**Directory Structure:**
```
group_service/
├── DockerFile
├── requirements.txt
└── app/
    ├── main.py
    ├── controllers/      # Group management logic
    ├── core/            # Group-specific config
    ├── models/          # Group and membership models
    ├── repositories/    # Group data access layer
    ├── routes/          # Group API endpoints
    ├── schemas/         # Group validation schemas
    └── utils/           # Group utilities
```

---

### 📊 **project_service**
**Mission:** Handles project lifecycle management including creation, updates, collaboration, and project-specific resources.

**Responsibilities:**
- Project CRUD operations
- Project metadata management (Not yet)
- Project member and role assignment 
- Project status and timeline tracking (Not yet)
- Project-resource associations
- Project search and filtering (Not yet)

**Directory Structure:**
```
project_service/
├── DockerFile
├── requirements.txt
└── app/
    ├── main.py
    ├── controllers/      # Project business logic
    ├── core/            # Project configuration
    ├── models/          # Project database models
    ├── repositories/    # Project data operations
    ├── routes/          # Project API endpoints
    ├── schemas/         # Project validation schemas
    └── utils/           # Project-specific utilities
```

---

## 🗂️ Common Directory Structure Explanation

Each microservice follows a consistent structure:

| Directory | Purpose |
|-----------|---------|
| **controllers/** | Contains business logic and request handlers. Processes data from routes and coordinates with repositories. |
| **core/** | Configuration files, middleware, database connections, and shared utilities. |
| **models/** | Database models (SQLAlchemy/ORM classes) that define the structure of data. |
| **repositories/** | Data access layer that handles all database operations and queries. |
| **routes/** | API endpoint definitions that map HTTP requests to controllers. |
| **schemas/** | Pydantic schemas for request/response validation and serialization. |
| **utils/** | Helper functions and utilities (e.g., file operations, hashing, formatting). |
| **main.py** | Application entry point that initializes the FastAPI app and registers routes. |

---
## Clone Project
```bash
# Step 1: Pick Your DIR to save to project
# Step 2 run cmd in that folder Or head your cmd to that folder
# Step 3: Clone the project
git clone https://github.com/essor1234/proman.git
```
## 🐍 Python Environment Setup

### Step 1: Create a Virtual Environment

#### For Windows:
```bash
# Navigate to project root
cd path/to/project

# Create virtual environment
python -m venv proman

# Activate virtual environment
proman\Scripts\activate
```

#### For macOS/Linux:
```bash
# Navigate to project root
cd path/to/project

# Create virtual environment
python3 -m venv proman

# Activate virtual environment
source proman/bin/activate
```

### Step 2: Install Dependencies

#### Option A: Install for a Single Service
```bash
# Navigate to specific service
cd server/account_management_service

# Install dependencies
pip install -r requirements.txt
```

#### Option B: Install All Service Dependencies
```bash
# From project root
pip install -r server/account_management_service/requirements.txt
pip install -r server/folder_and_file_management_service/requirements.txt
pip install -r server/group_service/requirements.txt
pip install -r server/project_service/requirements.txt
pip install -r server/gate_way/requirements.txt
```

#### Option C: Create Installation Script (Recommended)

Create `install_all.sh` (Linux/macOS) or `install_all.bat` (Windows):

**install_all.sh:**
```bash
#!/bin/bash
pip install -r server/account_management_service/requirements.txt
pip install -r server/folder_and_file_management_service/requirements.txt
pip install -r server/group_service/requirements.txt
pip install -r server/project_service/requirements.txt
pip install -r server/gate_way/requirements.txt
echo "All dependencies installed successfully!"
```

Run with: `bash install_all.sh`

### Step 3: Verify Installation
```bash
pip list
```

---

## 🐳 Running the Project with Docker

### Prerequisites
- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))
- Docker Compose (usually included with Docker Desktop)

### Step 1: Build and Start All Services
```bash
# From project root directory
docker-compose up --build
```

**What this does:**
- Builds Docker images for all services
- Creates containers for each service
- Sets up a shared network for inter-service communication
- Starts all services simultaneously

### Step 2: Run in Detached Mode (Background)
```bash
docker-compose up -d --build
```

### Step 3: View Running Containers
```bash
docker-compose ps
```

### Step 4: View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f gateway
docker-compose logs -f account_service
```

### Step 5: Stop All Services
```bash
# Stop containers (keeps data)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop, remove containers, and delete volumes
docker-compose down -v
```

### Step 6: Rebuild a Specific Service
```bash
docker-compose up -d --build account_service
```

---

## 🔗 Service Endpoints

Once running, services are available at:

| Service | Port | URL |
|---------|------|-----|
| **Gateway** | 8000 | http://localhost:8000 |
| **Account Service** | 8001 | http://localhost:8001 |
| **File Service** | 8002 | http://localhost:8002 |
| **Group Service** | 8003 | http://localhost:8003 |
| **Project Service** | 8004 | http://localhost:8004 |

---

## 📝 Additional Information

### Environment Variables
Create `.env` files for each service to store sensitive configuration:

**Example `.env` structure:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key-here
JWT_EXPIRATION=3600
ALLOWED_ORIGINS=http://localhost:3000
```

**Recommended location:** Place `.env` in each service directory or use a shared `.env` at project root.

### Database Integration
To add a database service to `docker-compose.yaml`:

```yaml
services:
  postgres:
    image: postgres:15-alpine
    container_name: postgres_db
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin123
      POSTGRES_DB: microservices_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

volumes:
  postgres_data:
```

### API Documentation
Each service typically exposes API documentation:
- **Swagger UI:** `http://localhost:PORT/docs`
- **ReDoc:** `http://localhost:PORT/redoc`

### Development vs Production

**Development Mode:**
```bash
# Hot reload enabled
docker-compose -f docker-compose.dev.yaml up
```

**Production Mode:**
```bash
# Optimized builds
docker-compose -f docker-compose.prod.yaml up -d
```

### Testing
```bash
# Run tests for a service
cd server/account_management_service
pytest

# Run with coverage
pytest --cov=app tests/
```

### Common Issues & Solutions

**Issue:** Port already in use
```bash
# Solution: Stop the process using the port or change port in docker-compose.yaml
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # macOS/Linux
```

**Issue:** Docker build fails
```bash
# Solution: Clean Docker cache
docker system prune -a
docker-compose build --no-cache
```

**Issue:** Services can't communicate
```bash
# Solution: Check network configuration
docker network ls
docker network inspect project_app-network
```

### Performance Optimization
- Use `.dockerignore` to exclude unnecessary files from builds
- Implement health checks in `docker-compose.yaml`
- Use multi-stage Docker builds to reduce image size
- Configure resource limits for containers

### Security Best Practices
- Never commit `.env` files to version control
- Use Docker secrets for sensitive data in production
- Implement rate limiting in the gateway
- Regular security updates for base images
- Use non-root users in Docker containers

---

## 🤝 Git Workflow & Collaboration

### 🌳 Branching Strategy

We follow a **feature-based branching model** to keep development organized:

```
main (protected)
│
├── develop
│
├── feature/<member_name>-<feature_name>
├── fix/<member_name>-<bugfix_name>
└── hotfix/<member_name>-<urgent_fix>
```

**Branch Naming Examples:**
- `feature/quy-auth-api` - New authentication API by Quy
- `feature/long-file-upload` - File upload feature by Long
- `fix/nam-login-bug` - Login bug fix by Nam
- `hotfix/minh-security-patch` - Urgent security fix by Minh

---

### 🔒 Protected Branch Rules

The `main` branch is **protected** to ensure stability:

| Rule | Status | Purpose |
|------|--------|---------|
| Direct Push | ❌ Not Allowed | Prevents untested code from reaching production |
| Pull Request Required | ✅ Mandatory | All changes must be reviewed |
| Code Review | ✅ Required (min. 1) | Ensures code quality and knowledge sharing |
| CI/CD Checks | ✅ Must Pass | Automated tests must succeed before merge |

**This ensures `main` is always stable and ready to deploy.**

---

### 📝 Standard Git Workflow

#### 1️⃣ Create Your Feature Branch

```bash
# Start from the latest main
git checkout main
git pull origin main

# If the branch already exist
git checkout feature/yourname-feature-description
## ELSE-------------------------------------------
# Create your feature branch
git checkout -b feature/yourname-feature-description
```


#### 2️⃣ Make Your Changes
```bash
# Make changes to your code
# Stage your changes
git add .

# Commit with a clear message
git commit -m "Add user authentication endpoint"
```

**Commit Message Guidelines:**
- Use present tense: "Add feature" not "Added feature"
- Be descriptive but concise
- Examples:
  - ✅ `Add JWT token validation middleware`
  - ✅ `Fix file upload size limit bug`
  - ✅ `Update user schema with email field`
  - ❌ `Fixed stuff`
  - ❌ `Updates`

#### 3️⃣ Keep Your Branch Updated
Before pushing, sync with the latest changes from `main`:

```bash
# Fetch the latest updates
git fetch origin

# Rebase your branch on top of main
git rebase origin/main

# If conflicts occur, resolve them, then:
git add .
git rebase --continue
```

**Why rebase?** It keeps your commits on top of the latest code, making the history linear and easier to understand.

#### 4️⃣ Push Your Changes
```bash
# First push
git push origin feature/yourname-feature-description

# After rebase (force push)
git push origin feature/yourname-feature-description --force-with-lease
```

⚠️ **Note:** Use `--force-with-lease` instead of `-f` to avoid accidentally overwriting others' work.

---

### 🔀 Pull Request (PR) Process

#### Creating a Pull Request

1. **Push your branch** to GitHub
2. **Navigate to the repository** on GitHub
3. **Click "New Pull Request"**
4. **Fill in the PR template:**

```markdown
## 📋 Description
Brief description of what this PR does

## 🎯 Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Hotfix
- [ ] Documentation update

## ✅ Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] No new warnings generated
- [ ] Tests added/updated (if applicable)

## 🧪 Testing
Describe how you tested your changes

## 📸 Screenshots (if applicable)
Add screenshots for UI changes
```

5. **Request reviewers** (at least 1 team member)
6. **Wait for review approval** and CI checks to pass
7. **Address review comments** if any
8. **Merge** once approved

#### PR Best Practices

| Practice | Description |
|----------|-------------|
| **Keep it small** | One feature per PR. Easier to review and less risky. |
| **Clear title** | Use format: `[Type] Brief description` (e.g., `[Feature] Add file upload endpoint`) |
| **Detailed description** | Explain what, why, and how |
| **Link issues** | Reference related issues: `Closes #123` |
| **Stay responsive** | Respond to review comments promptly |
| **Test thoroughly** | Ensure all tests pass before requesting review |

#### After PR is Merged

Clean up your local and remote branches:

```bash
# Switch back to main
git checkout main

# Pull the latest changes (including your merged PR)
git pull origin main

# Delete local branch
git branch -d feature/yourname-feature-description

# Delete remote branch
git push origin --delete feature/yourname-feature-description
```

---

### 🚨 Handling Conflicts

If you encounter merge conflicts during rebase:

```bash
# 1. See which files have conflicts
git status

# 2. Open conflicting files and resolve conflicts
# Look for conflict markers: <<<<<<<, =======, >>>>>>>

# 3. After resolving, stage the files
git add <resolved-files>

# 4. Continue the rebase
git rebase --continue

# 5. If you want to abort and start over
git rebase --abort
```

---

### 💡 Quick Command Reference

| Action | Command |
|--------|---------|
| Create branch | `git checkout -b feature/name-desc` |
| View branches | `git branch -a` |
| Switch branch | `git checkout branch-name` |
| Update from main | `git fetch origin && git rebase origin/main` |
| Check status | `git status` |
| View commit history | `git log --oneline` |
| Undo last commit (keep changes) | `git reset --soft HEAD~1` |
| Discard local changes | `git checkout -- <file>` |
| View remote URL | `git remote -v` |

---

### 📚 Additional Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Pull Request Guide](https://docs.github.com/en/pull-requests)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Rebase Tutorial](https://www.atlassian.com/git/tutorials/rewriting-history/git-rebase)

---

## 🤝 Contributing

We welcome contributions! Please follow the Git workflow above and ensure:

1. ✅ Your code follows the project's coding standards
2. ✅ All tests pass
3. ✅ Documentation is updated if needed
4. ✅ Commit messages are clear and descriptive
5. ✅ PR has a detailed description

---

## 📄 License

[Add your license information here]

---

## 📧 Contact

[Add your contact information or team details here]
