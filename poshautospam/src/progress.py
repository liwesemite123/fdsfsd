from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src.validator import ValidationStatus

console = Console()


def show_banner() -> None:
    banner = Panel(
        Text("Email Validator", style="bold cyan", justify="center"),
        subtitle="SMTP Email Verification Tool",
        border_style="cyan",
    )
    console.print(banner)
    console.print()


def update_progress(email: str, status: ValidationStatus) -> None:
    status_config = {
        ValidationStatus.VALID: ("✓", "green", "VALID"),
        ValidationStatus.INVALID: ("✗", "red", "INVALID"),
        ValidationStatus.ERROR: ("⚠", "yellow", "ERROR"),
    }

    symbol, color, label = status_config[status]

    status_text = Text()
    status_text.append(f"{symbol} ", style=f"bold {color}")
    status_text.append(email, style="white")
    status_text.append(f" → {label}", style=f"bold {color}")

    console.print(status_text)


def show_summary(total: int, valid: int, invalid: int, errors: int) -> None:
    console.print()
    console.rule("[bold cyan]Validation Summary", style="cyan")
    console.print()

    console.print(f"  📊 Total processed: [bold]{total}[/bold]")
    console.print(f"  ✓ Valid:          [bold green]{valid}[/bold green]")
    console.print(f"  ✗ Invalid:        [bold red]{invalid}[/bold red]")
    console.print(f"  ⚠ Errors:         [bold yellow]{errors}[/bold yellow]")

    if total - errors > 0:
        success_rate = (valid / (total - errors)) * 100
        console.print(f"  📈 Success rate:  [bold]{success_rate:.1f}%[/bold]")

    console.print()


def show_error_details(error_results: list) -> None:
    if not error_results:
        return

    console.print()
    console.rule("[bold yellow]Error Details", style="yellow")
    console.print()

    for result in error_results:
        console.print(f"  ⚠ [bold]{result.email}[/bold]")
        console.print(f"    Reason: [yellow]{result.reason}[/yellow]")
        if result.smtp_code:
            console.print(f"    SMTP Code: [dim]{result.smtp_code}[/dim]")
        console.print(f"    Duration: [dim]{result.duration_ms:.0f}ms[/dim]")
        console.print()

    console.print()
