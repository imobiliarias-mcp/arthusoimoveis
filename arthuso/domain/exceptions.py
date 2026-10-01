"""Domain exceptions hierarchy for Arthuso Imóveis rental research."""


class ArthusoError(Exception):
    """Base exception for all Arthuso rental research errors."""


class ValidationError(ArthusoError):
    """Raised when domain constraints or input values are invalid."""


class PropertyNotFoundError(ArthusoError):
    """Raised when a requested property cannot be found."""


class HttpTransportError(ArthusoError):
    """Raised when network communication or HTTP requests fail."""


class ParsingError(ArthusoError):
    """Raised when extracting or deserializing response content fails."""
