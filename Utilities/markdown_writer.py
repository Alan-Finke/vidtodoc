class MarkdownWriter:
    """
    Utility class for creating and writing Markdown (.md) files on the fly.
    """

    def __init__(self):
        """Initialize the MarkdownWriter."""
        self.lines = []

    def add_heading(self, text: str, level: int = 1):
        """Add a heading to the document."""
        self.lines.append(f"{'#' * level} {text}\n")

    def add_paragraph(self, text: str):
        """Add a paragraph to the document."""
        self.lines.append(f"{text}\n")

    def add_list(self, items: list[str]):
        """Add a list to the document."""
        for item in items:
            self.lines.append(f"- {item}\n")

    def add_image(self, image_path: str, image_width: float, alt_text: str = "Image"):
        """Add an image to the document."""
        self.lines.append(f"<img src=\"{image_path}\" width=\"{image_width}\" alt=\"{alt_text}\" />\n")

    def add_code_block(self, code: str, language: str = ""):
        """Add a code block to the document."""
        self.lines.append(f"```{language}\n{code}\n```\n")

    def save(self, filepath: str):
        """Save the document to a file."""
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(self.lines)