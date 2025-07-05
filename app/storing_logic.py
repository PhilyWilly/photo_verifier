import datetime
import shutil
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
import os

from database import Image, OrderNumber

def get_image_paths_from_ordernumber(order_number: str, db: Session) -> list[str]:
    # Get the order
    order = db.query(OrderNumber).filter(OrderNumber.number == order_number).first()

    if not order:
        # Order does not excist
        raise HTTPException(status_code=404, detail="Order number not found") 
    
    # Collect all images
    images = db.query(Image).filter(Image.ordernumber == order.id).all()
    return [img.filename for img in images]

def create_new_order_number(order_number: str, db: Session) -> int:
    # Check if order number exists
    order_number = str(order_number).strip() # Strip the number from spaces
    if db.query(OrderNumber).filter(OrderNumber.number == order_number).first():
        order = db.query(OrderNumber).filter(OrderNumber.number == order_number).first()
        files_index = db.query(Image).filter(Image.ordernumber == order.id).count()
        print(f"{files_index=}")
    else:
        # Order does not excists yet
        # Create new order
        order = OrderNumber(number=order_number)
        db.add(order)
        db.commit()
        db.refresh(order)
        files_index = 0

    return order.id, files_index

def add_images_to_ordernumber(files: list[UploadFile], order_id: int, order_number: str, files_index: int, db: Session):
    image_dir = "uploaded_images"
    os.makedirs(image_dir, exist_ok=True)

    for index, file in enumerate(files):
        # Create file name
        filename: str = f"{order_number}-{index+files_index}.jpeg"
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
    image_dir = "uploaded_images"

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
    threshold_date = datetime.datetime.utcnow() - datetime.timedelta(days=30*months)
    old_orders = db.query(OrderNumber).filter(OrderNumber.creation_date < threshold_date).all()
    for order in old_orders:
        delete_order_number(order.number, db=db)