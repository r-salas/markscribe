#
#
#   Utils
#
#

import base64
import inspect
import io

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
                      openai_model: str = "gpt-4o-mini", temperature: float = 0):
    """
    Convert an image to markdown using OpenAI's API
    """
    if previous_md_content is None:
        previous_md_content = ""

    openai_client = OpenAI(
        api_key=openai_api_key,
    )

    img_png_base64 = image_to_png_base64(image_path)

    prompt = inspect.cleandoc(f"""
        Analyze the given image, which may be a continuation of a previous page, and convert its 
        content into a markdown document or continue an existing one. Follow these guidelines:
    
        1. If this image is a continuation of a previous page:
           - Seamlessly continue any incomplete elements (paragraphs, lists, tables, etc.) 
             from the previous page.
           - Do not repeat headings or other elements already covered in the previous page.
    
        2. Identify and transcribe only the text content clearly visible in the image, maintaining 
           its original structure and hierarchy. Do not infer or generate content that 
           is not explicitly present.
    
        3. For any images or visual elements within the main image:
           - Replace them with a factual description in square brackets, focusing on quantifiable 
             details rather than subjective interpretations, you must use the same language as the document for the description,
             e.g., [Image: Cat on couch. Orange tabby. Curled position. Blue velvet couch. Sunlit.]
    
        4. Preserve the document's overall structure, including:
           - Headings (use appropriate markdown heading levels)
           - Lists (bulleted or numbered)
           - Tables
           - Blockquotes
           - Code blocks (if applicable)
    
        5. Ignore irrelevant elements such as page numbers, headers, footers, or watermarks.
    
        6. If there are any formatting elements like bold, italic, or underlined text, 
           represent them using markdown syntax.
    
        7. For any charts or graphs:
           - Replace them with a factual description in square brackets, focusing on observable 
             data points and structure, you must use the same language as the document for the description, 
             e.g., [Chart: Bar graph. 5 vertical bars. X-axis: years 2019-2023. Y-axis: values 0-50 in increments of 10.
             Bar heights: 10, 15, 20, 35, 50.]
    
        8. If there are any handwritten notes or annotations, include them as blockquotes or 
           inline comments, clearly labeled as such.
    
        9. Maintain the logical flow and organization of the original document, 
           ensuring continuity with any previous content.
    
        10. If a table, list, or other structured element is split across pages, reconstruct it 
            completely in the markdown, combining information from both pages.
    
        11. If any text or element is unclear or partially obscured, indicate this with [...] 
            instead of guessing the content.
    
        12. For characters that appear distorted or ambiguous, represent them as best as possible 
            and indicate uncertainty with [?] where needed.
    
        13. Do not add any explanatory text, headers, or footers that are not present in the 
            original image.
    
        Answer only with the markdown representation of the image content. Do not include any
        explanations, introductions, or additional comments. 
        The response should consist solely of the markdown document.
    """)  # noqa: W291

    if previous_md_content:
        prompt += inspect.cleandoc(f"""
            Here is the previous content:
            ```markdown
            {previous_md_content}
            ```
        """)

    response = openai_client.chat.completions.create(
        model=openai_model,
        temperature=temperature,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_png_base64}"},
                    },
                ],
            }
        ],
    )

    md_block = response.choices[0].message.content
    md_block = md_block.removeprefix("```markdown\n").removesuffix("\n```")

    return md_block
