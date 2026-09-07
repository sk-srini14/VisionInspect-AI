import cv2
import numpy as np


class CalibrationDetector:

    def __init__(self):
        print("Calibration detector ready.")

    def detect_reference(self, image, reference_width_mm=50.0):

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        edges = cv2.Canny(
            blurred,
            50,
            150
        )

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        image_area = image.shape[0] * image.shape[1]

        candidates = []

        for contour in contours:

            area = cv2.contourArea(contour)

            if area < image_area * 0.005:
                continue

            perimeter = cv2.arcLength(
                contour,
                True
            )

            approx = cv2.approxPolyDP(
                contour,
                0.02 * perimeter,
                True
            )

            # Look for rectangular reference
            if len(approx) == 4:

                x, y, w, h = cv2.boundingRect(
                    approx
                )

                if w > 30 and h > 20:

                    candidates.append({
                        "contour": contour,
                        "x": x,
                        "y": y,
                        "width": w,
                        "height": h,
                        "area": area
                    })

        if not candidates:

            return {
                "calibrated": False,
                "message": "Calibration reference not detected."
            }

        # Choose the largest rectangular candidate
        reference = max(
            candidates,
            key=lambda item: item["area"]
        )

        pixel_width = float(reference["width"])
        pixel_height = float(reference["height"])

        # Use the larger dimension as reference width
        pixel_reference = max(
            pixel_width,
            pixel_height
        )

        mm_per_pixel = (
            reference_width_mm / pixel_reference
        )

        return {
            "calibrated": True,

            "reference": {
                "width_mm": reference_width_mm,
                "width_pixels": round(pixel_reference, 2),
                "bbox": [
                    reference["x"],
                    reference["y"],
                    reference["x"] + reference["width"],
                    reference["y"] + reference["height"]
                ]
            },

            "scale": {
                "mm_per_pixel": round(
                    mm_per_pixel,
                    6
                ),

                "pixels_per_mm": round(
                    1.0 / mm_per_pixel,
                    3
                )
            }
        }