import logging

from zeep import Client
from zeep.exceptions import Fault

from .exceptions import LogoffFailedError, LogonFailedError

logger = logging.getLogger(__name__)


class OBIEESession:
    """
    This class is intended to be used as a context manager.
    It logs into OBIEE when entering the context block, returning the session ID, and logs off when exiting the context block.

    Raises:
    - LogonFailedError: If logging into OBIEE fails.
    - LogoffFailedError: If logging off from OBIEE fails.

    Notes:
    - Ensure that the client provided is correctly configured to communicate with OBIEE.
    """

    def __init__(self, client: Client, username, password):
        """
        Example usage:
        with OBIEEsession(client, username, password):
            # Session is automatically managed within this block.
            # Use this if you dont need the session ID.

        Or:

        with OBIEEsession(client, username, password) as session_id:
            # Session is automatically managed within this block.
            # The session ID is returned and captured here for use.

        Parameters:
        - client (Client): A zeep Client object to interact with OBIEE.
        - username (str): The username for the OBIEE session.
        - password (str): The password for the OBIEE session.
        """
        self.session_service = client.bind("SAWSessionService")
        self.username = username
        self._password = password
        self._session_id = None

    def __enter__(self):
        logger.info(f"Attempting to log in as {self.username}...")
        try:
            self._session_id = self.session_service.logon(self.username, self._password)
            logger.info(f"Logged in successfully as {self.username}.")
            # Log session ID at debug level
            logger.debug(f"Session ID: {self._session_id}")
            return self._session_id
        except Fault as e:
            logger.error(f"Logon failed for user {self.username}. Error: {e}")
            raise LogonFailedError(f"Logon failed. {str(e)}") from e
        finally:
            self._password = None  # Clear password from memory

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session_id:
            try:
                self.session_service.logoff(self._session_id)
                logger.info(f"User {self.username} logged off successfully.")
                # Log session ID at debug level
                logger.debug(f"Logged off from session {self._session_id}.")
            except Fault as e:
                logger.error(f"Logoff failed for user {self.username}. Error: {e}")
                raise LogoffFailedError(f"Logoff failed. {str(e)}") from e
            finally:
                self._session_id = None  # Clear session ID

        # TODO: Test this. See if we can get the error to raise. Maybe logon, start export, disconnect network, then try to logoff?