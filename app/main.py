from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from storing_logic import add_images_to_ordernumber, create_new_order_number, delete_old_ordernumbers, get_image_paths_from_ordernumber
from validations import validate_file_list
from database import Image, OrderNumber, get_db

# Load the secrets :-)
load_dotenv()
FAVICON_URL = os.getenv("FAVICON_URL")
#X_API_KEY = os.getenv("X-API-Key")
DATABASEURL = os.getenv("DATABASEURL")
SERVERURL = os.getenv("SERVERURL")
SERVERPORT = int(os.getenv("SERVERPORT"))
SERVERPATH = os.getenv("SERVERPATH")

# Setup templates
templates = Jinja2Templates(directory=f"{SERVERPATH}templates")

# Initialize app
app = FastAPI()
app.mount("/static", StaticFiles(directory=f"{SERVERPATH}static"), name="static")

# !!! THE SECURITY FEATURE IS DISABLED !!!
# Add security layer for only in company usage
# 
# This part is optional, but it ensures, that only clients with the same api key as the server
# can access the data stored in the server. 
# Kepp in mind, that every client message to the server need the api key in the header.
# 
# Exeptions for this rule are:
# - All HTMLResponses
# - All static responses
# - The favicon
'''
@app.middleware("http")
async def check_api_key(request: Request, call_next):
    if request.url.path == "/" or request.url.path == "/image_getter/" or request.url.path == "/image_poster/":
        return await call_next(request)
    if request.url.path.startswith("/static") or request.url.path.startswith("/favicon"):
        return await call_next(request)
    if request.headers.get("X-API-Key") != X_API_KEY:
        return JSONResponse(status_code=403, content={"detail": "Forbidden"})
    return await call_next(request)
'''

r"""
 _   _ _____ __  __ _      
| | | |_   _|  \/  | |     
| |_| | | | | |\/| | |     
|  _  | | | | |  | | |___  
|_| |_| |_| |_|  |_|_____| 
"""
@app.get("/", response_class=HTMLResponse)
async def default_url(request: Request):
    return RedirectResponse("/image_getter/")

@app.get("/image_getter/", response_class=HTMLResponse)
async def image_getter_url(request: Request):
    return templates.TemplateResponse(
        "image_getter.html", 
        {
            "request": request,
            "favicon_url": FAVICON_URL
        }
    )

@app.get("/image_poster/", response_class=HTMLResponse)
async def image_poster_url(request: Request):
    return templates.TemplateResponse(
        "image_poster.html", 
        {
            "request": request,
            "favicon_url": FAVICON_URL
        }
    )


r"""
    _    ____ ___  
   / \  |  _ \_ _| 
  / _ \ | |_) | |  
 / ___ \|  __/| |  
/_/   \_\_|  |___| 
"""
# Get all the order_numbers
#
# Inputs: q: string the search input from the search bar
#         offset: int the offset for the list
#         limit: int the limit for the list
# Output: order_numbers: list[string]
@app.get("/order_numbers/")
async def get_order_numbers(
    q: str = Query("", alias="q"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(OrderNumber)
    if q:
        query = query.filter(OrderNumber.number.contains(q.strip()))
    total = query.count()
    order_numbers = [order.number for order in query.order_by(OrderNumber.number).offset(offset).limit(limit)]
    return {"order_numbers": order_numbers, "total": total}

# Get all the image paths from a order number
#
# Input: order_number: string
# Output: images: list[string]
@app.get("/images/")
async def get_images_for_order(order_number: str, db: Session = Depends(get_db)):
    # Delete all old ordernumbers
    delete_old_ordernumbers(db)

    order_number: str = order_number.strip() # Strip the number from spaces
    file_paths = get_image_paths_from_ordernumber(order_number, db=db)
    return {"images": file_paths}

# Get the image file from the filename
#
# Input: filename: string
# Ouput: Imagefile: image/jpeg
@app.get("/image/{filename}/")
async def get_image_file(filename: str):
    image_path = os.path.join(f"{SERVERPATH}uploaded_images", filename)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path, media_type="image/jpeg", filename=filename)

# Add a new ordernumber and images for that order number
#
# Input: order_number: string
#        files: list[images]
# Ouput: order_id: int
@app.post("/orders/")
async def create_order_with_images(
    number: str = Form(...),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    # Delete all old ordernumbers
    delete_old_ordernumbers(db)

    # Validate files if images
    validate_file_list(files)   

    order_id, files_index = create_new_order_number(number, db=db)
    add_images_to_ordernumber(files=files, order_id=order_id, order_number=number,files_index=files_index, db=db)
  
    return order_id

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=SERVERURL, port=SERVERPORT, reload=True)