from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from PIL import Image
import uuid
import io
import os

from app.database import get_db
from app.models import UserProfile
from app.schemas import ProfileUpdateRequest, ProfileResponse
from app.crud import get_profile_by_user_id, create_or_update_profile
from app.auth import get_current_user, get_optional_current_user

router = APIRouter()


@router.put("/profile/update", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verify that the user is updating their own profile
    if profile_data.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this profile"
        )
    
    # Convert URLs to database fields
    profile_dict = profile_data.model_dump()
    
    # Handle the URL field conversions
    if 'github' in profile_dict:
        profile_dict['github_url'] = str(profile_dict.pop('github')) if profile_dict['github'] else None
    if 'twitter' in profile_dict:
        profile_dict['twitter_url'] = str(profile_dict.pop('twitter')) if profile_dict['twitter'] else None
    if 'linkedin' in profile_dict:
        profile_dict['linkedin_url'] = str(profile_dict.pop('linkedin')) if profile_dict['linkedin'] else None
    
    # Ensure these fields are strings or None
    profile_dict['website'] = str(profile_dict['website']) if profile_dict.get('website') else None
    profile_dict['email'] = str(profile_dict['email']) if profile_dict.get('email') else None
    
    # Create or update profile
    profile = create_or_update_profile(db, profile_dict)
    
    return profile


@router.get("/profile/me", response_model=ProfileResponse)
async def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    profile = get_profile_by_user_id(db, user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@router.get("/profile/{user_id}", response_model=ProfileResponse)
async def get_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@router.post("/profile/avatar")
async def upload_avatar(
    avatar: UploadFile = File(...),
    user_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verify that the user is uploading their own avatar
    if user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to upload avatar for this user"
        )
    
    # Validate file type
    if not avatar.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validate file size (max 5MB)
    if avatar.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")
    
    # Read and resize image
    contents = await avatar.read()
    image = Image.open(io.BytesIO(contents))
    
    # Convert to RGB if necessary (for PNG with transparency)
    if image.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[-1])
        image = background
    
    # Resize image
    image.thumbnail((500, 500), Image.Resampling.LANCZOS)
    
    # Generate unique filename
    file_extension = avatar.filename.split('.')[-1].lower()
    if file_extension not in ['jpg', 'jpeg', 'png', 'gif']:
        file_extension = 'jpg'
    unique_filename = f"{user_id}_{uuid.uuid4()}.{file_extension}"
    
    # Create directory if it doesn't exist
    upload_dir = "static/avatars"
    os.makedirs(upload_dir, exist_ok=True)
    upload_path = os.path.join(upload_dir, unique_filename)
    
    # Save image
    output = io.BytesIO()
    image_format = 'JPEG' if file_extension in ['jpg', 'jpeg'] else file_extension.upper()
    image.save(output, format=image_format)
    output.seek(0)
    
    with open(upload_path, "wb") as f:
        f.write(output.read())
    
    avatar_url = f"/static/avatars/{unique_filename}"
    
    # Update database with new avatar_url
    profile = get_profile_by_user_id(db, user_id)
    if profile:
        # Delete old avatar file if exists
        if profile.avatar_url and profile.avatar_url.startswith("/static/avatars/"):
            old_file_path = profile.avatar_url[1:]  # Remove leading slash
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        
        # Update avatar URL
        profile.avatar_url = avatar_url
        db.commit()
        db.refresh(profile)
    else:
        # Create new profile with avatar
        profile_data = {
            "user_id": user_id,
            "name": user_id,  # Default name
            "avatar_url": avatar_url
        }
        profile = create_or_update_profile(db, profile_data)
    
    return {"avatar_url": avatar_url, "message": "Avatar uploaded successfully"}