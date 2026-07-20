"""Typed domain exceptions, translated to HTTP responses by the error middleware."""


class DomainError(Exception):
    """Base class for all domain-level errors."""

    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class TransactionNotFoundError(DomainError):
    """Raised when a transaction cannot be found by its identifier."""

    code = "TRANSACTION_NOT_FOUND"

    def __init__(self, transaction_id: str) -> None:
        super().__init__(f"Transaction '{transaction_id}' not found")
        self.transaction_id = transaction_id


class InvalidTransactionAmountError(DomainError):
    """Raised when a transaction amount violates business rules."""

    code = "INVALID_TRANSACTION_AMOUNT"

    def __init__(self, monto: float) -> None:
        super().__init__(f"Invalid transaction amount: {monto}")
        self.monto = monto


class TransactionConflictError(DomainError):
    """Raised when a transaction state transition is not allowed."""

    code = "TRANSACTION_CONFLICT"


class QueuePublishError(DomainError):
    """Raised when a job cannot be enqueued for background processing."""

    code = "QUEUE_PUBLISH_ERROR"


class AIServiceError(DomainError):
    """Raised when the AI service fails to produce a response."""

    code = "AI_SERVICE_ERROR"


class AIQuotaExceededError(AIServiceError):
    """Raised when the AI provider rejects a request due to quota/rate limits."""

    code = "AI_QUOTA_EXCEEDED"

    def __init__(self, message: str, retry_after_seconds: float | None = None) -> None:
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


class RateLimitExceededError(DomainError):
    """Raised when a client exceeds the allowed request rate."""

    code = "RATE_LIMIT_EXCEEDED"
