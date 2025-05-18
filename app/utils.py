"""
Utility functions for the mental health support app.
"""
import os
import hashlib
from PIL import Image, ImageDraw
from app import db
from app.models import Avatar

def generate_identicon(text, size=420):
    """Generate an identicon-style avatar."""
    # Create a hash of the text
    hash_object = hashlib.md5(text.encode())
    hash_hex = hash_object.hexdigest()
    
    # Create a new image with a white background
    image = Image.new('RGB', (size, size), 'white')
    draw = ImageDraw.Draw(image)
    
    # Use the hash to determine the color
    color = '#{}'.format(hash_hex[:6])
    
    # Create a 5x5 grid of squares
    block_size = size // 5
    for i in range(3):  # Only need to do half, will mirror
        for j in range(5):
            if int(hash_hex[i * 5 + j], 16) % 2 == 0:  # Use hash to determine if block should be filled
                # Draw the square and its mirror
                draw.rectangle([
                    i * block_size, j * block_size,
                    (i + 1) * block_size - 1, (j + 1) * block_size - 1
                ], fill=color)
                # Mirror the square
                draw.rectangle([
                    (4 - i) * block_size, j * block_size,
                    (5 - i) * block_size - 1, (j + 1) * block_size - 1
                ], fill=color)
    
    return image

def ensure_avatar_dirs(app):
    """Ensure avatar directories exist and create them if they don't."""
    avatar_dir = os.path.join(app.static_folder, 'avatars')
    os.makedirs(avatar_dir, exist_ok=True)
    
    # Create default avatar
    default_path = os.path.join(avatar_dir, 'default.png')
    if not os.path.exists(default_path):
        default_avatar = generate_identicon('default')
        default_avatar.save(default_path, 'PNG')

def initialize_default_avatars(app):
    """Initialize default avatars if they don't exist."""
    if Avatar.query.count() == 0:
        avatar_dir = os.path.join(app.static_folder, 'avatars')
        
        # Create default avatars with different seeds
        for i in range(1, 11):
            filename = f'avatar{i}.png'
            filepath = os.path.join(avatar_dir, filename)
            
            if not os.path.exists(filepath):
                avatar = generate_identicon(f'avatar{i}')
                avatar.save(filepath, 'PNG')
            
            db_avatar = Avatar(filename=filename)
            db.session.add(db_avatar)
        
        db.session.commit() 