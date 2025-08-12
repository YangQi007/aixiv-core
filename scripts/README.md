# AIXIV Scripts Directory

This directory contains utility scripts for the AIXIV project.

## 🚨 **FOR NEW DEVELOPERS: READ THIS FIRST**

### **🎯 START HERE: Use Docker Compose (ONLY)**

```bash
# Start everything (database + API)
docker compose up

# Stop everything  
docker compose down
```

**This is the ONLY method you need for normal development.**
**Don't use the scripts below unless specifically instructed.**

---

## 🚀 **Available Scripts**

### **Primary Development Method (USE THIS)**

#### `docker compose up` - Start Everything with Docker
```bash
# Start everything (database + API)
docker compose up

# Stop everything
docker compose down

# Start only database
docker compose up db
```

**What it does:**
- Starts PostgreSQL database container
- Builds and runs API container
- Runs database migrations automatically
- Everything in isolated containers

**Use when:** **Normal development (USE THIS)**

---

### **Advanced/Backup Scripts (IGNORE UNLESS NEEDED)**

#### `start.sh` - Native Python Alternative (ADVANCED USERS ONLY)
```bash
./scripts/start.sh
```

**⚠️  WARNING: This is NOT for new developers!**
**⚠️  Only use if Docker is broken and you know what you're doing**

**What it does:**
- Sets up Python virtual environment
- Installs dependencies manually
- Runs database migrations
- Starts FastAPI server with uvicorn

**Use when:** 
- **Docker troubleshooting** (advanced users only)
- Performance debugging (advanced users only)
- **NOT for normal development**

**Prerequisites:**
- Database must be running separately
- Python 3.11+ installed locally
- Advanced Python knowledge

---

#### `run_tests.sh` - Run Test Suite
```bash
./scripts/run_tests.sh
```

**What it does:**
- Runs all tests with pytest
- Supports various options (verbose, coverage, keyword filtering)

**Options:**
- `-v` - Verbose output
- `-c` - With coverage report
- `-k <keyword>` - Run tests matching keyword
- `-h` - Show help

**Use when:** Testing code changes, CI/CD, quality assurance

---

### **Environment & Deployment Scripts**

#### `setup-env.sh` - Environment Configuration
```bash
./scripts/setup-env.sh
```

**What it does:**
- Interactive environment setup
- Configures database URLs for local vs production
- Creates/updates `.env` file

**Use when:** First-time setup, switching between environments

---

#### `deploy.sh` - Manual Deployment Script
```bash
./scripts/deploy.sh
```

**What it does:**
- Builds production Docker image locally
- Pushes to ECR
- Deploys to ECS
- Updates infrastructure

**Use when:** 
- Manual deployment (not automatic)
- Testing deployment process
- Deploying specific versions
- Emergency deployments
- Non-main branch deployments

---

## 🚀 **Deployment Systems**

### **Two Deployment Options Available:**

#### **1. Manual Deployment (This Script)**
```bash
./scripts/deploy.sh
```
- **Control**: You decide when to deploy
- **Use case**: Testing, specific versions, emergency fixes
- **Timing**: On-demand deployment

#### **2. Automatic Deployment (GitHub Actions)**
- **Control**: Automatically deploys on every push to main
- **Use case**: Production deployments, continuous delivery
- **Timing**: Automatic on code changes

**Both systems deploy to the same AWS infrastructure.**
**Choose based on your needs: manual control vs automatic reliability.**

---

## 📋 **Development Workflows**

### **🎯 NEW DEVELOPERS: Use This (ONLY)**

```bash
# 1. Clone the repository
git clone <repository-url>
cd aixiv-core

# 2. Start everything
docker compose up

# 3. Your backend is running at http://localhost:8000
# 4. API docs at http://localhost:8000/docs

# 5. Stop when done
docker compose down
```

### **🧪 Testing (Works with Docker Compose)**

```bash
# Run all tests
./scripts/run_tests.sh

# Run with coverage
./scripts/run_tests.sh -c

# Run specific tests
./scripts/run_tests.sh -k health
```

### **🚀 Production Deployment**

```bash
# Deploy to AWS
./scripts/deploy.sh
```

## 🔧 **Prerequisites**

- **Docker** and **Docker Compose** (for development)
- **Python 3.11+** (only needed for advanced scripts)
- **AWS CLI** configured (for deployment)
- **Terraform** (for infrastructure)

## 📝 **Important Notes for New Developers**

- **🚨 USE DOCKER COMPOSE ONLY** for development
- **🚨 IGNORE the scripts below** unless specifically told to use them
- **🚨 Don't try to be clever** - stick to the recommended method
- All scripts should be run from the **project root directory**
- If something breaks, ask for help before trying alternatives

## 🆘 **Troubleshooting for New Developers**

If you encounter issues:
1. **First**: Try `docker compose down && docker compose up` (restart)
2. **Second**: Check if Docker is running
3. **Third**: Ask for help - don't try advanced scripts
4. **Never**: Try to run `start.sh` unless specifically instructed

## 🎯 **Summary for New Developers**

**START HERE:**
```bash
docker compose up
```

**STOP HERE:**
```bash
docker compose down
```

**Everything else is advanced/backup - ignore it until you're experienced.** 