import io
import logging
import time
from datetime import datetime, timedelta
from mimetypes import guess_extension
from pathlib import Path

from zeep import Client
from zeep.exceptions import Fault

from .exceptions import ExportFailedError
from .report import Report

logger = logging.getLogger(__name__)


class OBIEEAnalysisExporter:
    """
    A class to handle the export of OBIEE (Oracle Business Intelligence Enterprise Edition) analysis reports.

    This class provides functionality to export reports in various formats, save them to a specified directory, or return them as file-like objects.

    Attributes:
        client (Client): A zeep SOAP client instance used to communicate with the OBIEE web service.
        timeout (int): The maximum amount of time (in seconds) to wait for an export to complete.
        overwrite_existing (bool): If True, existing files with the same name as the export file will be overwritten.
        status_check_interval (int): The interval (in seconds) at which the export status is checked.

    Methods:
        export_and_save(report): Exports a report and saves it to a file.
        export_to_file_like_object(report): Exports a report and returns a file-like object.
    """

    def __init__(
        self,
        client: Client,
        timeout: int = 300,
        overwrite_existing: bool = False,
        status_check_interval: int = 2,
    ):
        """
        Initialize the OBIEEAnalysisExporter instance.

        Parameters:
            client (Client): A zeep Client object to interact with OBIEE.
            timeout (int, optional): Maximum time to wait for the export to complete. Default is 300 seconds.
            overwrite_existing (bool, optional): Whether to overwrite existing files. Default is False.
            status_check_interval (int, optional): Time interval in seconds to check the export status. Default is 2 seconds.
        """
        self.export_service = client.bind("AnalysisExportViewsService")
        self.timeout = timeout  # Timeout in seconds
        self.overwrite_existing = overwrite_existing
        self.status_check_interval = status_check_interval

    def export_and_save(self, report: Report):
        """
        Export am OBIEE analysis report and save it to a file.

        Parameters:
            report (Report): A Report object representing the report to be exported.

        Returns:
            str: The path to the saved export file.

        Raises:
            ValueError: If the report output folder in the Report object is None.
            ExportFailedError: If the export fails.
            TimeoutError: If the export process times out.
        """
        if report.output_folder is None:
            logger.error("Output folder is required when exporting to file.")
            raise ValueError("Output folder is required when exporting to file.")
        export_result = self._export_report(report)
        return self._save_export(export_result, report)

    def export_to_file_like_object(self, report: Report):
        """
        Export an OBIEE analysis report and return it as a file-like object.
        This method is useful if you want to use the export data in memory without saving it to a file.
        For example, you can use this method to export a report to a Pandas DataFrame.

        Parameters:
            report (Report): A Report object representing the report to be exported.

        Returns:
            io.BytesIO: A file-like object containing the export data.
            str: The file extension of the export file.

        Raises:
            ExportFailedError: If the export fails.
            TimeoutError: If the export process times out.
        """
        export_result = self._export_report(report)
        file_like_object = io.BytesIO(export_result.viewData)
        file_extension = self._get_extension(export_result.mimeType)
        return file_like_object, file_extension

    def _export_report(self, report: Report):
        try:
            logger.info(
                "Exporting '%s' in '%s' format...",
                report.report_name,
                report.output_format,
            )
            query_id = self._initiate_export(report).queryID
            export_result = self._wait_for_export_completion(query_id)
            logger.info("Export Complete '%s'.", report.report_name)
            return export_result

        except Fault as e:
            logger.error(
                "Export failed for report '%s'. Error: %s", report.report_name, e
            )
            raise ExportFailedError(f"Export failed. {str(e)}") from e
        except Exception as e:
            logger.error(
                "Export failed for report '%s'. Error: %s", report.report_name, e
            )
            raise ExportFailedError("Export failed.") from e

    def _save_export(self, export_result, report: Report):
        output_file_path = self._get_output_file_path(export_result, report)

        logger.debug("Saving export data to %s...", output_file_path)
        self._write_data_to_file(export_result, output_file_path)

        logger.info("Export saved to %s.", output_file_path)
        return output_file_path

    def _initiate_export(self, report: Report):
        logger.debug(f"Initiating export for report: {report.report_ref}")
        logger.debug(f"Output format: {report.output_format}")
        logger.debug(f"Execution options: {report.execution_options}")

        return self.export_service.initiateAnalysisExport(
            report=report.report_ref,
            outputFormat=report.output_format,
            executionOptions=report.execution_options,
        )

    def _get_export_result(self, query_id):
        return self.export_service.completeAnalysisExport(queryID=query_id)

    def _wait_for_export_completion(self, query_id):
        """
        Wait for the export to complete. Checks the export status at regular intervals.
        Raises an error if the export fails or times out.

        We use asynchronous export and check the export status at regular intervals.
        """
        start_time = datetime.now()  # Record start time
        while True:
            export_result = self._get_export_result(query_id)
            export_status = export_result.exportStatus

            # Calculate elapsed time in seconds
            elapsed_time = (datetime.now() - start_time).total_seconds()

            # Format the elapsed time as a duration
            formatted_elapsed_time = str(timedelta(seconds=int(elapsed_time)))

            # Log the formatted elapsed time, current time, and export status
            logger.debug(
                "Elapsed time: %s. Current time: %s. Export status: %s",
                formatted_elapsed_time,
                datetime.now().strftime("%I:%M:%S %p"),
                export_status,
            )

            # Check if the timeout is exceeded and raise an error if it is
            if elapsed_time > self.timeout:
                raise TimeoutError(
                    f"Export timed out after {formatted_elapsed_time}. Timeout is {self.timeout} seconds."
                )

            # Handling different export statuses
            match export_status:
                case "InProgress":
                    # Wait for the specified interval before checking again
                    time.sleep(self.status_check_interval)
                    continue
                case "Error":
                    logger.error(
                        "Export failed with an error. OBIEE returned exportStatus 'Error'."
                    )
                    raise ExportFailedError(
                        "Export failed with an error. OBIEE returned exportStatus 'Error'."
                    )
                case "Done":
                    # Log the final elapsed time
                    logger.debug(
                        "Report finished exporting in %s.", formatted_elapsed_time
                    )
                    break
                case _:
                    logger.error(
                        "OBIEE returned an unknown exportStatus: %s", export_status
                    )
                    raise ValueError(
                        f"OBIEE returned an unknown exportStatus: {export_status}"
                    )

        return export_result

    def _get_output_file_path(self, export_result, report: Report):
        """Get the output file path by combining the output folder, report name, and extension."""
        extension = self._get_extension(export_result.mimeType)
        output_folder_path = Path(report.output_folder)
        output_folder_path.mkdir(parents=True, exist_ok=True)
        output_file_path = output_folder_path / f"{report.report_name}{extension}"
        return output_file_path

    def _write_data_to_file(self, export_result, output_file_path):
        """Write the export data to a file."""
        if output_file_path.exists() and not self.overwrite_existing:
            logger.error(
                "File %s already exists and overwriting is disabled.", output_file_path
            )
            raise FileExistsError(
                f"File {output_file_path} already exists and overwriting is disabled."
            )

        with open(output_file_path, "wb") as output_file:
            output_file.write(export_result.viewData)

    def _get_extension(self, mime_type):
        """Get the file extension from a MIME type."""
        return guess_extension(mime_type, strict=True)
