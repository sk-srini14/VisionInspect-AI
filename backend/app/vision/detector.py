from ultralytics import YOLO


class ComponentDetector:

    def __init__(self):
        print("Loading VisionInspect-AI detection model...")

        self.model = YOLO("yolov8s-worldv2.pt")

        self.classes = [
            "bolt",
            "screw",
            "hex screw",
            "hex bolt",
            "fastener",
            "mechanical fastener",
            "washer",
            "gear",
            "ruler",
            "caliper",
            "calibration marker"
        ]

        self.model.set_classes(self.classes)

        print("Detection model ready.")
        print("Detection classes:", self.classes)

    def detect(self, image):

        results = self.model.predict(
            source=image,
            conf=0.01,
            verbose=False
        )

        detections = []

        print("\n--- AI DETECTIONS ---")

        for result in results:

            if result.boxes is None or len(result.boxes) == 0:
                print("No boxes returned.")
                continue

            for box in result.boxes:

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                print(
                    f"Class: {self.classes[class_id]} | "
                    f"Confidence: {confidence:.3f} | "
                    f"Box: "
                    f"({round(x1)}, {round(y1)}, "
                    f"{round(x2)}, {round(y2)})"
                )

                mechanical_classes = {
                    "bolt",
                    "screw",
                    "hex screw",
                    "hex bolt",
                    "fastener",
                    "mechanical fastener",
                    "washer",
                    "gear"
                }

                if (
                    self.classes[class_id] in mechanical_classes
                    and confidence >= 0.01
                ):

                    detections.append({
                        "class": self.classes[class_id],
                        "confidence": round(confidence, 3),
                        "bbox": [
                            round(x1),
                            round(y1),
                            round(x2),
                            round(y2)
                        ]
                    })

        print("---------------------\n")

        return detections