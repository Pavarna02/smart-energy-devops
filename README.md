# ⚡ Smart Energy Monitoring System
## Complete DevOps Project

---

## 1. Project Architecture

```
Internet / Users
      │
      ▼
┌─────────────────────────────────────────────────────┐
│                  KUBERNETES CLUSTER                  │
│                                                      │
│  ┌──────────────┐   HPA (2–6 pods)                  │
│  │  LoadBalancer│──► Deployment: smart-energy-backend│
│  │   Service    │    ┌──────┐ ┌──────┐ ┌──────┐    │
│  └──────────────┘    │ Pod  │ │ Pod  │ │ Pod  │    │
│                      └──────┘ └──────┘ └──────┘    │
└─────────────────────────────────────────────────────┘
         ▲
         │  kubectl apply
         │
┌────────────────────────────────────────────────────┐
│              CI/CD: JENKINS PIPELINE               │
│  Checkout → Build → Test → Docker Build → Push     │
│             → Deploy to K8s                        │
└────────────────────────────────────────────────────┘
         ▲
         │  git push
         │
┌────────────────────────────────────────────────────┐
│                  GIT REPOSITORY                    │
│  main ←── dev ←── feature/xyz                     │
└────────────────────────────────────────────────────┘
         ▲
         │  ansible-playbook
         │
┌────────────────────────────────────────────────────┐
│         ANSIBLE – INFRASTRUCTURE SETUP             │
│  Installs: Docker, Jenkins, kubectl on Ubuntu VM   │
└────────────────────────────────────────────────────┘
```

---

## 2. Folder Structure

```
smart-energy/
├── backend/
│   ├── app.py              ← Flask API (IoT simulation)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/
│       └── test_app.py
├── frontend/
│   └── index.html          ← Dashboard (vanilla HTML/JS/Chart.js)
├── k8s/
│   ├── namespace.yaml
│   ├── deployment.yaml     ← 2 replicas + self-healing probes
│   ├── service.yaml        ← LoadBalancer
│   └── hpa.yaml            ← Auto-scale 2→6 pods
├── ansible/
│   ├── setup.yml           ← Install Docker/Jenkins/kubectl
│   └── inventory.ini
├── docker-compose.yml      ← Local development stack
├── Jenkinsfile             ← CI/CD pipeline definition
└── README.md
```

---

## 3. Git Workflow

### Initial setup
```bash
git init smart-energy
cd smart-energy
git checkout -b main
git add .
git commit -m "feat: initial project scaffold"

# Push to GitHub/GitLab
git remote add origin https://github.com/YOU/smart-energy.git
git push -u origin main
```

### Feature development workflow
```bash
# Always branch off dev
git checkout main
git checkout -b dev
git push -u origin dev

# Create a feature branch
git checkout dev
git checkout -b feature/flask-api
# ... write code ...
git add backend/app.py backend/requirements.txt
git commit -m "feat(backend): add Flask energy simulation API"
git push origin feature/flask-api

# Merge feature → dev (via Pull Request or directly)
git checkout dev
git merge --no-ff feature/flask-api
git push origin dev

# After testing, merge dev → main
git checkout main
git merge --no-ff dev
git tag -a v1.0.0 -m "Release v1.0.0 – initial deployment"
git push origin main --tags
```

### Useful git commands
```bash
git log --oneline --graph --all   # Visual branch history
git stash                          # Save uncommitted work temporarily
git stash pop                      # Restore stashed work
git diff dev main                 # Compare branches
```

---

## 4. Run Locally (Docker Compose)

### Prerequisites
- Docker Desktop (Mac/Windows) or Docker Engine (Linux)
- Git

```bash
# 1. Clone the repo
git clone https://github.com/YOU/smart-energy.git
cd smart-energy

# 2. Start all containers
docker-compose up --build

# 3. Access the app
#    Dashboard → http://localhost:8080
#    API       → http://localhost:5000/api/readings
#    Health    → http://localhost:5000/health

# 4. Stop containers
docker-compose down
```

---

## 5. Run Tests

```bash
cd backend
pip install -r requirements.txt pytest
pytest tests/ -v
```

---

## 6. Infrastructure Setup (Ansible)

### Prerequisites
- Ubuntu 22.04 server (AWS EC2 / GCP VM / local VM)
- Ansible installed on your laptop: `pip install ansible`

```bash
cd ansible

# Edit inventory.ini and set YOUR_SERVER_IP

# Test connectivity first
ansible -i inventory.ini devops_servers -m ping

# Run the full setup playbook
ansible-playbook -i inventory.ini setup.yml

# Access Jenkins at http://YOUR_SERVER_IP:8080
# Get initial admin password:
ssh ubuntu@YOUR_SERVER_IP "sudo cat /var/lib/jenkins/secrets/initialAdminPassword"
```

---

## 7. Kubernetes Deployment

### Prerequisites
- `kubectl` installed
- A running cluster (minikube, EKS, GKE, AKS)

```bash
# Create namespace and deploy everything
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/

# Check status
kubectl get pods -n smart-energy
kubectl get svc  -n smart-energy
kubectl get hpa  -n smart-energy

# Follow logs
kubectl logs -f deployment/smart-energy-backend -n smart-energy

# Minikube only – get the service URL
minikube service smart-energy-backend -n smart-energy
```

---

## 8. Jenkins CI/CD Setup

1. Open Jenkins at `http://YOUR_SERVER:8080`
2. Install suggested plugins + **Docker Pipeline** + **Kubernetes CLI**
3. Add credentials:
   - ID `dockerhub-creds` → Docker Hub username/password
   - ID `kubeconfig`       → Secret File (your `~/.kube/config`)
4. Create a **Pipeline** job → point to your Git repo → select `Jenkinsfile`
5. Enable **GitHub webhook** or poll SCM every 5 minutes
6. Push code → pipeline runs automatically ✅

---

## 9. Cloud Deployment (AWS)

```bash
# 1. Provision EC2 (t3.medium) – Ansible does the rest
ansible-playbook -i ansible/inventory.ini ansible/setup.yml

# 2. Create EKS cluster
eksctl create cluster --name smart-energy --region us-east-1 --nodes 2

# 3. Point kubectl to EKS
aws eks update-kubeconfig --name smart-energy --region us-east-1

# 4. Deploy
kubectl apply -f k8s/

# 5. Get external IP (wait ~2 min for cloud LB)
kubectl get svc smart-energy-backend -n smart-energy
```

---

## API Reference

| Method | Endpoint         | Description                  |
|--------|-----------------|------------------------------|
| GET    | /health          | Health check (K8s probe)     |
| GET    | /api/latest      | Most recent sensor reading   |
| GET    | /api/readings    | Last N readings (?limit=20)  |
| GET    | /api/summary     | Aggregated stats             |

---

## DevOps Checklist

- [x] Git branching: main / dev / feature branches
- [x] CI/CD: Jenkins pipeline with 6 stages
- [x] Docker: multi-stage Dockerfile, Docker Compose
- [x] Kubernetes: Deployment, Service, HPA, self-healing probes
- [x] Ansible: automated infrastructure setup playbook
- [x] IoT simulation: voltage, current, power usage
- [x] Web dashboard: real-time charts
- [x] Unit tests: pytest test suite
