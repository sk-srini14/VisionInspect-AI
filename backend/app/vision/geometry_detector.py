import cv2
import numpy as np


class GeometryDetector:

    def __init__(self):
        print("Geometry detector ready.")

    def detect(self, image):

        # Convert image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Smooth small image noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Separate the mechanical object from a bright background
        _, threshold = cv2.threshold(
            blurred,
            230,
            255,
            cv2.THRESH_BINARY_INV
        )

        # Clean small gaps/noise
        kernel = np.ones((5, 5), np.uint8)

        threshold = cv2.morphologyEx(
            threshold,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=2
        )

        # Find contours
        contours, _ = cv2.findContours(
            threshold,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            return {
                "detected": False,
                "message": "No foreground object detected."
            }

        # Select the largest meaningful contour
        image_area = image.shape[0] * image.shape[1]

        valid_contours = []

        for contour in contours:

            area = cv2.contourArea(contour)

            # Ignore tiny noise and objects occupying almost the whole image
            if area > image_area * 0.01 and area < image_area * 0.90:
                valid_contours.append(contour)

        if not valid_contours:
            return {
                "detected": False,
                "message": "No suitable mechanical object found."
            }

        contour = max(
            valid_contours,
            key=cv2.contourArea
        )

        # Axis-aligned bounding box
        x, y, width, height = cv2.boundingRect(contour)

        # Rotated bounding rectangle
        rotated_rect = cv2.minAreaRect(contour)

        center, size, angle = rotated_rect

        rotated_width = float(size[0])
        rotated_height = float(size[1])

        # Ensure width represents the longer dimension
        if rotated_height > rotated_width:
            long_dimension = rotated_height
            short_dimension = rotated_width
        else:
            long_dimension = rotated_width
            short_dimension = rotated_height

        return {
            "detected": True,

            "object_type": "mechanical_component",

            "bbox": [
                int(x),
                int(y),
                int(x + width),
                int(y + height)
            ],

            "pixel_dimensions": {
                "width": round(float(width), 2),
                "height": round(float(height), 2)
            },

            "rotated_dimensions": {
                "long": round(long_dimension, 2),
                "short": round(short_dimension, 2)
            },

            "orientation_angle": round(float(angle), 2),

            "contour_area": round(
                float(cv2.contourArea(contour)),
                2
            )
        }