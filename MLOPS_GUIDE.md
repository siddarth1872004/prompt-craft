# prompt-craft: MLOps and Deployment Guide

This document provides a beginner-friendly explanation of how the **prompt-craft** application works, how it is packaged using Docker, and how it is deployed automatically to AWS using GitHub Actions.

---

## 1. How prompt-craft Works (The Workbench Flow)

PromptCraft is an interactive prompt engineering and security audit workbench. It helps developers write robust LLM instructions by scoring prompt quality, running vulnerability scans (jailbreak/leakage detection), generating few-shot examples automatically, and benchmarking output token counts and latencies across models.

### The System Architecture Flow:
```mermaid
graph TD
    User[1. Developer] -->|Raw Prompt Draft| UI[2. Streamlit Workbench]
    UI -->|Evaluate System Prompts| Audit[3. Security Auditor Engine]
    Audit -->|Pattern Match Outliers| Heuristics[4. Vulnerability Scanners]
    UI -->|Few-Shot Objective| Optimizer[5. Optimization Engine]
    Optimizer -->|Assemble API Request| Gemini[6. Google Gemini Client]
    Gemini -->|Streamed Prompt Suggestions| UI
    UI -->|Benchmark Tests| Suite[7. Assertions Suite]
    Suite -->|Save Run History| S3[8. S3 Storage Bucket]
```

---

## 2. Code Structure

PromptCraft is built entirely around Python and Streamlit, making it dynamic and visual.

```text
prompt-craft/
├── app.py                  # Main Streamlit web application dashboard
├── client.py               # Google Gemini client and streaming wrapper
├── prompt_analyzer.py      # Security scanners (regex/injection checks)
├── test_utils.py           # Automated test assertions evaluator
├── config.py               # Settings & API key loaders
├── Dockerfile              # Streamlit container configuration
└── requirements.txt        # Package dependencies (streamlit, google-genai)
```

---

## 3. The Docker Blueprint (How We Containerize)

We use a simple and lightweight Docker container configured specifically to run Streamlit on port `8000`:

```mermaid
graph LR
    Base[Python 3.11 Image] --> Install[Install Packages - streamlit, google-genai]
    Install --> CopyCode[Copy prompt engineering files]
    CopyCode --> Expose[Expose Port 8000]
    Expose --> Run[Start Streamlit Server on Port 8000]
```

### Why we do this:
* **Streamlit Configuration:** By default, Streamlit runs on port `8501`. We use the flag `--server.port 8000` inside our Dockerfile CMD to map it to port `8000` so that it conforms to our EC2 firewall standards.
* **Direct UI Loading:** The container runs the frontend process directly. You do not need a separate backend server because Streamlit binds the Python logic directly to the web interface.

---

## 4. The GitHub Actions CD Pipeline (Continuous Deployment)

When you run `git push origin main`, GitHub starts a temporary virtual machine to execute the assembly line defined in `.github/workflows/deploy.yml`:

```mermaid
sequenceDiagram
    autonumber
    participant Local as Your Local Computer
    participant GH as GitHub Actions VM
    participant ECR as AWS ECR Registry
    participant EC2 as AWS EC2 Server

    Local->>GH: git push origin main
    Note over GH: Loads secrets: AWS keys, IP, Instance ID
    GH->>GH: Build Docker image (Streamlit environment configuration)
    GH->>ECR: Login & Push image to 'promptcraft' repo
    GH->>EC2: Send SSH public key (EC2 Instance Connect)
    GH->>EC2: SSH into instance and run deployment script
    Note over EC2: 1. Pull latest image from ECR<br/>2. Stop old prompt-craft container<br/>3. Start new container on Port 8000
    EC2-->>Local: Live at http://54.86.99.71:8000
```

---

## 5. AWS Cloud Components

prompt-craft relies on these core AWS services:
1. **AWS ECR (Elastic Container Registry):** A private cloud folder where your built Docker image is stored.
2. **AWS EC2 (Elastic Compute Cloud):** A virtual server (`t3.micro`) running Ubuntu 22.04 that downloads and hosts the Docker container.
3. **AWS Security Group:** An inbound firewall rule configured to open **Port 8000** (so you can view the dashboard UI) and **Port 22** (for secure SSH management).
4. **AWS S3 (Simple Storage Service):** Used by the application to store prompt history run metrics and benchmark logs.
