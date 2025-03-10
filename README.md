
# Augmented Reality Object Viewer

This project is an Augmented Reality (AR) application that loads and displays 3D objects using OpenCV and Streamlit.

## 📁 Folder Structure

```
AUGMENTED-REALITY/
│── models/                # Contains 3D object (.obj) files
│── reference/             # Reference images for object placement
│── src/                   # Source code
│   │── ar_main.py         # Main AR processing script
│   │── objloader_simple.py# Helper script for loading .obj files
│   │── app.py             # Streamlit frontend
│── requirements.txt       # Dependencies
```

## 🚀 Setup Instructions

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/Sonupatel15/Augmented-reality
cd AUGMENTED-REALITY
```

### 2️⃣ Create a Virtual Environment (Recommended)
```sh
python -m venv venv
```
Activate the virtual environment:

- **Windows:**
  ```sh
  venv\Scripts\activate
  ```
- **Mac/Linux:**
  ```sh
  source venv/bin/activate
  ```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```
If `requirements.txt` is missing, generate it by running:
```sh
pip freeze > requirements.txt
```

### 4️⃣ Run the Streamlit Frontend
```sh
streamlit run src/app.py
```
This will launch the Streamlit UI in your browser. 🚀

## 🛠️ Future Enhancements
- Implement FastAPI backend for handling API requests.
- Use Uvicorn for running the backend.
- Improve object tracking and rendering.

---
Made with ❤️ using OpenCV and Streamlit.
