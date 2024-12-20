#
#
#   PDF
#
#

import datetime
import os
import tempfile
import collections
import time

from tqdm.auto import tqdm
from typing import List, Optional

import pdf2image

from .utils import image_to_markdown


def pdf_to_md(path: str, openai_api_key: Optional[str] = None, verbose: bool = True,
              throttle: Optional[datetime.timedelta] = None) -> str:
    """
    Convert a PDF file to markdown using OpenAI's Vision Models

    Parameters
    ----------
    path
        File path to the PDF file
    openai_api_key
        OpenAI API key
    verbose
        Whether to display progress bar
    throttle
        Throttle time between API requests
    Returns
    -------
    str
        Markdown content
    """
    if openai_api_key is None:
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OpenAI API key is required. "
                             "Use `openai_api_key` argument or set `OPENAI_API_KEY` env var.")
        else:
            openai_api_key = os.environ["OPENAI_API_KEY"]

    with tempfile.TemporaryDirectory() as temp_dir:
        # Split PDF into images
        # noinspection PyTypeChecker
        images_from_path: List[str] = pdf2image.convert_from_path(path, output_folder=temp_dir,
                                                                  paths_only=True, fmt="png")

        markdown_content = ""
        previous_md_content_deque = collections.deque(maxlen=3)
        for image_path in tqdm(images_from_path, disable=not verbose, desc=path, unit="page"):
            previous_md_content_str = "\n".join(previous_md_content_deque)
            image_markdown = image_to_markdown(image_path, openai_api_key, previous_md_content_str)

            markdown_content += "\n" + image_markdown
            previous_md_content_deque.append(image_markdown)

            if throttle:
                time.sleep(throttle.total_seconds())

    return markdown_content
