from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from PIL import Image
import uuid
import io
import os
import logging

from app.database import get_db
from app.models import UserProfile
from app.schemas import ProfileUpdateRequest, ProfileResponse
from app.crud import get_profile_by_user_id, create_or_update_profile
from app.auth import get_current_user, get_optional_current_user
from app.services.s3_service import s3_service

logger = logging.getLogger(__name__)

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
    
    # Helper function to normalize URLs
    def normalize_url(url: Optional[str], base_url: str = None) -> Optional[str]:
        if not url:
            return None
        url = url.strip()
        if not url:
            return None
        # If it's already a full URL, return it
        if url.startswith(('http://', 'https://')):
            return url
        # If base_url provided and url is just username/path, prepend base
        if base_url and not url.startswith('/'):
            # Handle username-only inputs
            if '/' not in url and '.' not in url:
                return f"{base_url}/{url}"
            # Handle partial paths
            elif not url.startswith('http'):
                return f"{base_url}/{url}"
        # Default to https:// if it looks like a domain
        if '.' in url:
            return f"https://{url}"
        return url
    
    # Handle the URL field conversions with smart normalization
    if 'github' in profile_dict:
        github_url = normalize_url(profile_dict.pop('github'), 'https://github.com')
        profile_dict['github_url'] = github_url
    if 'twitter' in profile_dict:
        twitter_url = normalize_url(profile_dict.pop('twitter'), 'https://twitter.com')
        profile_dict['twitter_url'] = twitter_url
    if 'linkedin' in profile_dict:
        linkedin_url = normalize_url(profile_dict.pop('linkedin'), 'https://linkedin.com/in')
        profile_dict['linkedin_url'] = linkedin_url
    
    # Handle website URL (require more complete URL)
    if 'website' in profile_dict:
        profile_dict['website'] = normalize_url(profile_dict['website'])
    
    # Email doesn't need URL processing
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
    
    # Resize image to max 500x500 while maintaining aspect ratio
    image.thumbnail((500, 500), Image.Resampling.LANCZOS)
    
    # Prepare image for upload
    output = io.BytesIO()
    file_extension = avatar.filename.split('.')[-1].lower()
    if file_extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        file_extension = 'jpg'
    image_format = 'JPEG' if file_extension in ['jpg', 'jpeg'] else file_extension.upper()
    
    # Save optimized image to bytes
    if image_format == 'JPEG':
        image.save(output, format=image_format, quality=85, optimize=True)
    else:
        image.save(output, format=image_format, optimize=True)
    output.seek(0)
    
    try:
        # Upload to S3
        logger.info(f"Uploading avatar for user {user_id}, filename: {avatar.filename}")
        avatar_url = s3_service.upload_avatar(
            file_content=output.read(),
            filename=avatar.filename,
            user_id=user_id
        )
        logger.info(f"Avatar uploaded to S3: {avatar_url}")
        
        # Update database with new avatar_url
        profile = get_profile_by_user_id(db, user_id)
        if profile:
            # Delete old avatar from S3 if it exists and is an S3 URL
            if profile.avatar_url and "s3" in profile.avatar_url and "amazonaws.com" in profile.avatar_url:
                try:
                    s3_service.delete_avatar(profile.avatar_url)
                except Exception as e:
                    # Log error but continue - old avatar deletion shouldn't block new upload
                    logger.warning(f"Error deleting old avatar: {e}")
            
            # Update avatar URL
            profile.avatar_url = avatar_url
            db.commit()
            db.refresh(profile)
            logger.info(f"Profile updated with new avatar URL: {avatar_url}")
        else:
            # Create new profile with avatar
            profile_data = {
                "user_id": user_id,
                "name": user_id,  # Default name
                "avatar_url": avatar_url
            }
            profile = create_or_update_profile(db, profile_data)
            logger.info(f"New profile created with avatar URL: {avatar_url}")
        
        return {"avatar_url": avatar_url, "message": "Avatar uploaded successfully"}
        
    except Exception as e:
        logger.error(f"Failed to upload avatar for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload avatar: {str(e)}"
        )