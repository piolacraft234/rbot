from urllib.parse import urlparse

from loguru import logger


class UrlUtilities:
    @staticmethod
    @logger.catch
    def is_valid_url(url: str) -> bool:
        """
        Check if a string is a URL.
        :param url: The URL to check.
        :return: Whether the string is a URL.
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])

        except Exception as e:
            return False
