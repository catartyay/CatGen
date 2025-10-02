"""
Cat image renderer - creates visual representation of cats
"""

from PIL import Image, ImageDraw, ImageFont
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
import io


class CatRenderer:
    """Renders cat images based on phenotype"""
    
    def __init__(self):
        self.image_size = (400, 500)
        self.color_map = self.load_color_map()
    
    def load_color_map(self):
        """Define color mappings for phenotypes"""
        return {
            # Solid colors
            'Black': (0, 0, 0),
            'Blue': (100, 120, 140),
            'Chocolate': (90, 50, 30),
            'Lilac': (150, 130, 140),
            'Cinnamon': (140, 80, 50),
            'Fawn': (180, 140, 110),
            'Red': (220, 100, 60),
            'Cream': (240, 200, 150),
            'White': (255, 255, 255),
            'Seal': (40, 30, 30),
            'Ruddy': (160, 90, 50),
            'Sorrel': (200, 100, 60),
            
            # Eye colors
            'Blue_eye': (80, 140, 220),
            'Green_eye': (60, 180, 100),
            'Gold_eye': (220, 180, 50),
            'Copper_eye': (180, 100, 40),
            'Amber_eye': (200, 140, 50),
            'Hazel_eye': (140, 120, 70),
            'Yellow_eye': (230, 200, 60),
        }
    
    def render_cat(self, cat, phenotype_calc):
        """Render a cat as an image"""
        # Create blank image
        img = Image.new('RGB', self.image_size, (245, 245, 245))
        draw = ImageDraw.Draw(img)
        
        # Get phenotype info
        phenotype = phenotype_calc.calculate_phenotype(cat)
        eye_color = phenotype_calc.calculate_eye_color(cat)
        white_pct = phenotype_calc.get_white_percentage(cat)
        
        # Extract base color
        base_color = self.extract_base_color(phenotype)
        
        # Draw cat body
        self.draw_cat_body(draw, base_color, white_pct)
        
        # Draw eyes
        self.draw_eyes(draw, eye_color)
        
        # Draw pattern (simplified)
        if 'Tabby' in phenotype:
            self.draw_tabby_stripes(draw, base_color)
        
        # Add text labels
        self.draw_labels(draw, cat, phenotype, eye_color)
        
        return self.pil_to_qpixmap(img)
    
    def extract_base_color(self, phenotype):
        """Extract base color from phenotype string"""
        for color_name, rgb in self.color_map.items():
            if color_name in phenotype and '_eye' not in color_name:
                return rgb
        return (150, 150, 150)  # Default gray
    
    def draw_cat_body(self, draw, color, white_pct):
        """Draw simplified cat body"""
        # Body oval
        body_color = color if white_pct < 50 else (255, 255, 255)
        draw.ellipse([100, 200, 300, 400], fill=body_color, outline=(0, 0, 0), width=2)
        
        # Head circle
        head_color = color if white_pct < 30 else (255, 255, 255)
        draw.ellipse([140, 120, 260, 240], fill=head_color, outline=(0, 0, 0), width=2)
        
        # Ears
        ear_points_left = [(140, 150), (120, 100), (160, 130)]
        ear_points_right = [(260, 150), (280, 100), (240, 130)]
        draw.polygon(ear_points_left, fill=head_color, outline=(0, 0, 0))
        draw.polygon(ear_points_right, fill=head_color, outline=(0, 0, 0))
        
        # Legs (simplified)
        draw.rectangle([120, 380, 150, 460], fill=body_color, outline=(0, 0, 0))
        draw.rectangle([250, 380, 280, 460], fill=body_color, outline=(0, 0, 0))
        
        # Tail
        draw.arc([60, 250, 120, 350], 0, 180, fill=(0, 0, 0), width=15)
    
    def draw_eyes(self, draw, eye_color):
        """Draw cat eyes"""
        # Determine eye color RGB
        eye_rgb = (100, 180, 100)  # Default green
        
        if 'Blue' in eye_color:
            eye_rgb = self.color_map.get('Blue_eye', (80, 140, 220))
        elif 'Green' in eye_color:
            eye_rgb = self.color_map.get('Green_eye', (60, 180, 100))
        elif 'Gold' in eye_color or 'Golden' in eye_color:
            eye_rgb = self.color_map.get('Gold_eye', (220, 180, 50))
        elif 'Copper' in eye_color:
            eye_rgb = self.color_map.get('Copper_eye', (180, 100, 40))
        elif 'Amber' in eye_color:
            eye_rgb = self.color_map.get('Amber_eye', (200, 140, 50))
        elif 'Yellow' in eye_color:
            eye_rgb = self.color_map.get('Yellow_eye', (230, 200, 60))
        
        # Left eye
        draw.ellipse([160, 170, 180, 190], fill=eye_rgb, outline=(0, 0, 0), width=2)
        draw.ellipse([167, 177, 173, 183], fill=(0, 0, 0))  # Pupil
        
        # Right eye
        draw.ellipse([220, 170, 240, 190], fill=eye_rgb, outline=(0, 0, 0), width=2)
        draw.ellipse([227, 177, 233, 183], fill=(0, 0, 0))  # Pupil
    
    def draw_tabby_stripes(self, draw, base_color):
        """Draw simplified tabby stripes"""
        # Darken base color for stripes
        stripe_color = tuple(max(0, c - 50) for c in base_color)
        
        # Body stripes
        for y in range(220, 380, 30):
            draw.line([(120, y), (280, y + 20)], fill=stripe_color, width=3)
        
        # Head stripes
        draw.line([(200, 140), (200, 170)], fill=stripe_color, width=3)
        draw.line([(180, 145), (220, 145)], fill=stripe_color, width=2)
    
    def draw_labels(self, draw, cat, phenotype, eye_color):
        """Draw text labels"""
        # Title
        title = f"Cat #{cat.id}"
        if cat.name:
            title += f" - {cat.name}"
        
        # Use default font
        draw.text((10, 10), title, fill=(0, 0, 0))
        draw.text((10, 30), phenotype[:50], fill=(0, 0, 0))
        if len(phenotype) > 50:
            draw.text((10, 45), phenotype[50:], fill=(0, 0, 0))
        draw.text((10, 65), f"Eyes: {eye_color}", fill=(0, 0, 0))
    
    def pil_to_qpixmap(self, pil_image):
        """Convert PIL Image to QPixmap"""
        # Convert PIL image to bytes
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Create QPixmap from bytes
        qimage = QImage.fromData(img_byte_arr)
        return QPixmap.fromImage(qimage)