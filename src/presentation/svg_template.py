import re
from typing import Dict, List, Optional
from src.utils.file_system import FileSystem

class SVGTemplate:
    """
    Handles rendering and saving of SVG templates by applying string replacements.
    """

    def __init__(self, template_path: str, output_dir: str, fs: FileSystem = None):
        """
        Initializes the SVGTemplate engine.

        :param template_path: Directory path where templates are stored.
        :param output_dir: Directory path where rendered images will be saved.
        :param fs: FileSystem instance for I/O operations. Defaults to a new
                   ``FileSystem`` if not provided.
        """
        self.template_path = template_path
        self.output_dir = output_dir
        self.fs = fs or FileSystem()

    def render_and_save(self, 
                        template_file: str, 
                        output_filename_base: str, 
                        replacements: Dict[str, str],
                        theme_suffix: str = "") -> None:
        """
        Renders a template with replacements and saves it to disk.

        :param template_file: Template filename to read.
        :param output_filename_base: Base filename for the output (without .svg).
        :param replacements: Dictionary of placeholders and their replacement values.
        :param theme_suffix: Suffix to append to the output filename.
        """
        self.fs.ensure_directory(self.output_dir)
        
        content = self.fs.read_file(f"{self.template_path}{template_file}")
        rendered = self._apply_replacements(content, replacements)
        
        output_path = f"{self.output_dir}/{output_filename_base}{theme_suffix}.svg"
        self.fs.write_file(output_path, rendered)

    def _apply_replacements(self, content: str, replacements: Dict[str, str]) -> str:
        """
        Applies placeholders replacements to the content using regular expressions.

        Placeholders are expected to be in the format '{{ placeholder }}'.

        :param content: The raw string content of the template.
        :param replacements: Dictionary mapping placeholders to values.
        :return: The rendered content.
        """
        for placeholder, value in replacements.items():
            content = re.sub(rf"{{{{ {placeholder} }}}}", str(value), content)
        return content
