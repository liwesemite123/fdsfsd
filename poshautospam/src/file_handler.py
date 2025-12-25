import asyncio
from pathlib import Path

from src.validator import ValidationResult, ValidationStatus


async def read_emails(file_path: str) -> list[str]:
    path = Path(file_path)

    if not path.exists():
        msg = f"Input file not found: {file_path}"
        raise FileNotFoundError(msg)

    loop = asyncio.get_event_loop()
    content = await loop.run_in_executor(None, path.read_text, "utf-8")

    return [line.strip() for line in content.splitlines() if line.strip()]


async def write_valid_emails(
    file_path: str,
    results: list[ValidationResult],
) -> None:
    valid_emails = [
        result.email
        for result in results
        if result.status == ValidationStatus.VALID
    ]

    content = "\n".join(valid_emails)
    if valid_emails:
        content += "\n"

    path = Path(file_path)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, path.write_text, content, "utf-8")
