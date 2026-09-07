import cv2
import numpy as np


class DefectDetector:

    def __init__(self):
        print("Visual inspection module ready.")

    def inspect(self, image, geometry):

        if not geometry or not geometry.get("detected"):

            return {
                "inspected": False,
                "status": "INSUFFICIENT_DATA",
                "message":
                    "Visual inspection requires a detected component."
            }

        bbox = geometry["bbox"]

        x1, y1, x2, y2 = bbox

        # Keep coordinates inside image
        height, width = image.shape[:2]

        x1 = max(0, min(x1, width - 1))
        x2 = max(0, min(x2, width))
        y1 = max(0, min(y1, height - 1))
        y2 = max(0, min(y2, height))

        if x2 <= x1 or y2 <= y1:

            return {
                "inspected": False,
                "status": "INSUFFICIENT_DATA",
                "message": "Invalid component region."
            }

        # Crop component
        crop = image[y1:y2, x1:x2]

        if crop.size == 0:

            return {
                "inspected": False,
                "status": "INSUFFICIENT_DATA",
                "message": "Component image is unavailable."
            }

        # Convert to grayscale
        gray = cv2.cvtColor(
            crop,
            cv2.COLOR_BGR2GRAY
        )

        # Detect strong local edges
        edges = cv2.Canny(
            gray,
            80,
            180
        )

        # Remove tiny isolated regions
        kernel = np.ones(
            (3, 3),
            np.uint8
        )

        cleaned = cv2.morphologyEx(
            edges,
            cv2.MORPH_OPEN,
            kernel
        )

        edge_pixels = np.count_nonzero(cleaned)
        total_pixels = cleaned.shape[0] * cleaned.shape[1]

        edge_ratio = (
            edge_pixels / total_pixels
            if total_pixels > 0
            else 0
        )

        # This is a visual screening heuristic,
        # NOT a certified defect classifier.

        if edge_ratio > 0.18:

            status = "WARNING"

            message = (
                "High surface-edge activity detected. "
                "Manual inspection recommended."
            )

        else:

            status = "PASS"

            message = (
                "No significant visual anomaly detected "
                "by the screening algorithm."
            )

        return {

            "inspected": True,

            "status": status,

            "edge_activity_ratio":
                round(edge_ratio, 4),

            "message": message,

            "inspection_source":
                "Computer Vision visual screening",

            "confidence":
                "LOW",

            "note":
                "This is a visual anomaly screening result, "
                "not a certified manufacturing defect inspection."
        }