import torch
from torch.nn.modules.container import Sequential
from ultralytics.nn.tasks import DetectionModel

# Allow YOLO models to load
torch.serialization.add_safe_globals([
    Sequential,
    DetectionModel
])

from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from typing import List, Dict, Tuple
from collections import Counter



class DocumentInspector:
    def __init__(self, model_configs: List[Dict[str, any]], device: str = "cpu", imgsz: int = 1280):
        """
        Initialize with multiple models using cropper-style inference.
        
        Args:
            model_configs: List of dicts with keys:
                - 'path': str, path to model file
                - 'conf_threshold': float, confidence threshold (default 0.25)
                - 'name': str, optional name for the model (for debugging)
            device: Device to run inference on ('cpu', 'cuda', '0', etc.)
            imgsz: Inference image size for 'slight zoom' effect (default 1280)
        
        Example:
            model_configs = [
                {"path": "./models/qrcode.pt", "conf_threshold": 0.65},
                {"path": "./models/signature.pt", "conf_threshold": 0.25},
            ]
        """
        self.models = []
        self.device = device if device else "cpu"
        self.imgsz = imgsz
        
        for config in model_configs:
            model_path = config["path"]
            conf_threshold = config.get("conf_threshold", 0.25)
            model_name = config.get("name", model_path)
            
            model = YOLO(model_path)
            model.to(self.device)
            
            self.models.append({
                "model": model,
                "conf_threshold": conf_threshold,
                "name": model_name
            })
        
        # Statistics tracking
        self.total_detections = 0
        self.class_statistics = Counter()

    def detect_image(self, pil_image: Image.Image) -> Tuple[List[Dict], Image.Image]:
        """
        Run YOLO inference on a PIL image using all loaded models with cropper parameters.
        Merges detections from all models using native YOLO prediction.
        
        Returns:
            - detections: List of detection dicts with merged results from all models
            - annotated_pil_image: PIL.Image with all detections visualized
        """
        img_np = np.array(pil_image)
        all_detections = []
        
        # Run inference with each model using cropper-style parameters
        for model_info in self.models:
            model = model_info["model"]
            conf_threshold = model_info["conf_threshold"]
            model_name = model_info["name"]
            
            # Use native YOLO prediction with cropper parameters
            results = model.predict(
                source=img_np,
                imgsz=self.imgsz,      # 'Slight zoom' effect from cropper
                conf=conf_threshold,
                iou=0.5,               # IOU threshold from cropper (don't change)
                device=self.device,
                verbose=False,
                stream=False
            )
            result = results[0]
            
            # Extract detections from this model
            for box in result.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                class_name = result.names[cls]
                
                all_detections.append({
                    "class": class_name,
                    "confidence": conf,
                    "bbox": [x1, y1, x2, y2],
                    "model": model_name
                })
                
                # Update statistics
                self.class_statistics[class_name] += 1
        
        self.total_detections += len(all_detections)
        
        # Draw all detections on the image
        annotated_pil = self._draw_all_detections(pil_image.copy(), all_detections)
        
        return all_detections, annotated_pil
    
    def get_statistics(self) -> Dict:
        """Get detection statistics across all processed images."""
        return {
            "total_detections": self.total_detections,
            "class_statistics": dict(self.class_statistics)
        }
    
    def reset_statistics(self):
        """Reset detection statistics."""
        self.total_detections = 0
        self.class_statistics.clear()
    
    def _draw_all_detections(self, image: Image.Image, detections: List[Dict]) -> Image.Image:
        """Draw all detections from all models on the image with labels showing percentages."""
        draw = ImageDraw.Draw(image)
        
        # Try to load a larger, bold font
        try:
            font = ImageFont.truetype("arial.ttf", 32)  # Larger font size
        except:
            try:
                font = ImageFont.truetype("Arial Bold.ttf", 32)
            except:
                font = ImageFont.load_default()
        
        # Define colors for different classes
        colors = {
            "qr_code": (0, 0, 255),      # Blue
            "signature": (255, 0, 0),     # Red
            "stamp": (0, 255, 0),         # Green
        }
        default_color = (255, 165, 0)  # Orange for unknown classes
        
        for detection in detections:
            class_name = detection["class"]
            confidence = detection["confidence"]
            x1, y1, x2, y2 = detection["bbox"]
            
            # Get color for this class
            color = colors.get(class_name, default_color)
            
            # Draw bounding box with thicker lines (width=5 for bolder appearance)
            draw.rectangle([x1, y1, x2, y2], outline=color, width=5)
            
            # Draw label with percentage
            label = f"{class_name} {confidence:.0%}"  # Shows as "qr_code 95%"
            
            # Calculate text size and draw background
            bbox = draw.textbbox((x1, y1 - 40), label, font=font)
            draw.rectangle(bbox, fill=color)
            draw.text((x1, y1 - 40), label, fill="white", font=font)
        
        return image


