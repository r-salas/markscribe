#
#
#   Utils
#
#

import base64
import inspect
import io
import re

import PIL.Image
from openai import OpenAI


def image_to_png_base64(image_path: str):
    """
    Convert an image to a PNG base64 string
    """
    with PIL.Image.open(image_path) as img:
        width, height = img.size
        max_dim = max(width, height)
        if max_dim > 1024:
            scale_factor = 1024 / max_dim
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            img = img.resize((new_width, new_height))

        buffered = io.BytesIO()
        img.save(buffered, format="PNG")

    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str


def image_to_markdown(image_path: str, openai_api_key: str, previous_md_content: str | None = None,
                      openai_model: str = "gpt-6-luna", temperature: float | None = None):
    """
    Convert an image to markdown using OpenAI's API
    """
    if previous_md_content is None:
        previous_md_content = ""

    openai_client = OpenAI(
        api_key=openai_api_key,
    )

    img_png_base64 = image_to_png_base64(image_path)

    system_prompt = inspect.cleandoc("""
        You are a precise document transcription engine. You receive an image of a single document
        page and convert it into clean GitHub-Flavored Markdown (GFM). Your output is appended
        directly to the Markdown of the previous pages, so it must read as a seamless continuation.

        # Core principles
        - Fidelity: transcribe exactly what is visible. Never summarize, paraphrase, translate,
          correct, complete or invent content.
        - Language: keep the original language of the document for everything, including image
          and chart descriptions.
        - Reading order: follow the natural reading order of the page (e.g. multi-column layouts
          column by column, top to bottom).

        # Continuity with previous pages
        When previous content is provided, it is context only. Never repeat it.
        - If the page starts in the middle of a paragraph, sentence or list, continue it directly
          without adding a heading or restarting the element.
        - If a table continues from the previous page, output only the new rows, without
          repeating the header row or separator, so they join the existing table.
        - Keep numbering of ordered lists, footnotes and heading levels consistent with the
          previous content.
        - Do not repeat running headers, titles or section headings already present.

        # Structure and formatting
        - Headings: map the visual hierarchy to `#`, `##`, `###`, etc. consistently.
        - Lists: use `-` for bullets and `1.` for numbered lists, preserving nesting. Use
          `- [ ]` / `- [x]` for checkboxes.
        - Tables: use GFM pipe tables. For merged cells, repeat the value or leave the cell
          empty; never drop columns.
        - Emphasis: use `**bold**`, `*italic*`, `~~strikethrough~~`. Represent underlined text
          as `<u>text</u>`.
        - Code: use fenced code blocks with a language tag when identifiable.
        - Math: use LaTeX, `$...$` inline and `$$...$$` for display equations.
        - Quotes: use `>` blockquotes.
        - Links and footnotes: keep visible URLs as links; use `[^n]` footnote syntax for
          footnotes.

        # Visual elements
        - Images, photos, diagrams, logos: replace them with a concise, factual description in
          square brackets focused on observable details, not interpretation. Transcribe any
          text they contain.
          Example: [Image: Orange tabby cat curled up on a blue velvet couch, sunlit.]
        - Charts and graphs: describe type, axes, labels, legend and the data values that can be
          read. If the data is clearly readable, also provide it as a Markdown table.
          Example: [Chart: Bar chart. X-axis: years 2019-2023. Y-axis: 0-50. Values: 10, 15, 20,
          35, 50.]
        - Handwritten notes or annotations: include them as blockquotes labeled as handwritten,
          e.g. `> [Handwritten: ...]`.

        # What to omit
        - Page numbers, running headers/footers, watermarks, scanning artifacts and decorative
          elements.
        - Any commentary, introduction or explanation of your own.

        # Uncertainty
        - Illegible or obscured text: use `[...]`. Do not guess.
        - Ambiguous characters or words: give your best reading followed by `[?]`.

        # Output
        - Respond only with the Markdown content of this page. Do not wrap it in a code fence.
        - If the page is blank or contains nothing to transcribe, respond with an empty string.
    """)

    user_prompt = "Transcribe this page into Markdown."
    if previous_md_content:
        user_prompt = (
            "Markdown of the previous pages (context only, do not repeat it):\n"
            "<previous_content>\n"
            f"{previous_md_content}\n"
            "</previous_content>\n\n"
            "Transcribe this page into Markdown, continuing seamlessly from the previous content."
        )

    response = openai_client.chat.completions.create(
        model=openai_model,
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_png_base64}"},
                    },
                ],
            }
        ],
    )

    md_block = (response.choices[0].message.content or "").strip()
    md_block = re.sub(r"^```(?:markdown|md)?\n(.*)\n```$", r"\1", md_block, flags=re.DOTALL)

    return md_block
