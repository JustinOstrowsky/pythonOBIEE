import logging
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class Report:
    """
    Represents a report for export from OBIEE with specified format and save options.

    Attributes:
    - report_ref (str): Path to the report within OBIEE.
    - output_format (str): Format for the exported report (e.g., 'PDF', 'MHTML', 'EXCEL2007', 'CSV').
    - output_folder (str, optional): Folder path where the report will be saved.
    - custom_report_name (str, optional): Name for the saved report file. If not provided, the name of the report in OBIEE is used.
    - refresh (bool, optional): Whether to refresh the report before exporting.
    """

    report_ref: str
    output_format: str
    output_folder: str = None  # should be a valid path to a folder
    custom_report_name: str = (
        None  # should be a valid file name. Optional, if not provided, a report name will be generated
    )
    refresh: bool = False

    def __post_init__(self):
        # Strip the user input strings
        self.report_ref = self._strip_and_log(self.report_ref, "report_ref")
        self.output_format = self._strip_and_log(self.output_format, "output_format")
        if self.output_folder:
            self.output_folder = self._strip_and_log(
                self.output_folder, "output_folder"
            )
        if self.custom_report_name:
            self.custom_report_name = self._strip_and_log(
                self.custom_report_name, "custom_report_name"
            )

    @property
    def execution_options(self):
        return {
            "async": True,
            "useMtom": False,
            "refresh": self.refresh,
        }

    @property
    def report_name(self):
        """Returns a name for the report file, either the custom name if provided, or one created from the OBIEE path."""
        if self.custom_report_name:
            return self.custom_report_name
        else:
            return self._generate_report_name()

    @property
    def original_name(self):
        """Returns the name of the report in OBIEE. Created from the OBIEE path."""
        return self._generate_report_name()

    def _generate_report_name(self):
        return Path(self.report_ref).name

    @staticmethod
    def _strip_and_log(value, attribute_name):
        stripped_value = value.strip()
        if stripped_value != value:
            logger.warning(
                f"Leading or trailing space removed from {attribute_name}: '{value}' -> '{stripped_value}'. "
                "To avoid this warning, please consider correcting the input at the source."
            )
        return stripped_value
