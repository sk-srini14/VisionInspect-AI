import json
import os


class StandardsDatabase:

    def __init__(self):

        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(__file__)
                )
            )
        )

        self.file_path = os.path.join(
            base_dir,
            "data",
            "standards.json"
        )

        self.data = self._load_database()

        print("Engineering standards database ready.")

    def _load_database(self):

        try:

            with open(
                self.file_path,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except FileNotFoundError:

            print(
                f"WARNING: Standards database not found: "
                f"{self.file_path}"
            )

            return {}

        except json.JSONDecodeError:

            print(
                "WARNING: Standards database contains invalid JSON."
            )

            return {}

    def get_fastener(self, designation):

        if not designation:
            return None

        designation = designation.upper().strip()

        # Support databases stored either as:
        # {"M10": {...}}
        # or {"fasteners": {"M10": {...}}}

        if designation in self.data:
            return self.data[designation]

        fasteners = self.data.get("fasteners", {})

        if designation in fasteners:
            return fasteners[designation]

        return None

    def list_fasteners(self):

        if "fasteners" in self.data:

            return list(
                self.data["fasteners"].keys()
            )

        return list(self.data.keys())