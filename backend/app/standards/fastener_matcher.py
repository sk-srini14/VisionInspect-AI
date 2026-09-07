class FastenerMatcher:

    def __init__(self, standards_db):

        self.standards_db = standards_db

        print("Fastener standards matcher ready.")

    def match(self, component_type, measured_length_mm):

        # ============================================
        # CHECK COMPONENT TYPE
        # ============================================

        if not component_type:

            return {
                "matched": False,
                "status": "INSUFFICIENT_DATA",
                "message": "Component type is unavailable."
            }


        component = component_type.lower()


        # ============================================
        # CHECK WHETHER IT IS A FASTENER
        # ============================================

        fastener_keywords = [
            "bolt",
            "screw",
            "fastener"
        ]

        is_fastener = any(
            keyword in component
            for keyword in fastener_keywords
        )

        if not is_fastener:

            return {
                "matched": False,
                "status": "NOT_APPLICABLE",
                "message":
                    "Engineering fastener matching is not "
                    "applicable to this component."
            }


        # ============================================
        # CHECK MEASUREMENT
        # ============================================

        if measured_length_mm is None:

            return {
                "matched": False,
                "status": "INSUFFICIENT_DATA",
                "message":
                    "Measured length is required for "
                    "standards matching."
            }


        # ============================================
        # GET DATABASE FASTENERS
        # ============================================

        fasteners = self.standards_db.data.get(
            "fasteners",
            {}
        )

        if not fasteners:

            return {
                "matched": False,
                "status": "DATABASE_UNAVAILABLE",
                "message":
                    "No fastener specifications were found "
                    "in the engineering database."
            }


        # ============================================
        # FIND CLOSEST STANDARD LENGTH
        # ============================================

        candidates = []


        for designation, specification in fasteners.items():

            example_lengths = specification.get(
                "example_lengths_mm",
                []
            )

            nominal_diameter = specification.get(
                "nominal_diameter_mm"
            )

            pitch = specification.get(
                "coarse_pitch_mm"
            )


            for standard_length in example_lengths:

                difference = abs(
                    measured_length_mm -
                    float(standard_length)
                )

                candidates.append({

                    "designation": designation,

                    "standard_length_mm":
                        float(standard_length),

                    "difference_mm":
                        round(difference, 2),

                    "nominal_diameter_mm":
                        nominal_diameter,

                    "coarse_pitch_mm":
                        pitch,

                    "type":
                        specification.get("type")

                })


        # ============================================
        # NO LENGTH DATA
        # ============================================

        if not candidates:

            return {
                "matched": False,
                "status": "NO_STANDARD_DATA",
                "message":
                    "No standard lengths are available "
                    "for comparison."
            }


        # Sort by dimensional difference
        candidates.sort(
            key=lambda item:
                item["difference_mm"]
        )


        best = candidates[0]


        # ============================================
        # DETERMINE MATCH QUALITY
        # ============================================

        # This is intentionally conservative.
        #
        # It is NOT a manufacturing tolerance.
        # It is only a software matching threshold.

        match_tolerance_mm = 3.0


        if best["difference_mm"] <= match_tolerance_mm:

            return {

                "matched": True,

                "status": "STANDARD_MATCHED",

                "designation":
                    best["designation"],

                "component_type":
                    best["type"],

                "nominal_diameter_mm":
                    best["nominal_diameter_mm"],

                "coarse_pitch_mm":
                    best["coarse_pitch_mm"],

                "measured_length_mm":
                    round(
                        measured_length_mm,
                        2
                    ),

                "standard_length_mm":
                    best["standard_length_mm"],

                "difference_mm":
                    best["difference_mm"],

                "confidence":
                    "HIGH",

                "measurement_source":
                    "Computer Vision",

                "database_source":
                    "Engineering Standards Database",

                "note":
                    "Standard matched using measured "
                    "image length. This is not certified "
                    "metrology."

            }


        # ============================================
        # CLOSE BUT NOT MATCHED
        # ============================================

        if best["difference_mm"] <= 15.0:

            return {

                "matched": False,

                "status": "CANDIDATE_STANDARD",

                "designation":
                    best["designation"],

                "component_type":
                    best["type"],

                "nominal_diameter_mm":
                    best["nominal_diameter_mm"],

                "coarse_pitch_mm":
                    best["coarse_pitch_mm"],

                "measured_length_mm":
                    round(
                        measured_length_mm,
                        2
                    ),

                "nearest_standard_length_mm":
                    best["standard_length_mm"],

                "difference_mm":
                    best["difference_mm"],

                "confidence":
                    "LOW",

                "measurement_source":
                    "Computer Vision",

                "database_source":
                    "Engineering Standards Database",

                "message":
                    "A nearby engineering standard was "
                    "found, but the measured dimension is "
                    "outside the matching threshold.",

                "note":
                    "Additional evidence such as shaft "
                    "diameter, thread pitch or a better "
                    "calibrated image is required for "
                    "reliable fastener identification."

            }


        # ============================================
        # NO RELIABLE MATCH
        # ============================================

        return {

            "matched": False,

            "status": "NO_STANDARD_MATCH",

            "measured_length_mm":
                round(
                    measured_length_mm,
                    2
                ),

            "nearest_candidate":
                best["designation"],

            "nearest_standard_length_mm":
                best["standard_length_mm"],

            "difference_mm":
                best["difference_mm"],

            "confidence":
                "INSUFFICIENT",

            "measurement_source":
                "Computer Vision",

            "database_source":
                "Engineering Standards Database",

            "message":
                "The measured component does not "
                "reliably match the available standard "
                "fastener dimensions.",

            "note":
                "Do not infer nominal diameter or thread "
                "pitch without sufficient visual evidence."
        }