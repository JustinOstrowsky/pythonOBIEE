import logging

from zeep import Client, Settings
from zeep.cache import SqliteCache
from zeep.transports import Transport

logger = logging.getLogger(__name__)


def build_client(wsdl):
    """
    Creates, configures, and returns a Zeep Client object for interacting with OBIEE services.

    The returned client is configured with some default settings.
    If you need to customize the client, you can create your own client and use it instead.

    The function configures the following defaults:
    - Enables 'xml_huge_tree' to allow processing of large XML documents.
    - Sets up a caching mechanism using SqliteCache with a 1-hour cache timeout.
    - Uses default Zeep settings for other parameters.

    Parameters:
    - wsdl (str): The URL to the WSDL file for the OBIEE web service.

    Returns:
    - zeep.Client: A Zeep Client instance configured for interaction with OBIEE services.

    Example usage:
    client = build_client("http://your-OBIEE-server:9502/analytics-ws/saw.dll/wsdl/v10")

    """

    # Prepare default settings
    default_settings = {"xml_huge_tree": True}

    # Create Settings object
    settings = Settings(default_settings)

    # Setup cache with SqliteCache. The argument is the timeout for cache, in seconds.
    cache = SqliteCache(timeout=3600)  # 1 hour caching

    transport = Transport(cache=cache)

    return Client(wsdl, settings=settings, transport=transport)
