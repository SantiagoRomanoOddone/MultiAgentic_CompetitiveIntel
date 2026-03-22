from typing import Optional

from rich.console import Console
from rich.panel import Panel

from models import ActionRecommendation


console = Console()

_ACTION_COLOR = {
    "escalate": "red",
    "notify_account_manager": "yellow",
    "reprice": "magenta",
    "monitor": "cyan",
}


def _urgency_color(score: int) -> str:
    if score >= 8:
        return "red"
    if score >= 5:
        return "yellow"
    return "cyan"


def human_review(rec: ActionRecommendation) -> Optional[ActionRecommendation]:
    urgency_color = _urgency_color(rec.urgency_score)
    action_color = _ACTION_COLOR.get(rec.action, "white")
    change_str = (
        f"{rec.price_change_pct:+.1f}% vs previous"
        if rec.price_change_pct is not None
        else "new price"
    )
    promo_line = f"  Promo:    ${rec.promo_price:.0f}\n" if rec.is_on_promo else ""

    console.print(
        Panel(
            f"[bold]Product:[/bold]  {rec.product_name}  (EAN {rec.ean})\n"
            f"[bold]Brand:[/bold]    {rec.brand}\n"
            f"[bold]Chain:[/bold]    {rec.chain} | {rec.city} | {rec.date}\n"
            f"[bold]Price:[/bold]    ${rec.list_price:.0f}  ({change_str})\n"
            + promo_line
            + f"[bold]Urgency:[/bold]  [{urgency_color}]{rec.urgency_score}/10  {rec.alert_type.upper()}[/{urgency_color}]\n"
            f"[bold]Reason:[/bold]   {rec.reasoning}\n\n"
            f"[bold]Action:[/bold]   [{action_color}]{rec.action.upper()}[/{action_color}]\n"
            f"{rec.message}",
            title=f"[bold blue]{rec.brand}[/bold blue]  —  {rec.chain}",
            border_style="blue",
            padding=(1, 2),
        )
    )

    while True:
        choice = input("  [A]pprove  [R]eject  [E]dit  > ").strip().lower()

        if choice == "a":
            console.print("  [green]Approved — action logged.[/green]\n")
            return rec

        elif choice == "r":
            console.print("  [red]Rejected — skipped.[/red]\n")
            return None

        elif choice == "e":
            new_action = input(f"  Action [{rec.action}]: ").strip()
            if new_action:
                rec.action = new_action
            print("  Message (blank line to finish):")
            lines = []
            while True:
                line = input("  ")
                if line == "":
                    break
                lines.append(line)
            if lines:
                rec.message = "\n".join(lines)
            console.print("  [green]Approved with edits — action logged.[/green]\n")
            return rec

        else:
            print("  Enter A, R, or E.")
