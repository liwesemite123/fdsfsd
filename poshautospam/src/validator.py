import asyncio
import logging
import os
import re
import socket
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

import aiosmtplib

# from rich.console import Console
# from rich.panel import Panel
# from rich.text import Text

# console = Console()

class ValidationStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"
    ERROR = "error"


@dataclass
class ValidationResult:
    email: str
    status: ValidationStatus
    reason: str | None
    smtp_code: int | None
    timestamp: datetime
    duration_ms: float


@dataclass
class ValidationBatch:
    total_count: int
    valid_count: int
    invalid_count: int
    error_count: int
    results: list[ValidationResult]
    start_time: datetime
    end_time: datetime | None
    duration_seconds: float

    @property
    def success_rate(self) -> float:
        if self.total_count - self.error_count == 0:
            return 0.0
        return (self.valid_count / (self.total_count - self.error_count)) * 100

    @property
    def is_complete(self) -> bool:
        return self.end_time is not None


EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}"
    r"[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)


def parse_email(email: str) -> tuple[str, str] | None:
    email = email.strip()

    if not EMAIL_REGEX.match(email):
        return None

    if len(email) > 320:
        return None

    try:
        local_part, domain = email.rsplit("@", 1)
    except ValueError:
        return None

    if not local_part or not domain:
        return None

    if len(local_part) > 64:
        return None

    if len(domain) > 255:
        return None

    if "." not in domain:
        return None

    return local_part, domain


class SMTPConnection:
    def __init__(self, domain: str) -> None:
        self.domain = domain
        self.connection: aiosmtplib.SMTP | None = None
        self.last_used = datetime.now(timezone.utc)
        self.email_count = 0
        self.is_connected = False
        self._lock = asyncio.Lock()

    def _get_mx_host(self) -> str | None:
        try:
            import dns.resolver

            answers = dns.resolver.resolve(self.domain, "MX")
            mx_records = sorted([(r.preference, str(r.exchange).rstrip(".")) for r in answers])
            if mx_records:
                return mx_records[0][1]
        except Exception:
            pass

        return self.domain

    async def connect(self, timeout: float = 10.0) -> bool:
        async with self._lock:
            if self.is_connected and self.connection:
                return True

            try:
                mx_host = self._get_mx_host()
                if not mx_host:
                    logging.warning("No MX record found for %s", self.domain)
                    return False

                self.connection = aiosmtplib.SMTP(
                    hostname=mx_host,
                    port=25,
                    timeout=timeout,
                )
                await self.connection.connect()
                self.is_connected = True
                self.last_used = datetime.now(timezone.utc)
                logging.debug("Connected to SMTP server: %s", mx_host)
                return True
            except (
                aiosmtplib.SMTPException,
                socket.gaierror,
                TimeoutError,
                OSError,
            ) as e:
                logging.warning("Failed to connect to %s: %s", self.domain, e)
                self.is_connected = False
                return False
            except Exception:
                logging.exception("Unexpected error connecting to %s", self.domain)
                self.is_connected = False
                return False

    async def close(self) -> None:
        async with self._lock:
            if self.connection and self.is_connected:
                try:
                    await self.connection.quit()
                except Exception as e:
                    logging.debug("Error closing connection to %s: %s", self.domain, e)
                finally:
                    self.is_connected = False
                    self.connection = None

    async def verify_email(self, email: str, timeout: float = 10.0) -> tuple[bool, int | None, str | None]:
        if not self.is_connected and not await self.connect(timeout):
            return False, None, "Connection failed"

        try:
            await self.connection.mail("verify@validator.local")

            code, message = await self.connection.rcpt(email)

            self.email_count += 1
            self.last_used = datetime.now(timezone.utc)
            if code == 250:
                return True, code, None
            if code in (550, 551, 553):
                return False, code, message
            if code in (421, 450, 451, 452):
                return False, code, f"Temporary error: {message}"
            return False, code, f"Unknown response: {message}"

        except aiosmtplib.SMTPException as e:
            logging.warning("SMTP error verifying %s: %s", email, e)
            return False, None, str(e)
        except Exception as e:
            logging.exception("Unexpected error verifying %s", email)
            return False, None, str(e)


_connection_pool: dict[str, SMTPConnection] = {}
_pool_lock = asyncio.Lock()

_gmail_validator = None


def _get_gmail_validator():
    global _gmail_validator
    if _gmail_validator is None:
        try:
            from src.gmail_validator import EmailValidator
            _gmail_validator = EmailValidator()
            logging.info("Gmail validator loaded: version %s", _gmail_validator.get_version())
        except FileNotFoundError:
            logging.warning("Gmail validator library not found, falling back to standard SMTP")
            _gmail_validator = False
        except Exception:
            logging.exception("Failed to load Gmail validator: %s")
            _gmail_validator = False
    return _gmail_validator if _gmail_validator is not False else None


