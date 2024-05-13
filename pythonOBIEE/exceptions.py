class OBIEEError(Exception):
    """Base class for all OBIEE related errors."""


class LogonFailedError(OBIEEError):
    """Exception raised when logon to the service fails."""


class LogoffFailedError(OBIEEError):
    """Exception raised when logoff from the service fails."""


class ExportFailedError(OBIEEError):
    """Exception raised when export operation fails."""
