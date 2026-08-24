---
title: Computer Vision
description: OpenCV, image processing, object detection, YOLO and image classification
---

# Computer Vision <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🤖 AI Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="../data/intermediate/numpy/">NumPy</a></span>
  </div>
</div>

---

## OpenCV basics

```python
import cv2
import numpy as np

# ─── Read and display ─────────────────────────────
img = cv2.imread("photo.jpg")
print(f"Shape: {img.shape}")   # (height, width, channels) e.g. (480, 640, 3)
print(f"Dtype: {img.dtype}")   # uint8

# Convert BGR → RGB (OpenCV uses BGR by default)
rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Resize
resized = cv2.resize(img, (300, 200))   # (width, height)
resized = cv2.resize(img, None, fx=0.5, fy=0.5)   # scale by factor

# Crop (just NumPy slicing)
cropped = img[100:300, 200:400]   # [y1:y2, x1:x2]

# Save
cv2.imwrite("output.jpg", img)

# ─── Drawing ──────────────────────────────────────
canvas = np.zeros((400, 600, 3), dtype=np.uint8)
cv2.rectangle(canvas, (50, 50), (200, 150), (0, 255, 0), 2)        # green rectangle
cv2.circle(canvas, (300, 200), 80, (255, 0, 0), -1)                # filled blue circle
cv2.putText(canvas, "Hello", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
cv2.line(canvas, (400, 50), (550, 350), (0, 0, 255), 3)            # red line
```

---

## Image processing

```python
# ─── Color spaces ─────────────────────────────────
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# ─── Blurring ────────────────────────────────────
blurred = cv2.GaussianBlur(img, (5, 5), 0)
median = cv2.medianBlur(img, 5)

# ─── Edge detection ──────────────────────────────
edges = cv2.Canny(gray, 50, 150)   # min/max thresholds

# ─── Thresholding ────────────────────────────────
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

# ─── Contour detection ───────────────────────────
contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(img, contours, -1, (0, 255, 0), 2)
print(f"Found {len(contours)} contours")

# ─── Template matching ───────────────────────────
template = cv2.imread("button.png", cv2.IMREAD_GRAYSCALE)
result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
print(f"Best match at {max_loc} with score {max_val:.4f}")
```

---

## Object detection with YOLO

```python
from ultralytics import YOLO

# Load pre-trained model
model = YOLO("yolov8n.pt")   # nano (fast), also s, m, l, x

# Detect objects in an image
results = model("street.jpg")

# Process results
for result in results:
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        label = model.names[class_id]
        print(f"  {label}: {confidence:.2f} at ({x1},{y1})-({x2},{y2})")

# Output:
#   person: 0.95 at (100,50)-(300,400)
#   car: 0.89 at (400,200)-(600,350)
#   dog: 0.78 at (50,300)-(150,420)

# Save annotated image
results[0].save("detected.jpg")

# ─── Video detection ──────────────────────────────
results = model("video.mp4", stream=True)
for frame_result in results:
    # Process each frame
    annotated = frame_result.plot()
```

---

## Image classification with PyTorch

```python
import torch
from torchvision import transforms, models
from PIL import Image

# Load pre-trained model
model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
model.eval()

# Preprocessing
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Predict
img = Image.open("cat.jpg")
input_tensor = preprocess(img).unsqueeze(0)   # add batch dimension

with torch.no_grad():
    output = model(input_tensor)
    probabilities = torch.nn.functional.softmax(output[0], dim=0)

# Top 5 predictions
top5 = torch.topk(probabilities, 5)
weights = models.ResNet50_Weights.DEFAULT
categories = weights.meta["categories"]
for score, idx in zip(top5.values, top5.indices):
    print(f"  {categories[idx]:30} {score.item():.4f}")
# tabby cat                      0.8732
# Egyptian cat                   0.0891
# tiger cat                      0.0234
# ...
```

---

## Practical applications

```python
# ─── Face detection ───────────────────────────────
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
for (x, y, w, h) in faces:
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

# ─── OCR (text from images) ──────────────────────
import pytesseract
text = pytesseract.image_to_string(img)
print(text)

# ─── Image similarity ────────────────────────────
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("clip-ViT-B-32")
img_embedding = model.encode(Image.open("cat.jpg"))
text_embedding = model.encode("a photo of a cat")
similarity = np.dot(img_embedding, text_embedding) / (
    np.linalg.norm(img_embedding) * np.linalg.norm(text_embedding)
)
print(f"Image-text similarity: {similarity:.4f}")   # ~0.3 for matching
```

---

## Practice Exercises

1. **Build a face counter** — count faces in photos using OpenCV.
2. **Build an object detector** — use YOLO to detect and label objects in a video stream.
3. **Image classifier** — use a pre-trained ResNet to classify uploaded images via a FastAPI endpoint.
4. **Document scanner** — detect document edges, perspective transform and OCR the text.
5. **Build a visual search** — given an image, find similar images in a database using CLIP embeddings.
6. **Real-time detection** — process webcam feed with YOLO and draw bounding boxes.
