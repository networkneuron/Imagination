#!/usr/bin/env python3
"""
Create a simple icon for the Ultimate AI System Automation Agent
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Create a simple icon using PIL"""
    try:
        # Create a 64x64 image with transparent background
        size = (64, 64)
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a sci-fi style icon
        # Background circle
        draw.ellipse([4, 4, 60, 60], fill=(0, 255, 255, 255), outline=(255, 0, 255, 255), width=2)
        
        # Inner circle
        draw.ellipse([12, 12, 52, 52], fill=(0, 0, 0, 0), outline=(255, 255, 0, 255), width=2)
        
        # Central symbol (AI)
        draw.text((20, 20), "AI", fill=(255, 255, 255, 255))
        
        # Sci-fi lines
        draw.line([(16, 16), (48, 48)], fill=(0, 255, 255, 255), width=1)
        draw.line([(48, 16), (16, 48)], fill=(0, 255, 255, 255), width=1)
        
        # Save as ICO
        img.save('icon.ico', format='ICO', sizes=[(64, 64), (32, 32), (16, 16)])
        print("✅ Icon created: icon.ico")
        return True
        
    except ImportError:
        print("⚠️  PIL not available. Creating a simple text icon placeholder...")
        # Create a simple text file as placeholder
        with open('icon.txt', 'w') as f:
            f.write("Icon placeholder - replace with actual icon.ico file")
        return False
    except Exception as e:
        print(f"❌ Error creating icon: {e}")
        return False

if __name__ == "__main__":
    create_icon()
