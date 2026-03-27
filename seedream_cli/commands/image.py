"""Image generation commands."""

import click

from seedream_cli.core.client import get_client
from seedream_cli.core.exceptions import SeedreamError
from seedream_cli.core.output import (
    DEFAULT_MODEL,
    RESOLUTIONS,
    SEEDREAM_MODELS,
    print_error,
    print_image_result,
    print_json,
)


@click.command()
@click.argument("prompt")
@click.option(
    "-m",
    "--model",
    type=click.Choice(SEEDREAM_MODELS),
    default=DEFAULT_MODEL,
    help="Seedream model version.",
)
@click.option(
    "-r",
    "--resolution",
    type=click.Choice(RESOLUTIONS),
    default=None,
    help="Output resolution.",
)
@click.option("--callback-url", default=None, help="Webhook callback URL.")
@click.option("--json", "output_json", is_flag=True, help="Output raw JSON.")
@click.pass_context
def generate(
    ctx: click.Context,
    prompt: str,
    model: str,
    resolution: str | None,
    callback_url: str | None,
    output_json: bool,
) -> None:
    """Generate an image from a text prompt.

    PROMPT is a detailed description of what to generate.

    Examples:

      seedream generate "A beautiful landscape painting"

      seedream generate "A product photo" -m doubao-seedream-4-5-251128
    """
    client = get_client(ctx.obj.get("token"))
    try:
        payload: dict[str, object] = {
            "prompt": prompt,
            "model": model,
            "callback_url": callback_url,
        }
        if resolution:
            payload["size"] = resolution

        result = client.generate_image(**payload)  # type: ignore[arg-type]
        if output_json:
            print_json(result)
        else:
            print_image_result(result)
    except SeedreamError as e:
        print_error(e.message)
        raise SystemExit(1) from e


@click.command()
@click.argument("prompt")
@click.option(
    "-i",
    "--image-url",
    "image_urls",
    required=True,
    multiple=True,
    help="Image URL(s) to edit. Can be specified multiple times.",
)
@click.option(
    "-m",
    "--model",
    type=click.Choice(SEEDREAM_MODELS),
    default=DEFAULT_MODEL,
    help="Seedream model version.",
)
@click.option("--callback-url", default=None, help="Webhook callback URL.")
@click.option("--json", "output_json", is_flag=True, help="Output raw JSON.")
@click.pass_context
def edit(
    ctx: click.Context,
    prompt: str,
    image_urls: tuple[str, ...],
    model: str,
    callback_url: str | None,
    output_json: bool,
) -> None:
    """Edit or combine images using AI.

    PROMPT describes the desired edit. Use with one or more image URLs.

    Examples:

      seedream edit "Convert to anime style" -i https://example.com/photo.jpg

      seedream edit "Virtual try-on" -i person.jpg -i shirt.jpg
    """
    client = get_client(ctx.obj.get("token"))
    try:
        result = client.edit_image(
            action="edit",
            prompt=prompt,
            image_urls=list(image_urls),
            model=model,
            callback_url=callback_url,
        )
        if output_json:
            print_json(result)
        else:
            print_image_result(result)
    except SeedreamError as e:
        print_error(e.message)
        raise SystemExit(1) from e
