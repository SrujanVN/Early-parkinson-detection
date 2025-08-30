# 🧠 Early Parkinson’s Detection

This project focuses on detecting **early signs of Parkinson’s Disease** using machine learning and deep learning techniques.  
It provides an intuitive interface for uploading patient data (such as voice recordings, medical data, etc.) and returns predictions.

---

## ✨ Features

- Detects early Parkinson’s disease with machine learning models.
- Interactive **React + TailwindCSS** frontend.
- **Flask backend** serving predictions.
- Supports multiple input formats.
- Scalable and deployable on cloud platforms.
- Live demo for real-time testing.

---

## 🛠 Tech Stack

- **Frontend:** React, TypeScript, TailwindCSS  
- **Backend:** Flask (Python)  
- **Machine Learning:** Scikit-learn / TensorFlow / Keras  
- **Deployment:** Render / Vercel / Netlify / HuggingFace Spaces (choose your platform)  

---

## ⚙️ Installation & Setup

### 🔹 Clone the repository

```bash
git clone https://github.com/SrujanVN/Early-parkinson-detection.git
cd Early-parkinson-detection
```

### 🔹 Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate it
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Flask server
python app.py
```

The backend server will run at: [http://localhost:5000/](http://localhost:5000/)

### 🔹 Frontend Setup

Open a **new terminal**, then:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will run at: [http://localhost:5173/](http://localhost:5173/)

---


## 🚀 Live Demo

👉 _Click here to try the live demo_  
<https://early-parkinsons-detection.netlify.app/>

---

## 📁 Project Structure

```
Early-parkinson-detection/
│
├── backend/                   # Flask backend + ML model
│   ├── app.py                 # Main Flask app
│   ├── requirements.txt       # Python dependencies
│   ├── models/                # Saved ML/DL models (.h5, .pkl, etc.)
│   ├── static/                # Static assets if needed
│   └── templates/             # HTML templates (if any)
│
├── frontend/                  # React + TypeScript + TailwindCSS
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # App pages (Home, Upload, Results)
│   │   ├── services/          # API calls to Flask backend
│   │   ├── App.tsx            # Main entry component
│   │   └── main.tsx           # React DOM entry
│   ├── public/                # Static frontend assets
│   ├── package.json           # Frontend dependencies
│   └── tailwind.config.js     # Tailwind configuration
│
├── README.md                  # Project documentation
└── .gitignore                 # Ignore unnecessary files
```

---

## 🙌 Acknowledgements

We would like to express our sincere gratitude to our guide **Shashanka H P** for his valuable guidance and support throughout the development of this project.

We also acknowledge the contributions of our team members:
- Rushika K Shankar
- Ronith D Singh
- Yashas M Samrat


---

## 📜 License

This project is licensed under the MIT License.

---