async def _validate_gmail_email(
    email: str,
    start_time: datetime,
    proxy_url: str | None = None,
) -> ValidationResult:
    gmail_validator = _get_gmail_validator()

    if gmail_validator is None:
        logging.debug("Gmail validator unavailable, using standard SMTP for %s", email)
        return ValidationResult(
            email=email,
            status=ValidationStatus.ERROR,
            reason="Gmail validator library not available",
            smtp_code=None,
            timestamp=datetime.now(timezone.utc),
            duration_ms=(datetime.now(timezone.utc) - start_time).total_seconds() * 1000,
        )

    try:
        loop = asyncio.get_event_loop()

        if proxy_url:
            result = await loop.run_in_executor(
                None,
                lambda: gmail_validator.validate(email, proxy_url=proxy_url)
            )
            logging.debug("Validating %s via proxy: %s", email, proxy_url)
        else:
            result = await loop.run_in_executor(None, gmail_validator.validate, email)

        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        if result["error"]:
            status = ValidationStatus.ERROR
            reason = result["error"]
            logging.warning("%s -> ERROR (Gmail validator: %s)", email, reason)
        elif result["has_mailbox"]:
            status = ValidationStatus.VALID
            reason = None
            logging.info("%s -> VALID (Gmail validator)", email)
        else:
            status = ValidationStatus.INVALID
            reason = "Mailbox not found"
            logging.info("%s -> INVALID (Gmail validator)", email)

        return ValidationResult(
            email=email,
            status=status,
            reason=reason,
            smtp_code=None,
            timestamp=datetime.now(timezone.utc),
            duration_ms=duration_ms,
        )

    except Exception as e:
        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        logging.exception("%s -> ERROR (Gmail validator exception)", email)
        return ValidationResult(
            email=email,
            status=ValidationStatus.ERROR,
            reason=f"Gmail validator error: {e}",
            smtp_code=None,
            timestamp=datetime.now(timezone.utc),
            duration_ms=duration_ms,
        )


async def validate_single_email(email: str, timeout: float = 10.0) -> ValidationResult:
    start_time = datetime.now(timezone.utc)

    parsed = parse_email(email)
    if not parsed:
        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        return ValidationResult(
            email=email,
            status=ValidationStatus.INVALID,
            reason="Invalid email format",
            smtp_code=None,
            timestamp=datetime.now(timezone.utc),
            duration_ms=duration_ms,
        )

    _local_part, domain = parsed

    if domain.lower() == "gmail.com":
        proxy_url = os.environ.get("VALIDATOR_PROXY")
        return await _validate_gmail_email(email, start_time, proxy_url)

    async with _pool_lock:
        if domain not in _connection_pool:
            _connection_pool[domain] = SMTPConnection(domain)
        smtp_conn = _connection_pool[domain]

    try:
        is_valid, smtp_code, reason = await smtp_conn.verify_email(email, timeout)

        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        if is_valid:
            status = ValidationStatus.VALID
            logging.info("%s -> VALID (%s)", email, smtp_code)
        elif smtp_code and smtp_code in (421, 450, 451, 452):
            status = ValidationStatus.ERROR
            logging.warning("%s -> ERROR (%s: %s)", email, smtp_code, reason)
        else:
            status = ValidationStatus.INVALID
            logging.info("%s -> INVALID (%s: %s)", email, smtp_code, reason)

        return ValidationResult(
            email=email,
            status=status,
            reason=reason,
            smtp_code=smtp_code,
            timestamp=datetime.now(timezone.utc),
            duration_ms=duration_ms,
        )

    except Exception as e:
        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        logging.exception("%s -> ERROR (exception)", email)
        return ValidationResult(
            email=email,
            status=ValidationStatus.ERROR,
            reason=str(e),
            smtp_code=None,
            timestamp=datetime.now(timezone.utc),
            duration_ms=duration_ms,
        )


async def validate_batch(
    emails: list[str],
    progress_callback: Callable[[str, ValidationStatus], None] | None = None,
    max_concurrent: int = 25,
    timeout: float = 10.0,
) -> list[ValidationResult]:
    if not emails:
        return []

    semaphore = asyncio.Semaphore(max_concurrent)

    async def validate_with_limit(email: str) -> ValidationResult:
        async with semaphore:
            result = await validate_single_email(email, timeout)

            if progress_callback:
                progress_callback(email, result.status)

            await asyncio.sleep(0.1)

            return result

    tasks = [asyncio.create_task(validate_with_limit(email)) for email in emails]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    final_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            final_results.append(
                ValidationResult(
                    email=emails[i],
                    status=ValidationStatus.ERROR,
                    reason=str(result),
                    smtp_code=None,
                    timestamp=datetime.now(timezone.utc),
                    duration_ms=0.0,
                )
            )
        else:
            final_results.append(result)

    return final_results


async def cleanup_connections() -> None:
    async with _pool_lock:
        for conn in _connection_pool.values():
            await conn.close()
        _connection_pool.clear()
    logging.info("All SMTP connections closed")


# def progress_callback(email: str, status: ValidationStatus):
#     if status == ValidationStatus.VALID:
#         console.print(f"[green]✅ {email} - валиден[/green]")
#     elif status == ValidationStatus.INVALID:
#         console.print(f"[red]❌ {email} - невалиден[/red]")
#     else:
#         conso

# async def main():
#     emails = [
#         "flushsfinds@gmail.com",
#         "drea_60@gmail.com",
#         "keyla829@gmail.com",
#         "sgraziano6119@gmail.com",
#         "lilawinthrop@gmail.com",
#         "sethanclayton@gmail.com",
#         "marleah525@gmail.com",
#         "madradretrotoys@gmail.com",
#         "nvaziran@gmail.com",
#         "craggcm1@gmail.com",
#         "kayleefha@gmail.com",
#         "oliveiramom1980@gmail.com",
#         "dhhelijio0@gmail.com",
#         "mackenziekla413@gmail.com",
#         "atx_lisa@gmail.com",
#         "burlyboutique@gmail.com",
#         "mstanchak@gmail.com",
#         "shaw6331@gmail.com",
#         "lilliannag7@gmail.com",
#         "ahanackart@gmail.com",
#     ]
#     d = await validate_batch(
#         emails=emails,
#         max_concurrent=25,
#         timeout=10.0,
#         progress_callback=progress_callback
#     )

# #     print(d)

# if __name__ == "__main__":
#     asyncio.run(main())
    