class MeasurementEngine:

    def __init__(self):
        print("Measurement engine ready.")

    def measure(self, geometry, calibration):

        # Check geometry
        if not geometry or not geometry.get("detected"):

            return {
                "measured": False,
                "message": "No component available for measurement."
            }

        # Check calibration
        if not calibration or not calibration.get("calibrated"):

            return {
                "measured": False,
                "message": "Calibration required before measurement."
            }

        # Get scale
        mm_per_pixel = calibration["scale"]["mm_per_pixel"]

        # Get pixel dimensions
        pixel_dimensions = geometry["pixel_dimensions"]

        rotated_dimensions = geometry["rotated_dimensions"]

        pixel_width = pixel_dimensions["width"]
        pixel_height = pixel_dimensions["height"]

        long_pixels = rotated_dimensions["long"]
        short_pixels = rotated_dimensions["short"]

        # Convert pixels to millimetres
        width_mm = pixel_width * mm_per_pixel
        height_mm = pixel_height * mm_per_pixel

        long_mm = long_pixels * mm_per_pixel
        short_mm = short_pixels * mm_per_pixel

        # Simple demo uncertainty estimate.
        # This is NOT certified metrology uncertainty.
        uncertainty_mm = max(
            2.0 * mm_per_pixel,
            long_mm * 0.02
        )

        return {

            "measured": True,

            "measurement_source": "Computer Vision + calibrated reference",

            "scale": {
                "mm_per_pixel": round(
                    mm_per_pixel,
                    6
                )
            },

            "dimensions": {

                "width_mm": round(
                    width_mm,
                    2
                ),

                "height_mm": round(
                    height_mm,
                    2
                ),

                "length_mm": round(
                    long_mm,
                    2
                ),

                "short_dimension_mm": round(
                    short_mm,
                    2
                )
            },

            "uncertainty": {

                "estimated_uncertainty_mm": round(
                    uncertainty_mm,
                    2
                ),

                "note":
                    "Demo estimate based on image measurement. "
                    "Not certified metrology."
            }
        }