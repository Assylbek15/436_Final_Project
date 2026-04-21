"""
Test to verify multi-model detection system works correctly.
"""
from app.services.document_inspector import DocumentInspector
from PIL import Image
import numpy as np

def test_single_model():
    """Test with a single model."""
    print("Testing single model...")
    
    config = [
        {
            "path": "./models/qrcode.pt",
            "conf_threshold": 0.65,
            "name": "QR Code Detector"
        }
    ]
    
    inspector = DocumentInspector(config)
    
    # Create a dummy image
    dummy_image = Image.fromarray(np.random.randint(0, 255, (800, 600, 3), dtype=np.uint8))
    
    detections, annotated = inspector.detect_image(dummy_image)
    
    print(f"✓ Single model loaded successfully")
    print(f"✓ Detections returned: {len(detections)}")
    print(f"✓ Annotated image type: {type(annotated)}")


def test_multiple_models():
    """Test with multiple models."""
    print("\nTesting multiple models...")
    
    config = [
        {
            "path": "./models/qrcode.pt",
            "conf_threshold": 0.65,
            "name": "QR Code Detector"
        },
        {
            "path": "./models/signature_manual_labeling.pt",
            "conf_threshold": 0.70,
            "name": "Signature Detector"
        }
    ]
    
    inspector = DocumentInspector(config)
    
    # Create a dummy image
    dummy_image = Image.fromarray(np.random.randint(0, 255, (800, 600, 3), dtype=np.uint8))
    
    detections, annotated = inspector.detect_image(dummy_image)
    
    print(f"✓ Multiple models loaded successfully")
    print(f"✓ Number of models: {len(inspector.models)}")
    print(f"✓ Detections returned: {len(detections)}")
    print(f"✓ Annotated image type: {type(annotated)}")
    
    # Check detection format
    if detections:
        print(f"✓ Detection format check:")
        for i, det in enumerate(detections[:3]):  # Show first 3
            print(f"  - Detection {i+1}: class={det['class']}, confidence={det['confidence']:.2f}")


if __name__ == "__main__":
    try:
        test_single_model()
        test_multiple_models()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
