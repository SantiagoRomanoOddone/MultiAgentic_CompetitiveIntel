from typing import Optional

from rich.console import Console
from rich.panel import Panel

from models import OutreachDraft


console = Console()

_CATEGORY_COLOR = {"hot": "red", "warm": "yellow", "cold": "cyan"}


def human_review(draft: OutreachDraft) -> Optional[OutreachDraft]:
    color = _CATEGORY_COLOR.get(draft.category, "white")

    console.print(
        Panel(
            f"[bold]To:[/bold]      {draft.name} <{draft.email}>\n"
            f"[bold]Score:[/bold]   {draft.score}/10  "
            f"[bold {color}]{draft.category.upper()}[/bold {color}]  —  {draft.reasoning}\n\n"
            f"[bold]Subject:[/bold] {draft.subject}\n\n"
            f"{draft.body}",
            title=f"[bold blue]{draft.company}[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        )
    )

    while True:
        choice = input("  [A]pprove  [R]eject  [E]dit  > ").strip().lower()

        if choice == "a":
            console.print("  [green]Approved — queued for sending.[/green]\n")
            return draft

        elif choice == "r":
            console.print("  [red]Rejected — skipped.[/red]\n")
            return None

        elif choice == "e":
            new_subject = input(f"  Subject [{draft.subject}]: ").strip()
            if new_subject:
                draft.subject = new_subject

            print("  Body (blank line to finish):")
            lines = []
            while True:
                line = input("  ")
                if line == "":
                    break
                lines.append(line)
            if lines:
                draft.body = "\n".join(lines)

            console.print("  [green]Approved with edits — queued for sending.[/green]\n")
            return draft

        else:
            print("  Enter A, R, or E.")
