from dataclasses import dataclass, field
from typing import Callable, Optional

from .agents import build_agents, Critique


@dataclass
class Round:
    number: int
    prompt: str
    critique: Critique


@dataclass
class RefineResult:
    original: str
    final_prompt: str
    final_score: int
    rounds: list[Round] = field(default_factory=list)


def format_critique(c: Critique) -> str:
    issues = "\n".join(f"- {i}" for i in c.issues)
    suggestions = "\n".join(f"- {s}" for s in c.suggestions)
    return f"Score: {c.score}/10\nIssues:\n{issues}\nSuggestions:\n{suggestions}"


def refine(
    goal: str,
    model_name: str,
    max_rounds: int = 3,
    target_score: int = 9,
    on_round: Optional[Callable[[Round], None]] = None,
) -> RefineResult:
    critic, refiner = build_agents(model_name)
    prompt = goal
    rounds: list[Round] = []

    for n in range(max_rounds + 1):
        critique = critic.invoke({"goal": goal, "prompt": prompt})
        rnd = Round(number=n, prompt=prompt, critique=critique)
        rounds.append(rnd)
        if on_round:
            on_round(rnd)

        if critique.score >= target_score or n == max_rounds:
            break

        prompt = refiner.invoke({
            "goal": goal,
            "prompt": prompt,
            "critique": format_critique(critique),
        }).strip()

    best = max(rounds, key=lambda r: r.critique.score)
    return RefineResult(
        original=goal,
        final_prompt=best.prompt,
        final_score=best.critique.score,
        rounds=rounds,
    )