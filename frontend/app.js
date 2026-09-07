const API = "http://127.0.0.1:8000";

const input = document.getElementById("imageInput");
const preview = document.getElementById("preview");
const inspectBtn = document.getElementById("inspectBtn");
const status = document.getElementById("status");

let selectedFile = null;


// ============================================
// CHECK BACKEND
// ============================================

fetch(`${API}/api/health`)
  .then(response => response.json())
  .then(data => {
    status.textContent = `Backend: ${data.status}`;
  })
  .catch(() => {
    status.textContent = "Backend unavailable";
  });


// ============================================
// IMAGE SELECTION
// ============================================

input.addEventListener("change", () => {

  preview.innerHTML = "";

  if (!input.files.length) {

    inspectBtn.disabled = true;
    selectedFile = null;

    return;
  }

  selectedFile = input.files[0];

  const img = document.createElement("img");

  img.src = URL.createObjectURL(selectedFile);

  img.style.maxWidth = "100%";
  img.style.display = "block";

  preview.appendChild(img);

  inspectBtn.disabled = false;
});


// ============================================
// RUN INSPECTION
// ============================================

inspectBtn.addEventListener("click", async () => {

  if (!selectedFile) {
    return;
  }

  inspectBtn.disabled = true;
  inspectBtn.textContent = "Inspecting...";


  const formData = new FormData();

  formData.append("file", selectedFile);


  try {

    const response = await fetch(`${API}/api/inspect`, {
      method: "POST",
      body: formData
    });


    if (!response.ok) {

      throw new Error(
        `Server returned ${response.status}`
      );

    }


    const result = await response.json();


    // ========================================
    // REMOVE OLD RESULT
    // ========================================

    let resultBox = document.getElementById("result");

    if (resultBox) {
      resultBox.remove();
    }


    // ========================================
    // CREATE RESULT CONTAINER
    // ========================================

    resultBox = document.createElement("div");

    resultBox.id = "result";
    resultBox.className = "card";

    document.querySelector("main").appendChild(resultBox);


    // ========================================
    // IMAGE INFORMATION
    // ========================================

    let html = `

      <h2>Inspection Result</h2>

      <p>
        <strong>Image:</strong>
        ${result.filename}
      </p>

      <p>
        <strong>Image Size:</strong>
        ${result.image.width}
        ×
        ${result.image.height}
        pixels
      </p>

      <p>
        <strong>Status:</strong>
        ${result.status}
      </p>

      <hr>

    `;


    // ========================================
    // GEOMETRY DETECTION
    // ========================================

    const geometry = result.geometry_detection;


    html += `<h2>Object Detection</h2>`;


    if (geometry && geometry.detected) {

      html += `

        <p>
          <strong>Object:</strong>
          ${geometry.object_type}
        </p>

        <p>
          <strong>Pixel Width:</strong>
          ${geometry.pixel_dimensions.width.toFixed(1)}
          px
        </p>

        <p>
          <strong>Pixel Height:</strong>
          ${geometry.pixel_dimensions.height.toFixed(1)}
          px
        </p>

        <p>
          <strong>Long Dimension:</strong>
          ${geometry.rotated_dimensions.long.toFixed(1)}
          px
        </p>

        <p>
          <strong>Short Dimension:</strong>
          ${geometry.rotated_dimensions.short.toFixed(1)}
          px
        </p>

        <p>
          <strong>Orientation:</strong>
          ${geometry.orientation_angle.toFixed(2)}
          °
        </p>

      `;

    } else {

      html += `

        <p>
          <strong>No mechanical component detected.</strong>
        </p>

        <p>
          Try a clearer image with the complete component visible.
        </p>

      `;
    }


    // ========================================
    // CALIBRATION
    // ========================================

    const calibration = result.calibration;


    html += `<hr><h2>Calibration</h2>`;


    if (calibration && calibration.calibrated) {

      const reference = calibration.reference;
      const scale = calibration.scale;


      html += `

        <p>
          <strong>Calibration Status:</strong>
          Calibrated
        </p>

        <p>
          <strong>Reference Size:</strong>
          ${reference.width_mm.toFixed(2)}
          mm
        </p>

        <p>
          <strong>Reference Width:</strong>
          ${reference.width_pixels.toFixed(1)}
          px
        </p>

        <p>
          <strong>Scale:</strong>
          ${scale.mm_per_pixel.toFixed(6)}
          mm/pixel
        </p>

        <p>
          <strong>Pixels per mm:</strong>
          ${scale.pixels_per_mm.toFixed(2)}
        </p>

      `;

    } else {

      html += `

        <p>
          <strong>Calibration unavailable.</strong>
        </p>

        <p>
          Add a known-size reference to the image.
        </p>

      `;
    }


    // ========================================
    // ENGINEERING MEASUREMENTS
    // ========================================

    const measurement = result.measurement;


    html += `<hr><h2>Engineering Measurements</h2>`;


    if (measurement && measurement.measured) {

      const dimensions = measurement.dimensions;
      const uncertainty = measurement.uncertainty;


      html += `

        <div class="measurement-card">

          <p>
            <strong>Length:</strong>
            ${dimensions.length_mm.toFixed(2)}
            mm
          </p>

          <p>
            <strong>Width:</strong>
            ${dimensions.width_mm.toFixed(2)}
            mm
          </p>

          <p>
            <strong>Short Dimension:</strong>
            ${dimensions.short_dimension_mm.toFixed(2)}
            mm
          </p>

          <p>
            <strong>Estimated Uncertainty:</strong>
            ±${uncertainty.estimated_uncertainty_mm.toFixed(2)}
            mm
          </p>

          <p>
            <strong>Measurement Source:</strong>
            ${measurement.measurement_source}
          </p>

          <p>
            <strong>Scale:</strong>
            ${measurement.scale.mm_per_pixel.toFixed(6)}
            mm/pixel
          </p>

          <p>
            <strong>Measurement Status:</strong>
            Calibrated
          </p>

        </div>

      `;

    } else {

      html += `

        <p>
          <strong>Measurement unavailable.</strong>
        </p>

        <p>
          A valid calibration reference is required.
        </p>

      `;
    }


    // ========================================
    // ENGINEERING STANDARDS
    // ========================================

    const standards = result.standards_match;

    html += `<hr><h2>Engineering Standards</h2>`;

    if (standards) {

      if (standards.status === "STANDARD_MATCHED") {

        html += `

          <div class="measurement-card">

            <p>
              <strong>Status:</strong>
              STANDARD MATCHED
            </p>

            <p>
              <strong>Designation:</strong>
              ${standards.designation}
            </p>

            <p>
              <strong>Component Type:</strong>
              ${standards.component_type}
            </p>

            <p>
              <strong>Nominal Diameter:</strong>
              ${standards.nominal_diameter_mm}
              mm
            </p>

            <p>
              <strong>Coarse Thread Pitch:</strong>
              ${standards.coarse_pitch_mm}
              mm
            </p>

            <p>
              <strong>Measured Length:</strong>
              ${standards.measured_length_mm}
              mm
            </p>

            <p>
              <strong>Standard Length:</strong>
              ${standards.standard_length_mm}
              mm
            </p>

            <p>
              <strong>Dimensional Difference:</strong>
              ${standards.difference_mm}
              mm
            </p>

            <p>
              <strong>Confidence:</strong>
              ${standards.confidence}
            </p>

            <p>
              <strong>Measurement Source:</strong>
              ${standards.measurement_source}
            </p>

            <p>
              <strong>Database Source:</strong>
              ${standards.database_source}
            </p>

          </div>

        `;

      } else {

        html += `

          <div class="measurement-card">

            <p>
              <strong>Status:</strong>
              ${standards.status}
            </p>

            <p>
              ${standards.message || "No reliable standard match."}
            </p>

          </div>

        `;
      }
    }


    // ========================================
    // AI COMPONENT DETECTION
    // ========================================

    const aiDetections = result.ai_detections || [];


    html += `<hr><h2>AI Component Detection</h2>`;


    if (aiDetections.length > 0) {

      aiDetections.forEach((detection, index) => {

        html += `

          <div class="detection">

            <h3>AI Detection ${index + 1}</h3>

            <p>
              <strong>Component:</strong>
              ${detection.class}
            </p>

            <p>
              <strong>Confidence:</strong>
              ${(detection.confidence * 100).toFixed(1)}%
            </p>

          </div>

        `;

      });

    } else {

      html += `

        <p>
          AI model did not produce a reliable component classification.
        </p>

        <p>
          <strong>
            Geometry-based detection used.
          </strong>
        </p>

      `;
    }


    // ========================================
    // VISUAL INSPECTION
    // ========================================

    const defect = result.defect_inspection;

    html += `<hr><h2>Visual Inspection</h2>`;

    if (defect && defect.inspected) {

      html += `

        <div class="measurement-card">

          <p>
            <strong>Status:</strong>
            ${defect.status}
          </p>

          <p>
            <strong>Edge Activity:</strong>
            ${defect.edge_activity_ratio}
          </p>

          <p>
            <strong>Confidence:</strong>
            ${defect.confidence}
          </p>

          <p>
            <strong>Inspection Source:</strong>
            ${defect.inspection_source}
          </p>

          <p>
            ${defect.message}
          </p>

        </div>

      `;

    } else {

      html += `

        <p>
          <strong>Visual inspection unavailable.</strong>
        </p>

      `;
    }


    // ========================================
    // PDF REPORT
    // ========================================

    if (result.report && result.report.generated) {

      html += `

        <hr>

        <h2>Inspection Report</h2>

        <div class="measurement-card">

          <p>
            <strong>PDF Report:</strong>
            Generated successfully
          </p>

          <a
            href="${API}${result.report.url}"
            target="_blank"
            class="download-report"
          >
            📄 Download PDF Inspection Report
          </a>

        </div>

      `;
    }


    // ========================================
    // DISPLAY RESULT
    // ========================================

    resultBox.innerHTML = html;


    // ========================================
    // DRAW DETECTION BOX
    // ========================================

    if (geometry && geometry.detected) {

      const canvas = document.createElement("canvas");

      canvas.width = result.image.width;
      canvas.height = result.image.height;

      canvas.style.width = "100%";
      canvas.style.height = "auto";
      canvas.style.display = "block";
      canvas.style.marginTop = "20px";

      const ctx = canvas.getContext("2d");

      const img = new Image();

      img.onload = () => {

        // Draw original image
        ctx.drawImage(
          img,
          0,
          0,
          canvas.width,
          canvas.height
        );


        // ------------------------------------
        // COMPONENT BOUNDING BOX
        // ------------------------------------

        const bbox = geometry.bbox;

        const x1 = bbox[0];
        const y1 = bbox[1];

        const x2 = bbox[2];
        const y2 = bbox[3];


        ctx.strokeStyle = "#00ff00";
        ctx.lineWidth = 5;

        ctx.strokeRect(
          x1,
          y1,
          x2 - x1,
          y2 - y1
        );


        // ------------------------------------
        // LABEL
        // ------------------------------------

        const labelHeight = 35;
        const labelWidth = 230;

        ctx.fillStyle = "#00ff00";

        ctx.fillRect(
          x1,
          Math.max(0, y1 - labelHeight),
          labelWidth,
          labelHeight
        );

        ctx.fillStyle = "#000000";

        ctx.font = "bold 18px Arial";

        ctx.fillText(
          "Mechanical Component",
          x1 + 8,
          Math.max(23, y1 - 10)
        );


        // ------------------------------------
        // DIMENSION LABEL
        // ------------------------------------

        if (measurement && measurement.measured) {

          const dimensions = measurement.dimensions;

          ctx.fillStyle = "#ffffff";

          ctx.fillRect(
            x1,
            y2 + 5,
            260,
            65
          );

          ctx.fillStyle = "#000000";

          ctx.font = "bold 16px Arial";

          ctx.fillText(
            `Length: ${dimensions.length_mm.toFixed(2)} mm`,
            x1 + 8,
            y2 + 28
          );

          ctx.fillText(
            `Width: ${dimensions.width_mm.toFixed(2)} mm`,
            x1 + 8,
            y2 + 50
          );
        }

      };

      img.src = URL.createObjectURL(selectedFile);

      resultBox.appendChild(canvas);
    }


  } catch (error) {

    console.error(error);

    alert(
      "Inspection failed. Check that the FastAPI backend is running."
    );

  } finally {

    inspectBtn.disabled = false;

    inspectBtn.textContent = "Run Inspection";

  }

});