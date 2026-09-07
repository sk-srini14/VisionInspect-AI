from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import cv2
import numpy as np
import os
import uuid

from app.vision.detector import ComponentDetector
from app.vision.geometry_detector import GeometryDetector
from app.vision.calibration import CalibrationDetector
from app.measurement.measurement import MeasurementEngine
from app.standards.database import StandardsDatabase
from app.standards.fastener_matcher import FastenerMatcher
from app.inspection.defect_detector import DefectDetector
from app.reports.pdf_report import InspectionReport


app = FastAPI(
    title="VisionInspect-AI",
    version="0.1.0",
    description="AI-assisted smartphone mechanical component inspection."
)


# Allow our frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# INITIALIZE VISIONINSPECT-AI MODULES
# ============================================

detector = ComponentDetector()

geometry_detector = GeometryDetector()

calibration_detector = CalibrationDetector()

measurement_engine = MeasurementEngine()

standards_db = StandardsDatabase()

fastener_matcher = FastenerMatcher(
    standards_db
)

defect_detector = DefectDetector()

report_generator = InspectionReport()


# ============================================
# REPORT STORAGE
# ============================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "reports",
    "generated"
)

UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "reports",
    "uploads"
)

os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Make generated reports accessible through the API
app.mount(
    "/reports",
    StaticFiles(directory=os.path.join(BASE_DIR, "reports")),
    name="reports"
)


# ============================================
# API HEALTH
# ============================================

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "VisionInspect-AI"
    }


@app.get("/api")
def root():
    return {
        "project": "VisionInspect-AI",
        "message": "AI-assisted mechanical component inspection API"
    }


# ============================================
# INSPECTION API
# ============================================

@app.post("/api/inspect")
async def inspect_image(file: UploadFile = File(...)):

    # ----------------------------------------
    # Read uploaded image
    # ----------------------------------------

    image_bytes = await file.read()

    # Convert uploaded bytes into an OpenCV image
    image_array = np.frombuffer(
        image_bytes,
        np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    # Check whether image was decoded successfully
    if image is None:
        return {
            "status": "error",
            "message": "Could not read the uploaded image."
        }

    height, width, channels = image.shape


    # ========================================
    # AI COMPONENT DETECTION
    # ========================================

    detections = detector.detect(image)


    # ========================================
    # GEOMETRY DETECTION
    # ========================================

    geometry = geometry_detector.detect(
        image
    )


    # ========================================
    # CALIBRATION
    # ========================================

    calibration = calibration_detector.detect_reference(
        image,
        reference_width_mm=50.0
    )

    print("\n--- CALIBRATION ---")
    print(calibration)
    print("-------------------\n")


    # ========================================
    # ENGINEERING MEASUREMENT
    # ========================================

    measurement = measurement_engine.measure(
        geometry,
        calibration
    )

    print("\n--- MEASUREMENT ---")
    print(measurement)
    print("-------------------\n")


    # ========================================
    # FASTENER STANDARDS MATCHING
    # ========================================

    fastener_match = fastener_matcher.match(
        "bolt",
        measurement["dimensions"]["length_mm"]
        if measurement.get("measured")
        else None
    )

    print("\n--- FASTENER STANDARDS MATCH ---")
    print(fastener_match)
    print("--------------------------------\n")


    # ========================================
    # VISUAL DEFECT INSPECTION
    # ========================================

    defect_inspection = defect_detector.inspect(
        image,
        geometry
    )

    print("\n--- VISUAL INSPECTION ---")
    print(defect_inspection)
    print("-------------------------\n")


    # ========================================
    # SAVE ORIGINAL IMAGE
    # ========================================

    inspection_id = str(
        uuid.uuid4()
    )

    image_filename = (
        f"{inspection_id}.jpg"
    )

    image_path = os.path.join(
        UPLOAD_DIR,
        image_filename
    )

    cv2.imwrite(
        image_path,
        image
    )


    # ========================================
    # GENERATE PDF REPORT
    # ========================================

    report_filename = (
        f"inspection_report_{inspection_id}.pdf"
    )

    report_path = os.path.join(
        REPORT_DIR,
        report_filename
    )

    report_generator.generate(
        output_path=report_path,
        image_path=image_path,
        filename=file.filename,
        image_info={
            "width": width,
            "height": height
        },
        geometry=geometry,
        calibration=calibration,
        measurement=measurement,
        standards=fastener_match,
        defect=defect_inspection
    )


    # ========================================
    # REPORT URL
    # ========================================

    report_url = (
        f"/reports/generated/{report_filename}"
    )


    # ========================================
    # FINAL RESPONSE
    # ========================================

    return {
        "status": "inspection_complete",

        "filename": file.filename,

        "image": {
            "width": width,
            "height": height
        },

        "ai_detections": detections,

        "geometry_detection": geometry,

        "calibration": calibration,

        "measurement": measurement,

        "standards_match": fastener_match,

        "defect_inspection": defect_inspection,

        "report": {
            "generated": True,
            "filename": report_filename,
            "url": report_url
        }
    }