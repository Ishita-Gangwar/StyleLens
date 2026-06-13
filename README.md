# StyleLens

StyleLens is a fashion image similarity search app built with FastAPI, FAISS, PyTorch, React, TypeScript, and Vite.

## Features

- Upload a fashion image
- Find visually similar items from the dataset
- View product image, title, category, color, usage, and similarity score
- FastAPI backend with FAISS-based image retrieval
- React frontend with image preview and result cards

## Tech Stack

- Backend: FastAPI, PyTorch, FAISS, Pandas
- Frontend: React, TypeScript, Vite
- Model: ResNet50 feature embeddings

## Project Structure

```text
stylelens/
  backend/
    app/
    ml/
    requirements.txt
  frontend/
    src/
    package.json
```

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at:
`http://127.0.0.1:8000`

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:
`http://localhost:5173`

## API Endpoint

### POST `/search?k=5`

Uploads an image and returns similar fashion items.

## Notes

- The frontend is built with TypeScript, so the main files are `App.tsx` and `main.tsx`.
- Static dataset images are served by the FastAPI backend.
- Docker setup can be added later.

## Future Improvements

- Docker containerization
- Drag and drop upload
- Top-k selector
- Better metadata filtering