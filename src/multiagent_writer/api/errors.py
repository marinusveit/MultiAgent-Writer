"""
Custom exceptions for API operations
"""


class APIError(Exception):
    """Basis-Fehlerklasse für API-Fehler"""
    pass


class NetworkError(APIError):
    """Fehler bei Netzwerkverbindung"""
    pass


class RateLimitError(APIError):
    """API Rate Limit überschritten"""
    pass


class AuthenticationError(APIError):
    """Ungültiger API-Key"""
    pass
