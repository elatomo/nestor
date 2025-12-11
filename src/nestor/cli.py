"""Command-line interface for Néstor."""

import asyncio
import logging
import sys
from typing import Any

import click
from pydantic_ai.exceptions import UnexpectedModelBehavior

from . import AssistantDeps, create_assistant_agent
from .config import settings

logger = logging.getLogger("nestor")


@click.group()
@click.option("--debug", "-d", is_flag=True, help="Enable debug logging")
@click.option("--usage", "-u", is_flag=True, help="Show token usage")
@click.pass_context
def cli(ctx, debug: bool, usage: bool):
    """Néstor - Your AI assistant."""
    ctx.ensure_object(dict)
    ctx.obj["usage"] = usage
    logging.basicConfig(level=logging.DEBUG if debug else logging.WARN)


@cli.command()
@click.argument("prompt", required=False)
@click.option(
    "--multiline",
    "-m",
    is_flag=True,
    help="Enter multiline mode (Ctrl+D to submit)",
)
@click.pass_context
def ask(ctx, prompt: str | None, multiline: bool):
    """Ask Néstor a question.

    Examples:
        nestor ask "What time is it in Tokyo?"
        nestor ask --multiline  # For longer prompts
    """
    if multiline or not prompt:
        click.echo("Enter your question (Ctrl+D to submit):")
        prompt = sys.stdin.read().strip()

    if not prompt:
        click.echo("No prompt provided", err=True)
        sys.exit(1)

    asyncio.run(_run_assistant(prompt, show_usage=ctx.obj["usage"]))


@cli.command()
@click.pass_context
def interactive(ctx):
    """Start interactive chat session."""
    click.secho("Néstor Interactive Mode", bold=True)
    click.echo("Type 'exit' or 'quit' to end the session\n")

    messages = []  # Conversation history

    while True:
        prompt = click.prompt(">>>", type=str, prompt_suffix=" ")
        if prompt.lower() in ("exit", "quit"):
            click.echo("Goodbye!")
            break

        messages = asyncio.run(
            _run_assistant(prompt, messages, show_usage=ctx.obj["usage"])
        )


async def _run_assistant(
    prompt: str,
    message_history: list[Any] | None = None,
    show_usage: bool = False,
):
    """Run the assistant with a prompt."""
    logger.info("Running assistant with prompt: %r", prompt)

    try:
        agent = create_assistant_agent(
            api_key=settings.openai_api_key,
            model_name=settings.default_model,
            max_retries=settings.max_retries,
        )

        deps = AssistantDeps(
            search_backend=settings.search_backend,
            safesearch=settings.safesearch,
        )

        result = await agent.run(
            prompt,
            message_history=message_history,
            deps=deps,
        )

        click.echo(f"\n{result.output}\n")

        if show_usage:
            usage = result.usage()
            click.echo(
                f"Tokens: {usage.total_tokens} "
                f"(↓ {usage.input_tokens} ↑ {usage.output_tokens}) "
                f"• {usage.requests} request(s)"
            )

        return result.all_messages()

    except UnexpectedModelBehavior as e:
        logger.exception("Agent run failed")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def info():
    """Show Néstor configuration."""
    click.echo("Néstor Configuration:")
    click.echo(f"  Model: {settings.default_model}")
    click.echo(f"  Max retries: {settings.max_retries}")


if __name__ == "__main__":
    cli()
