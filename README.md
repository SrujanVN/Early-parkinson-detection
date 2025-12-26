# 🧠 Early Parkinson’s Detection & Analysis via xAI

This is a clinical-grade diagnostic support platform that utilizes **12 ensemble deep learning models** and **Explainable AI (XAI)** to detect early signs of Parkinson’s Disease. It analyzes MRI scans (with GradCAM/LIME), voice recordings, handwriting, and clinical data.

---

## ✨ Features

- **Multi-Modal Ensemble Analysis**: Combines predictions from 12 specialized models across MRI, Voice, Handwriting, and Clinical symptoms.
- **Explainable AI (XAI)**: Generates GradCAM heatmaps and LIME explanations for MRI analysis to support clinical decision-making.
- **Integrated AI Assistant**: A unified Gemini AI chatbot for patient education and diagnostic guidance.
- **Persistent Analysis**: Base64-encoded session management ensures analysis results survive page refreshes.
- **Project Dockerization**: Fully containerized environment for consistent deployment across any infrastructure.
- **Medical Grade Reporting**: Generates detailed PDF reports with visualization overlays and risk assessments.

---

## 🛠 Tech Stack

- **Frontend:** React, TypeScript, TailwindCSS, Vite
- **Backend:** Flask (Python 3.10)
- **AI/ML Frameworks:** TensorFlow, PyTorch, Scikit-learn, XGBoost
- **XAI:** OpenCV, GradCAM, LIME (Superpixel segmentation)
- **LLM:** Google Gemini AI (Unified SDK)
- **DevOps:** Docker, Docker Compose, Nginx, Git LFS

---

## ⚙️ Quick Start (Docker - Recommended)

The easiest way to run the entire stack (including 18GB of models and dependencies) is using Docker Compose.

### 1. Clone the repository
```bash
git clone https://github.com/SrujanVN/Early-parkinson-detection.git
cd Early-parkinson-detection
```

### 2. Configure Environment
Create a `.env` file in the `backend/` directory:
```bash
GEMINI_API_KEY=your_api_key_here
```

### 3. Build and Run
```bash
docker-compose up --build -d
```
- **Frontend**: [http://localhost:8080](http://localhost:8080)
- **Backend API**: [http://localhost:5000](http://localhost:5000)

---

## 🛠 Manual Installation (Development)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
# From the root directory
npm install
npm run dev
```

---

## 📁 Project Structure

```
.
├── backend/
│   ├── models/                  # 12 Ensemble Models (.pth, .pkl)
│   ├── uploads/                 # Storage for processing analysis
│   ├── app.py                   # Main Flask API
│   ├── ensemble_predictor.py    # Multi-model inference logic
│   ├── xai_visualizations.py    # GradCAM & LIME implementation
│   └── Dockerfile               # Backend container config
├── src/
│   ├── components/              # UI, Upload, & Result Visualizers
│   ├── contexts/                # Persisted Session Management
│   ├── pages/                   # Landing, Upload, & Chatbot pages
│   └── utils/                   # Centralized API clients
├── Dockerfile                   # Frontend container config (Nginx)
├── docker-compose.yml           # Full stack orchestration
├── nginx.conf                   # Reverse proxy configuration
└── README.md
```

---

## 📦 Large File Storage (Git LFS)

This project uses **Git LFS** to manage large model files and datasets. Ensure you have Git LFS installed before cloning:
```bash
git lfs install
git clone https://github.com/SrujanVN/Early-parkinson-detection.git
```

---

## 🙌 Acknowledgements

We extend our deepest gratitude to our main project coordinator, [**Dr. Victor Ikechukwu Agughasi**](https://github.com/Victor-Ikechukwu), for his overall coordination and support, and to our guides **Shashanka H P** and **M J Yogesh** for their expert guidance throughout the development of this project..

**Team Members:**
- Rushika K Shankar
- Ronith D Singh
- Yashas M Samrat


---

## 📜 License

This project is licensed under the MIT License.
