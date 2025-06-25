from fastapi import UploadFile, HTTPException
from dotenv import load_dotenv
import os

load_dotenv()
MAX_FILE_SIZE:int = os.getenv("MAX_FILE_SIZE")
MAX_FILES:int = os.getenv("MAX_FILES")

def validate_file_list(files: list[UploadFile]):
    if len(files) > int(MAX_FILES): raise HTTPException(status_code=413, detail="Too many files were uploaded at once")
        
    for file in files:
        # Check if file is an image
        print(f"Size of file: {file.size}")
        if file.content_type != "image/jpeg" and file.content_type != "image/jpg" and file.content_type != "image/png" and file.content_type != "image/png" and file.content_type != "image/webp":
            raise HTTPException(status_code=415, detail="Uploaded file is not an image (valid file types: jpeg, jpg, png, webp)")
        if file.size > int(MAX_FILE_SIZE):
            raise HTTPException(status_code=413, detail=f"Uploaded image is to big ({int(MAX_FILE_SIZE)/1000} KB max)")
    return True