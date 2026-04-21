# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license

import argparse
import cv2
import numpy as np
import sys
from collections import Counter
from ultralytics import YOLO
from ultralytics.utils.files import increment_path
from ultralytics.utils.plotting import Annotator, colors
# NOTE: The Counter import is now less relevant as native YOLO prediction handles directory processing


class YOLOInference:
    """Runs Ultralytics YOLO inference on a source (file, directory, or stream),
    controlling the input size (imgsz) to manage downscaling ('slight zoom').
    """

    def __init__(self):
        """Initialize the YOLOInference class."""
        self.model = None

    def load_model(self, weights: str, device: str) -> None:
        """Load a YOLO model with specified weights."""
        if not device:
            device = 'cpu'
            print("WARNING: Device argument was empty. Falling back to 'cpu'.")

        self.model = YOLO(weights)
        self.model.to(device)

    def inference(
        self,
        weights: str = "yolo11n.pt",
        source: str = "test.mp4",
        view_img: bool = False,
        save_img: bool = False,
        exist_ok: bool = False,
        device: str = "",
        hide_conf: bool = False,
        imgsz: int = 1280, # Set a higher default for the 'slight zoom' effect
        bbox_thickness: int = 1,
        hide_labels: bool = True,
    ) -> None:
        """Run object detection on the specified source (file or directory) using YOLO."""

        # Output setup (remains the same)
        save_dir = increment_path("runs/detect/predict", exist_ok)
        save_dir.mkdir(parents=True, exist_ok=True)

        # Load model
        self.load_model(weights, device)

        # ⭐ CORE CHANGE: Use native YOLO model prediction for directory processing ⭐
        # This handles iterating over all images in the directory path provided by 'source'.
        results = self.model.predict(
            source=source,
            imgsz=imgsz,
            save=save_img, # Use native YOLO saving instead of manual cv2.imwrite
            save_conf=not hide_conf, # Save confidence in labels
            show=view_img, # Use native YOLO showing
            device=device,
            stream=False, # We use stream=False for file/directory processing
            project='runs/detect',
            name=save_dir.name, # Use the generated incremented name
            exist_ok=True, # Directory is already handled by increment_path
            # Set visualization style arguments
            conf=0.25, # Default confidence threshold
            line_thickness=bbox_thickness,
            show_labels=not hide_labels,
            show_conf=not hide_conf,
            verbose=True,
            iou=0.5
        )

        # Print final statistics based on the results list
        total_detections = 0
        total_counts = Counter()

        # Iterate through the list of result objects (one per image/video frame)
        for i, res in enumerate(results):
            detected_count = len(res.boxes)
            total_detections += detected_count

            # Get class-specific counts for the current result
            names = res.names if hasattr(res, 'names') else {k: str(k) for k in range(100)}
            class_names = [names[int(cls)] for cls in res.boxes.cls]
            current_counts = Counter(class_names)
            total_counts.update(current_counts)

            # Optional: Print per-image stats (YOLO already prints overall progress)
            print(f"--- Image {i + 1} ({detected_count} Detections) ---")
            print(f"Class Statistics for Image: {current_counts}")

        print("\n--- INFERENCE COMPLETE ---")
        print(f"TOTAL OBJECTS DETECTED ACROSS ALL FILES: {total_detections}")
        print(f"OVERALL CLASS STATISTICS: {total_counts}")


    @staticmethod
    def parse_opt(args=None) -> argparse.Namespace:
        """Parse command line arguments for the inference process."""
        parser = argparse.ArgumentParser()
        parser.add_argument("--weights", type=str, default="yolo11n.pt", help="initial weights path")
        parser.add_argument("--source", type=str, required=True, help="file, folder, or stream source")
        parser.add_argument("--view-img", action="store_true", help="show results")
        parser.add_argument("--save-img", action="store_true", help="save results")
        parser.add_argument("--exist-ok", action="store_true", help="existing project/name ok, do not increment")
        parser.add_argument("--device", default="", help="cuda device, i.e. 0 or 0,1,2,3 or cpu")

        parser.add_argument("--hide-conf", default=False, action="store_true", help="display or hide confidences")
        parser.add_argument("--imgsz", default=1280, type=int, help="Inference image size. Use a larger value (e.g., 1280) for 'slight zoom' effect.")
        parser.add_argument("--bbox-thickness", type=int, default=1, help="Bounding box line thickness")
        parser.add_argument("--hide-labels", action="store_true", help="Hide labels from visualization")

        return parser.parse_args(args)


if __name__ == "__main__":

    # ⭐ COLAB EXECUTION FIX: Source set to directory path ⭐
    COLAB_ARGS = [
        "--weights", "/content/danik&stamp.pt",
        "--source", "/content/sahi/data/", # FIX: Changed to the directory path
        "--imgsz", "1280",                 # 'Slight zoom' effect
        "--save-img",                      # Saves annotated images to runs/detect/predictX/
        "--device", "cuda",
    ]

    inference = YOLOInference()
    opt = inference.parse_opt(COLAB_ARGS)

    if opt.imgsz == 640:
        print("INFO: You are using the default imgsz=640. Try imgsz=1280 or 1920 for a 'slight zoom' effect.")

    inference.inference(**vars(opt))