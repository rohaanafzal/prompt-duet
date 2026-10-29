import os
import argparse

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markup import escape

from prompt_duet.loop import refine

console = Console()


def show_round(r):
    c = r.critique
    color = "green" if c.score >= 8 else "yellow" if c.score >= 5 else "red"
    title = f"Round {r.number} · score [{color}]{c.score}/10[/{color}]"
    body = "\n".join(f"• {escape(i)}" for i in c.issues[:3]) or "No major issues"
    console.print(Panel(body, title=title, border_style=color))


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Refine a prompt with a critic–refiner agent loop")
    parser.add_argument("prompt", nargs="?", help="Prompt to refine (asks if omitted)")
    parser.add_argument("--rounds", type=int, default=3, help="Max rewrite rounds")
    parser.add_argument("--target", type=int, default=9, help="Stop when score reaches this")
    args = parser.parse_args()

    goal = args.prompt or console.input("[bold]Enter your prompt:[/bold] ")
    model = os.getenv("MODEL", "groq:openai/gpt-oss-120b")

    with console.status("Critic and Refiner are talking..."):
        result = refine(goal, model, args.rounds, args.target, on_round=show_round)

    start = result.rounds[0].critique.score
    console.print(Panel(
        escape(result.final_prompt),
        title=f"Refined prompt · {start} → {result.final_score}/10",
        border_style="cyan",
    ))


if __name__ == "__main__":
    main()