import datetime
import shutil
from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
import os
from sqlalchemy import func
from datetime import datetime, time, timedelta

from database import Image, OrderNumber

# Load the secrets :-)
load_dotenv()
SERVERPATH = os.getenv("SERVERPATH")

def get_image_paths_from_ordernumber(order_number: str, db: Session) -> list[str]:
    # Get the order
    order = db.query(OrderNumber).filter(OrderNumber.number == order_number).first()

    if not order:
        # Order does not excist
        raise HTTPException(status_code=404, detail="Order number not found") 
    
    # Collect all images
    images = db.query(Image).filter(Image.ordernumber == order.id).all()
    return [img.filename for img in images]

def get_image_paths_by_date(date: str, db: Session) -> list[str]:
    # Parse input and use index-friendly range queries for date-only requests.
    try:
        input_dt = datetime.fromisoformat(date)
    except ValueError:
        # Try to parse as YYYY-MM-DD
        try:
            input_dt = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")

    # Detect whether the original input included a time component.
    has_time = ("T" in date) or (":" in date)

    if has_time:
        # Exact datetime match (still can use an index on the datetime column)
        orders = db.query(OrderNumber).filter(OrderNumber.creation_date == input_dt).all()
    else:
        # Date-only: use a half-open range [day_start, next_day) so DB can use indexes
        day_start = datetime.combine(input_dt.date(), time.min)
        next_day = day_start + timedelta(days=1)
        orders = db.query(OrderNumber).filter(
            OrderNumber.creation_date >= day_start,
            OrderNumber.creation_date < next_day
        ).all()

    if not orders:
        raise HTTPException(status_code=404, detail="Order number not found")

    # Collect all image filenames for the matching orders
    filenames: list[str] = []
    for order in orders:
        images_from_order: list[Image] = db.query(Image).filter(Image.ordernumber == order.id).all()
        for img in images_from_order:
            filenames.append(img.filename)

    return filenames

def create_new_order_number(order_number: str, retoure: bool, db: Session) -> int:
    # Check if order number exists
    order_number = str(order_number).strip() # Strip the number from spaces
    if db.query(OrderNumber).filter(OrderNumber.number == order_number).first():
        order = db.query(OrderNumber).filter(OrderNumber.number == order_number).first()
        files_index = db.query(Image).filter(Image.ordernumber == order.id).count()
        print(f"{files_index=}")
    else:
        # Order does not excists yet
        # Create new order
        if order_number == "" or order_number == "retoure" or order_number == "retoure!":
            order_number = None
        order = OrderNumber(number=order_number, retoure=retoure)
        db.add(order)
        db.commit()
        db.refresh(order)
        files_index = 0

    return order.id, files_index

def add_images_to_ordernumber(files: list[UploadFile], order_id: int, order_number: str, files_index: int, db: Session):
    image_dir = f"{SERVERPATH}uploaded_images"
    os.makedirs(image_dir, exist_ok=True)

    for index, file in enumerate(files):
        # Create file name
        filename: str = f"{order_number.replace('/', '-SLASH-')}-{index+files_index}.jpeg"
        file_path: str = os.path.join(image_dir, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        img = Image(filename=filename, ordernumber=order_id)
        db.add(img)
    db.commit()

def delete_order_number(order_number: str, db: Session):
    # Find the order by number
    order = db.query(OrderNumber).filter(OrderNumber.number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order number not found")

    # Find all images associated with the order
    images = db.query(Image).filter(Image.ordernumber == order.id).all()
    image_dir = f"{SERVERPATH}uploaded_images"

    # Delete image files from the directory
    for img in images:
        file_path = os.path.join(image_dir, img.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    # Delete images from the database
    db.query(Image).filter(Image.ordernumber == order.id).delete()
    # Delete the order from the database
    db.delete(order)
    db.commit()

def delete_old_ordernumbers(db: Session, months: int = 3):
    threshold_date = datetime.utcnow() - timedelta(days=30*months)
    old_orders = db.query(OrderNumber).filter(OrderNumber.creation_date < threshold_date).all()
    for order in old_orders:
        delete_order_number(order.number, db=db)