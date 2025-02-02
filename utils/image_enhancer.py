import cv2
import numpy as np
from PIL import Image, ImageEnhance
import face_recognition
import torch
from torch import nn
import torch.nn.functional as F

class ImageEnhancer:
    def __init__(self):
        # Initialize CUDA if available
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def enhance_image(self, image_path, methods=None):
        """Apply multiple enhancement methods to an image"""
        if methods is None:
            methods = ['color', 'denoise', 'sharpen']
            
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        enhanced_img = img.copy()
        for method in methods:
            if method == 'color':
                enhanced_img = self.enhance_color(enhanced_img)
            elif method == 'denoise':
                enhanced_img = self.reduce_noise(enhanced_img)
            elif method == 'sharpen':
                enhanced_img = self.sharpen_image(enhanced_img)
            elif method == 'face':
                enhanced_img = self.enhance_faces(enhanced_img)
            elif method == 'super_res':
                enhanced_img = self.super_resolution(enhanced_img)
            elif method == 'hdr':
                enhanced_img = self.apply_hdr_effect(enhanced_img)
        
        # Convert back to BGR for saving
        enhanced_img = cv2.cvtColor(enhanced_img, cv2.COLOR_RGB2BGR)
        
        # Save enhanced image with suffix
        output_path = image_path.replace('.jpg', '_enhanced.jpg')
        cv2.imwrite(output_path, enhanced_img)
        return output_path
    
    def enhance_color(self, img):
        """Enhance color saturation and contrast"""
        # Convert to PIL Image for better color enhancement
        pil_img = Image.fromarray(img)
        
        # Enhance color saturation
        enhancer = ImageEnhance.Color(pil_img)
        pil_img = enhancer.enhance(1.2)  # Increase saturation by 20%
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_img)
        pil_img = enhancer.enhance(1.1)  # Increase contrast by 10%
        
        # Convert back to numpy array
        return np.array(pil_img)
    
    def reduce_noise(self, img):
        """Apply advanced noise reduction"""
        # Non-local means denoising
        return cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    
    def sharpen_image(self, img):
        """Apply adaptive sharpening"""
        blurred = cv2.GaussianBlur(img, (0, 0), 3)
        return cv2.addWeighted(img, 1.5, blurred, -0.5, 0)
    
    def enhance_faces(self, img):
        """Enhance detected faces in the image"""
        # Find face locations
        face_locations = face_recognition.face_locations(img)
        
        for top, right, bottom, left in face_locations:
            # Extract face region
            face = img[top:bottom, left:right]
            
            # Apply face-specific enhancements
            face = self.reduce_noise(face)  # Reduce noise
            face = self.enhance_color(face)  # Enhance colors
            
            # Smooth skin while preserving details
            face = cv2.bilateralFilter(face, 9, 75, 75)
            
            # Replace enhanced face in original image
            img[top:bottom, left:right] = face
        
        return img
    
    def super_resolution(self, img):
        """Apply super-resolution using bicubic interpolation"""
        # Scale up the image by 2x
        height, width = img.shape[:2]
        scaled = cv2.resize(img, (width*2, height*2), interpolation=cv2.INTER_CUBIC)
        
        # Scale back down to original size with enhanced details
        return cv2.resize(scaled, (width, height), interpolation=cv2.INTER_AREA)
    
    def apply_hdr_effect(self, img):
        """Apply HDR-like effect to the image"""
        # Convert to float32
        img_float = img.astype(np.float32) / 255.0
        
        # Apply local tone mapping
        # Split into luminance and color
        luminance = cv2.cvtColor(img_float, cv2.COLOR_RGB2LAB)[:,:,0]
        
        # Apply bilateral filter to create base layer
        base = cv2.bilateralFilter(luminance, 9, 0.1, 7)
        detail = luminance - base
        
        # Enhance local contrast
        enhanced_base = np.clip((base - 0.5) * 1.2 + 0.5, 0, 1)
        enhanced_luminance = enhanced_base + detail
        
        # Reconstruct image
        img_float = cv2.cvtColor(img, cv2.COLOR_RGB2LAB).astype(np.float32)
        img_float[:,:,0] = enhanced_luminance * 255
        enhanced = cv2.cvtColor(img_float.astype(np.uint8), cv2.COLOR_LAB2RGB)
        
        return enhanced

    def batch_enhance(self, image_paths, methods=None):
        """Enhance multiple images with progress tracking"""
        enhanced_paths = []
        total = len(image_paths)
        
        for i, path in enumerate(image_paths, 1):
            try:
                enhanced_path = self.enhance_image(path, methods)
                enhanced_paths.append(enhanced_path)
                print(f"Enhanced {i}/{total}: {path}")
            except Exception as e:
                print(f"Error enhancing {path}: {str(e)}")
                continue
        
        return enhanced_paths
