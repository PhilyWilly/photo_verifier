# Photo Verifyer

A FastAPI-based web application for uploading, storing, and retrieving images associated with order numbers. Images are stored on disk and metadata is managed with SQLite via SQLAlchemy.

## Features
- Upload multiple images for a specific order number
- Retrieve all images for a given order number
- Simple web UI for uploading and viewing images

## Requirements
- Python 3.10+
- FastAPI
- SQLAlchemy
- Uvicorn (for running the server)

## Setup

1. **Clone the repository**
   ```sh
   git clone PhilyWilly/photo_verifier
   cd photo_verifier
   ```

2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. **Access the app**
   - Image upload: [http://127.0.0.1:8000/image_poster/](http://127.0.0.1:8000/image_poster/)
   - Image search: [http://127.0.0.1:8000/image_getter/](http://127.0.0.1:8000/image_getter/)
   (dont forget to use the secret api key)

## Project Structure
```
photo_verifyer/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── validations.py
│   ├── storing_logic.py
│   └── ...
├── static/
│   ├── get_images.js
│   ├── post_images.js
│   └── style.css
├── templates/
│   ├── image_getter.html
│   └── image_poster.html
├── uploaded_images/
├── requirements.txt
└── README.md
```

## API Endpoints
- `POST /orders/` — Upload images for an order number
- `GET /images/{order_number}/` — Get all image filenames for an order number
- `GET /image/{filename}/` — Download a specific image
- `GET /all_order_numbers/` — Get all order numbers

## TODOS
- [ ] Create automated deleting algorithm

## License
MIT
