#
#
#   CLI
#
#

import datetime
from typing import Annotated

import typer


def markscribe(input_path: Annotated[str, typer.Argument(help="Input file path", metavar="input")],
               openai_api_key: Annotated[str, typer.Option(help="OpenAI API key", envvar="OPENAI_API_KEY")],
               output_path: Annotated[str, typer.Argument(help="Markdown output file path", metavar="output")] = None,
               verbose: Annotated[bool, typer.Option(help="Whether or not display progress bar")] = True,
               throttle_seconds: Annotated[float, typer.Option(help="Throttle time between API requests")] = None):
    if output_path is None:
        output_path = input_path + ".md"

    if throttle_seconds:
        throttle = datetime.timedelta(seconds=throttle_seconds)
    else:
        throttle = None

    if input_path.endswith(".pdf"):
        from markscribe.documents.pdf import pdf_to_md
        markdown = pdf_to_md(input_path, openai_api_key, verbose=verbose, throttle=throttle)
    else:
        raise NotImplementedError(f"Unsupported file type: {input_path}")

    with open(output_path, "w") as fp:
        fp.write(markdown)


def run():
    typer.run(markscribe)


if __name__ == "__main__":
    run()
