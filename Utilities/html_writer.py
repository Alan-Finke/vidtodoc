import os

class HTMLWriter:
    """
    Utility class for creating HTML files using a template with placeholders.
    """

    def __init__(self, templates_path):
        """
        Initialize the HTMLWriter with the path to the templates directory.
        """
        self.templates_path = templates_path
        self.title = ""
        self.summary = ""
        self.steps_html = []

    def add_title(self, title):
        """Add a title to the document."""
        self.title = title

    def add_summary(self, summary):
        """Add a summary to the document."""
        self.summary = summary

    def add_step(self, step, text, image_path, image_width, alt_text="Image"):
        """Add a step to the document."""
        # Read the step template
        template_path = os.path.join(self.templates_path, "step_template.html")
        # Throw an exception if the template file doesn't exist
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")
        # Read the step template
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
        # Replace placeholders
        step_html = template.replace("{{STEP}}", str(step))
        step_html = step_html.replace("{{TEXT}}", text)
        step_html = step_html.replace("{{ALT_TEXT}}", alt_text)
        step_html = step_html.replace("{{IMAGE}}", image_path)
        step_html = step_html.replace("{{WIDTH}}", str(image_width))
        # Append the step HTML to the list
        self.steps_html.append(step_html)

    def save(self, output_path):
        """Save the document to a file."""
        # Read the main template
        template_path = os.path.join(self.templates_path, "main_template.html")
        # Throw an exception if the template file doesn't exist
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
        # Replace placeholders
        html_content = template.replace("{{TITLE}}", self.title)
        html_content = html_content.replace("{{SUMMARY}}", self.summary)
        html_content = html_content.replace("{{STEPS}}", "\n".join(self.steps_html))
        # Write to output file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)