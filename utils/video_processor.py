import cv2
import mediapipe as mp
import numpy as np
import base64
from PIL import Image, ImageEnhance
import io
import os
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5
        )
        logger.info("VideoProcessor initialized")

    def enhance_image(self, image):
        """Enhance the extracted image quality"""
        try:
            # Convert to PIL Image for better processing
            image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image_pil)
            image_pil = enhancer.enhance(1.5)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image_pil)
            image_pil = enhancer.enhance(1.2)
            
            # Enhance color
            enhancer = ImageEnhance.Color(image_pil)
            image_pil = enhancer.enhance(1.1)
            
            # Convert back to OpenCV format
            enhanced = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
            
            # Apply denoising
            enhanced = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)
            
            return enhanced
        except Exception as e:
            logger.error(f"Error in enhance_image: {str(e)}")
            raise

    def upscale_image(self, image):
        """Upscale the image resolution"""
        try:
            # Get original dimensions
            h, w = image.shape[:2]
            logger.info(f"Upscaling image from {w}x{h}")
            
            # Upscale by 2x using LANCZOS
            upscaled = cv2.resize(image, (w*2, h*2), interpolation=cv2.INTER_LANCZOS4)
            
            # Apply sharpening after upscaling
            kernel = np.array([[-1,-1,-1],
                             [-1, 9,-1],
                             [-1,-1,-1]])
            upscaled = cv2.filter2D(upscaled, -1, kernel)
            
            return upscaled
        except Exception as e:
            logger.error(f"Error in upscale_image: {str(e)}")
            raise

    def process_video(self, video_path, frame_rate=10, confidence_threshold=0.5):
        logger.info(f"Processing video: {video_path} with frame_rate={frame_rate}, confidence={confidence_threshold}")
        
        try:
            # Create directories if they don't exist
            os.makedirs('uploads', exist_ok=True)
            os.makedirs('extracted', exist_ok=True)
            
            # Generate timestamp for this batch
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            batch_dir = os.path.join('extracted', timestamp)
            os.makedirs(batch_dir, exist_ok=True)
            
            # Save the uploaded video
            video_name = f"video_{timestamp}.mp4"
            saved_video_path = os.path.join('uploads', video_name)
            if video_path != saved_video_path:  # Only copy if it's not already in uploads
                import shutil
                shutil.copy2(video_path, saved_video_path)
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
                
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            logger.info(f"Video info - Total frames: {total_frames}, FPS: {fps}")
            
            extracted_images = []
            frame_count = 0
            processed_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_rate == 0:
                    logger.debug(f"Processing frame {frame_count}/{total_frames}")
                    
                    # Convert BGR to RGB for pose detection
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Detect pose
                    results = self.pose.process(rgb_frame)
                    
                    if results.pose_landmarks:
                        # Check confidence
                        visibility = results.pose_landmarks.landmark[0].visibility
                        if visibility > confidence_threshold:
                            logger.debug(f"Human detected in frame {frame_count} with confidence {visibility}")
                            
                            # Get bounding box
                            h, w, _ = frame.shape
                            landmarks = results.pose_landmarks.landmark
                            
                            x_coords = [lm.x * w for lm in landmarks]
                            y_coords = [lm.y * h for lm in landmarks]
                            
                            # Add padding
                            padding = 0.2
                            x_min = max(0, int(min(x_coords) - padding * w))
                            x_max = min(w, int(max(x_coords) + padding * w))
                            y_min = max(0, int(min(y_coords) - padding * h))
                            y_max = min(h, int(max(y_coords) + padding * h))
                            
                            # Extract person
                            if x_max > x_min and y_max > y_min:
                                person = frame[y_min:y_max, x_min:x_max]
                                
                                # Enhance and upscale
                                enhanced = self.enhance_image(person)
                                upscaled = self.upscale_image(enhanced)
                                
                                # Save the image
                                img_name = f"frame_{frame_count:06d}.jpg"
                                img_path = os.path.join(batch_dir, img_name)
                                cv2.imwrite(img_path, upscaled, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                                
                                # Convert to base64 for display
                                with open(img_path, 'rb') as img_file:
                                    img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                                    extracted_images.append({
                                        'base64': img_base64,
                                        'path': img_path,
                                        'frame': frame_count,
                                        'timestamp': timestamp
                                    })
                                processed_count += 1
                                logger.info(f"Successfully extracted image {processed_count} from frame {frame_count}")
                
                frame_count += 1
            
            cap.release()
            logger.info(f"Video processing completed. Extracted {len(extracted_images)} images from {frame_count} frames")
            
            # Save metadata
            metadata = {
                'video_path': saved_video_path,
                'timestamp': timestamp,
                'frame_rate': frame_rate,
                'confidence_threshold': confidence_threshold,
                'total_frames': total_frames,
                'processed_frames': frame_count,
                'extracted_images': len(extracted_images)
            }
            
            metadata_path = os.path.join(batch_dir, 'metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=4)
            
            return extracted_images
            
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            raise
        finally:
            if 'cap' in locals() and cap is not None:
                cap.release()
