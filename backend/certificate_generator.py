import os
from datetime import datetime
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageDraw, ImageFont
import uuid
import base64

class CertificateGenerator:
    """Generate certificates with QR codes"""
    
    def __init__(self, template_path, config, field_config=None):
        self.template_path = template_path
        self.config = config
        self.field_config = field_config or {}
        # Handle both dict-like config (Flask) and object config
        if hasattr(config, 'CERTIFICATE_FOLDER'):
            self.certificate_folder = config.CERTIFICATE_FOLDER
        else:
            self.certificate_folder = config.get('CERTIFICATE_FOLDER', os.path.join(os.path.dirname(__file__), '..', 'certificates'))
        
        if not os.path.exists(self.certificate_folder):
            os.makedirs(self.certificate_folder)
    
    @staticmethod
    def generate_qr_code(data, filename):
        """Generate QR code for certificate"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        return filename
    
    def create_certificate_pdf(self, recipient_name, course_name, issue_date, certificate_uid, output_path):
        """Create PDF certificate with background image based on visual configuration"""
        
        # Make base image strictly 1200x800 to match frontend UI virtual canvas
        if self.template_path and os.path.exists(self.template_path):
            img = Image.open(self.template_path).convert('RGB')
        else:
            img = Image.new('RGB', (1200, 800), color=(240, 248, 255))
            
        img = img.resize((1200, 800))
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        fields = self.field_config.get('fields', [])
        
        # Auto-generate QR code as a file
        qr_filename = os.path.join(self.certificate_folder, f"qr_{certificate_uid}.png")
        verification_url = f"https://yoursite.com/verify/{certificate_uid}"
        self.generate_qr_code(verification_url, qr_filename)
        
        if fields:
            # We have visual field configurations
            for el in fields:
                if el.get('type') == 'text':
                    val = el.get('value', '')
                    # Dynamic replacements
                    val = val.replace('{{recipient_name}}', recipient_name)
                    val = val.replace('{{course_name}}', course_name)
                    val = val.replace('{{issue_date}}', issue_date.strftime('%B %d, %Y'))
                    val = val.replace('{{certificate_uid}}', certificate_uid)
                    
                    font_size = int(el.get('font_size', 24))
                    color_hex = el.get('color', '#000000').lstrip('#')
                    color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4)) if len(color_hex) == 6 else (0,0,0)
                    
                    x, y = el.get('x', 0), el.get('y', 0)
                    try:
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
                    
                    # Pillow draw.text treats (x,y) as top-left when using default anchor
                    draw.text((x, y), val, fill=color_rgb, font=font)
                    
                elif el.get('type') == 'image':
                    b64_data = el.get('value', '')
                    if b64_data.startswith('data:image'):
                        b64_data = b64_data.split(',')[1]
                    try:
                        img_data = base64.b64decode(b64_data)
                        logo = Image.open(BytesIO(img_data)).convert('RGBA')
                        
                        lw, lh = int(el.get('width', 100)), int(el.get('height', 100))
                        lx, ly = int(el.get('x', 0)), int(el.get('y', 0))
                        logo = logo.resize((lw, lh))
                        
                        # Use self as mask if transparent
                        mask = logo if 'A' in logo.getbands() else None
                        img.paste(logo, (lx, ly), mask)
                    except Exception as e:
                        print(f"Failed to load overlay image: {e}")
        else:
            # Fallback legacy layout if no visual config is present
            try:
                title_font = ImageFont.truetype("arial.ttf", 60)
                name_font = ImageFont.truetype("arial.ttf", 48)
                text_font = ImageFont.truetype("arial.ttf", 24)
                small_font = ImageFont.truetype("arial.ttf", 16)
            except:
                title_font = name_font = text_font = small_font = ImageFont.load_default()
                
            draw.text((width//2 - 250, 80), "Certificate of Completion", fill=(0, 0, 100), font=title_font)
            draw.text((width//2 - 150, 200), "This certifies that", fill=(0, 0, 0), font=text_font)
            draw.text((width//2 - 200, 300), recipient_name, fill=(0, 0, 150), font=name_font)
            draw.text((width//2 - 200, 400), f"has successfully completed", fill=(0, 0, 0), font=text_font)
            draw.text((width//2 - 100, 450), course_name, fill=(0, 0, 150), font=text_font)
            draw.text((width//2 - 150, 550), f"Date: {issue_date.strftime('%B %d, %Y')}", fill=(0, 0, 0), font=small_font)
            draw.text((width//2 - 150, 600), f"ID: {certificate_uid}", fill=(0, 0, 0), font=small_font)
            
            try:
                qr_img = Image.open(qr_filename).resize((120, 120))
                img.paste(qr_img, (width - 150, 50))
                draw.text((width - 145, 35), "Scan to verify", fill=(0, 0, 0), font=small_font)
            except Exception:
                pass
                
        # Finally, save exactly as PDF
        img.save(output_path, "PDF", resolution=100.0)
        return output_path
        
    def create_certificate_with_image(self, *args, **kwargs):
        # We can route this fallback to the PDF logic since it now guarantees perfect alignment
        pass
