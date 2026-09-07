from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as ReportImage
)

import os
from datetime import datetime


class InspectionReport:

    def __init__(self):
        print("PDF inspection report module ready.")

    def generate(
        self,
        output_path,
        image_path,
        filename,
        image_info,
        geometry,
        calibration,
        measurement,
        standards,
        defect
    ):

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True
        )

        document = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=20,
            spaceAfter=8
        )

        section_style = ParagraphStyle(
            "Section",
            parent=styles["Heading2"],
            fontSize=13,
            spaceBefore=10,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["BodyText"],
            fontSize=9,
            leading=12
        )

        story = []

        # ========================================
        # REPORT TITLE
        # ========================================

        story.append(
            Paragraph(
                "VisionInspect-AI",
                title_style
            )
        )

        story.append(
            Paragraph(
                "Mechanical Component Inspection Report",
                ParagraphStyle(
                    "Subtitle",
                    parent=body_style,
                    alignment=TA_CENTER,
                    fontSize=11
                )
            )
        )

        story.append(Spacer(1, 8))

        story.append(
            Paragraph(
                f"Generated: "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                body_style
            )
        )

        story.append(
            Paragraph(
                f"Input Image: {filename}",
                body_style
            )
        )

        story.append(Spacer(1, 8))


        # ========================================
        # INSPECTION IMAGE
        # ========================================

        if image_path and os.path.exists(image_path):

            story.append(
                Paragraph(
                    "Inspection Image",
                    section_style
                )
            )

            report_image = ReportImage(
                image_path
            )

            report_image._restrictSize(
                170 * mm,
                90 * mm
            )

            story.append(report_image)

            story.append(
                Spacer(1, 6)
            )


        # ========================================
        # IMAGE INFORMATION
        # ========================================

        story.append(
            Paragraph(
                "Image Information",
                section_style
            )
        )

        image_table = Table(
            [
                ["Property", "Value"],
                [
                    "Image Width",
                    f"{image_info.get('width', '-')} px"
                ],
                [
                    "Image Height",
                    f"{image_info.get('height', '-')} px"
                ]
            ],
            colWidths=[
                60 * mm,
                90 * mm
            ]
        )

        image_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        9
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE"
                    )
                ]
            )
        )

        story.append(image_table)


        # ========================================
        # CALIBRATION
        # ========================================

        story.append(
            Paragraph(
                "Calibration",
                section_style
            )
        )

        if calibration and calibration.get("calibrated"):

            reference = calibration["reference"]
            scale = calibration["scale"]

            calibration_data = [
                ["Property", "Value"],
                [
                    "Calibration Status",
                    "Calibrated"
                ],
                [
                    "Reference Size",
                    f"{reference['width_mm']:.2f} mm"
                ],
                [
                    "Reference Width",
                    f"{reference['width_pixels']:.1f} px"
                ],
                [
                    "Scale",
                    f"{scale['mm_per_pixel']:.6f} mm/pixel"
                ],
                [
                    "Pixels per mm",
                    f"{scale['pixels_per_mm']:.2f}"
                ]
            ]

        else:

            calibration_data = [
                ["Property", "Value"],
                [
                    "Calibration Status",
                    "Unavailable"
                ]
            ]

        calibration_table = Table(
            calibration_data,
            colWidths=[
                60 * mm,
                90 * mm
            ]
        )

        calibration_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        9
                    )
                ]
            )
        )

        story.append(calibration_table)


        # ========================================
        # ENGINEERING MEASUREMENTS
        # ========================================

        story.append(
            Paragraph(
                "Engineering Measurements",
                section_style
            )
        )

        if measurement and measurement.get("measured"):

            dimensions = measurement["dimensions"]
            uncertainty = measurement["uncertainty"]

            measurement_data = [
                ["Property", "Value"],
                [
                    "Length",
                    f"{dimensions['length_mm']:.2f} mm"
                ],
                [
                    "Width",
                    f"{dimensions['width_mm']:.2f} mm"
                ],
                [
                    "Short Dimension",
                    f"{dimensions['short_dimension_mm']:.2f} mm"
                ],
                [
                    "Estimated Uncertainty",
                    f"±{uncertainty['estimated_uncertainty_mm']:.2f} mm"
                ],
                [
                    "Measurement Source",
                    measurement["measurement_source"]
                ]
            ]

        else:

            measurement_data = [
                ["Property", "Value"],
                [
                    "Measurement Status",
                    "Unavailable"
                ]
            ]

        measurement_table = Table(
            measurement_data,
            colWidths=[
                60 * mm,
                90 * mm
            ]
        )

        measurement_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        9
                    )
                ]
            )
        )

        story.append(measurement_table)


        # ========================================
        # ENGINEERING STANDARDS
        # ========================================

        story.append(
            Paragraph(
                "Engineering Standards",
                section_style
            )
        )

        if standards and standards.get("matched"):

            standards_data = [
                ["Property", "Value"],
                [
                    "Status",
                    "STANDARD MATCHED"
                ],
                [
                    "Designation",
                    standards["designation"]
                ],
                [
                    "Component Type",
                    standards["component_type"]
                ],
                [
                    "Nominal Diameter",
                    f"{standards['nominal_diameter_mm']} mm"
                ],
                [
                    "Coarse Thread Pitch",
                    f"{standards['coarse_pitch_mm']} mm"
                ],
                [
                    "Measured Length",
                    f"{standards['measured_length_mm']} mm"
                ],
                [
                    "Standard Length",
                    f"{standards['standard_length_mm']} mm"
                ],
                [
                    "Difference",
                    f"{standards['difference_mm']} mm"
                ],
                [
                    "Confidence",
                    standards["confidence"]
                ],
                [
                    "Database Source",
                    standards["database_source"]
                ]
            ]

        else:

            standards_data = [
                ["Property", "Value"],
                [
                    "Status",
                    standards.get(
                        "status",
                        "Unavailable"
                    )
                ],
                [
                    "Message",
                    standards.get(
                        "message",
                        "No reliable standard match."
                    )
                ]
            ]

        standards_table = Table(
            standards_data,
            colWidths=[
                60 * mm,
                90 * mm
            ]
        )

        standards_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        9
                    )
                ]
            )
        )

        story.append(standards_table)


        # ========================================
        # VISUAL INSPECTION
        # ========================================

        story.append(
            Paragraph(
                "Visual Inspection",
                section_style
            )
        )

        if defect and defect.get("inspected"):

            defect_data = [
                ["Property", "Value"],
                [
                    "Inspection Status",
                    defect["status"]
                ],
                [
                    "Edge Activity",
                    str(
                        defect.get(
                            "edge_activity_ratio",
                            "-"
                        )
                    )
                ],
                [
                    "Confidence",
                    defect.get(
                        "confidence",
                        "-"
                    )
                ],
                [
                    "Inspection Source",
                    defect.get(
                        "inspection_source",
                        "-"
                    )
                ],
                [
                    "Result",
                    defect.get(
                        "message",
                        "-"
                    )
                ]
            ]

        else:

            defect_data = [
                ["Property", "Value"],
                [
                    "Inspection Status",
                    "INSUFFICIENT_DATA"
                ]
            ]

        defect_table = Table(
            defect_data,
            colWidths=[
                60 * mm,
                90 * mm
            ]
        )

        defect_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        9
                    )
                ]
            )
        )

        story.append(defect_table)


        # ========================================
        # MEASUREMENT & DECISION PROVENANCE
        # ========================================

        story.append(
            Paragraph(
                "Measurement & Decision Provenance",
                section_style
            )
        )

        provenance_text = """
        <b>Component identification:</b>
        AI vision when reliable; geometry-based fallback otherwise.<br/>
        <b>Geometric measurement:</b>
        Computer Vision using calibrated image scale.<br/>
        <b>Engineering specification:</b>
        Engineering Standards Database.<br/>
        <b>Visual inspection:</b>
        Computer Vision screening.<br/>
        <b>Uncertainty:</b>
        Estimated image-measurement uncertainty; not certified metrology.
        """

        story.append(
            Paragraph(
                provenance_text,
                body_style
            )
        )

        story.append(
            Spacer(1, 12)
        )


        # ========================================
        # ENGINEERING NOTE
        # ========================================

        story.append(
            Paragraph(
                "<b>Engineering Note:</b> "
                "Measurements and inspection results are AI-assisted "
                "visual estimates intended for engineering screening "
                "and decision support. They are not certified metrology "
                "measurements and should be validated using appropriate "
                "measurement equipment for production decisions.",
                ParagraphStyle(
                    "Disclaimer",
                    parent=body_style,
                    fontSize=8,
                    leading=10
                )
            )
        )


        # ========================================
        # BUILD PDF
        # ========================================

        document.build(story)

        print(
            f"Inspection report generated: {output_path}"
        )

        return output_path