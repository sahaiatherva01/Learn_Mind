import logging
import sys
import re

PII_PATTERNS = [
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'), "[REDACTED_EMAIL]"),
    (re.compile(r'\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b'), "[REDACTED_PHONE]"),
    (re.compile(r'password\s*[:=]\s*["\']?([^"\'\s]+)["\']?', re.IGNORECASE), "password:[REDACTED]"),
]


class PIISafeFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        for pattern, replacement in PII_PATTERNS:
            message = pattern.sub(replacement, message)
        return message


def setup_logging():
    logger = logging.getLogger("learn_mind")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = PIISafeFormatter(
            "%(asctime)s | %(levelname)-7s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logging()
