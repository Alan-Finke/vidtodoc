class MarkdownWriter:
    """
    Utility class for creating and writing Markdown (.md) files on the fly.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.lines = []

    def add_heading(self, text: str, level: int = 1):
        self.lines.append(f"{'#' * level} {text}\n")

    def add_paragraph(self, text: str):
        self.lines.append(f"{text}\n")

    def add_list(self, items: list[str]):
        for item in items:
            self.lines.append(f"- {item}\n")

    def add_image(self, image_path: str, width: float, alt_text: str = "Image"):
        #self.lines.append(f"![{alt_text}]({image_path}){{: width=\"{width}\" }}\n")
        self.lines.append(f"<img src=\"{image_path}\" width=\"{width}\" alt=\"{alt_text}\" />\n")

    def add_code_block(self, code: str, language: str = ""):
        self.lines.append(f"```{language}\n{code}\n```\n")

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.writelines(self.lines)