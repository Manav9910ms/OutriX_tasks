import json
import random
import time
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def load_questions(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def show_intro():
    console.rule("[bold cyan]Welcome to the Interactive Quiz!")
    console.print("Test your knowledge and see how you score 🏆", style="yellow")
    time.sleep(1)

def run_quiz(questions):
    score = 0
    random.shuffle(questions)

    for idx, q in enumerate(questions, start=1):
        console.rule(f"[bold green]Question {idx}")
        console.print(q["question"], style="bold magenta")

        options = q["options"]
        random.shuffle(options)

        table = Table(show_header=False, box=None)
        for i, option in enumerate(options, start=1):
            table.add_row(f"[cyan]{i}[/]. {option}")
        console.print(table)

        choice = Prompt.ask("Your answer", choices=[str(i) for i in range(1, len(options)+1)])
        if options[int(choice)-1] == q["answer"]:
            console.print("✅ [bold green]Correct![/]", justify="center")
            score += 1
        else:
            console.print(f"❌ [bold red]Wrong![/] The correct answer was [yellow]{q['answer']}[/]", justify="center")

        time.sleep(0.8)

    console.rule("[bold blue]Quiz Complete!")
    console.print(f"🏅 Your final score: [bold]{score}[/] / {len(questions)}", style="bold yellow")

if __name__ == "__main__":
    show_intro()
    questions = load_questions("quiz_questions.json")
    run_quiz(questions)