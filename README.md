Markdown# 🎬 Cinebook: Cloud-Native Recommendation Engine

![Python](https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge&logo=python&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-Run-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-High_Performance-009688?style=for-the-badge&logo=fastapi&logoColor=white)

> **A scalable, serverless SaaS application that unifies movie and book recommendations using Machine Learning and Hybrid Filtering Architecture.**

<img width="100%" alt="Cinebook Dashboard" src="https://github.com/user-attachments/assets/a268c240-c873-470c-ae0a-6cb65a6ed60c" />

---

## 📖 Project Overview

**Cinebook** is a full-stack recommendation platform designed to solve the **"Decision Fatigue"** and **"Cold Start"** problems prevalent in modern streaming services.

Unlike traditional local ML models, Cinebook is engineered as a **Cloud-Native** application. It is containerized with **Docker** and deployed on **Google Cloud Run**, featuring a custom **Stateful Architecture** within a stateless serverless environment to ensure robust data persistence.

### 🌟 Key Features
* **Hybrid Recommendation Logic:** Utilizes **TF-IDF Vectorization** and **Cosine Similarity** to analyze semantic metadata (plots, genres, authors) for accurate content-based suggestions.
* **Unified Media Experience:** Seamlessly integrates two distinct domains (Movies & Books) into a single user interface.
* **Serverless Scalability:** Deployed on **Google Cloud Run** with "Scale-to-Zero" capability, optimizing costs and handling traffic spikes automatically.
* **Persistent User Data:** Overcomes the ephemeral nature of containers by implementing **Cloud Storage FUSE** to mount a persistent bucket for the database.
* **Interactive Dashboard:** Features user authentication, watchlists, favorites, and real-time rating systems.

---

## 🏗️ System Architecture

The project follows a **Decoupled Architecture**, separating the Compute Layer from the Storage Layer for maximum resilience.

graph TD;
    User-->|HTTPS Request| CloudRun[Google Cloud Run Container];
    CloudRun-->|Compute| ML_Engine[TF-IDF & Cosine Similarity];
    CloudRun-->|Read/Write via FUSE| GCS[Google Cloud Storage Bucket];
    GCS-->|Persist| SQLiteDB[(Cinebook Database)];
    CloudRun-->|Response| Frontend[Jinja2 / HTML5 Interface];
    
🚀 Installation & Usage1. Local DevelopmentTo run the project locally on your machine:Bash# Clone the repository
git clone [https://github.com/sya126/cinebook-cloud-recommendation.git](https://github.com/sya126/cinebook-cloud-recommendation.git)
cd cinebook-cloud-recommendation

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn api:app --reload
Access the app at http://127.0.0.1:80002. Cloud Deployment (GCP)The deployment process using Google Cloud SDK:Bash# Build the Docker image and push to Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/cinebook

# Deploy to Cloud Run with FUSE execution environment
gcloud run deploy cinebook \
  --image gcr.io/YOUR_PROJECT_ID/cinebook \
  --platform managed \
  --execution-environment gen2 \
  --allow-unauthenticated
  
📂 Project StructureBashcinebook-cloud-recommendation/
├── api.py              # Main Application Entry Point (FastAPI Routes)
├── recommender.py      # ML Engine (Vectorization & Similarity Logic)
├── data_manager.py     # Database Handler (SQLite & FUSE Integration)
├── processor.py        # ETL Script (Data Cleaning & Processing)
├── user_manager.py     # Auth System (Password Hashing & Sessions)
├── Dockerfile          # Container Configuration
├── requirements.txt    # Project Dependencies
└── templates/          # Frontend UI Files

**Author: Şeyma Adanalı
