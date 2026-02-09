from typing import Dict, Any


class StatsFormatter:
    """
    Provides static methods for formatting GitHub statistics into human-readable strings,
    HTML, or SVG elements.
    """

    @staticmethod
    def format_name(name: str) -> str:
        """
        Formats a user's name with a possessive suffix.

        :param name: The user's name.
        :return: Formatted name (e.g., "Alice's" or "James'").
        """
        if not name:
            return ""
        return f"{name}'" if name.endswith('s') else f"{name}'s"

    @staticmethod
    def format_number(number: Any) -> str:
        """
        Formats a number with thousands of separators.

        :param number: The number to format.
        :return: Formatted number string (e.g., '1,234').
        """
        try:
            return f"{int(number):,}"
        except (ValueError, TypeError):
            return str(number)

    @staticmethod
    def format_language_progress(languages: Dict[str, Dict[str, Any]], total_width: int = 310) -> str:
        """
        Generates SVG rect elements for a progress bar representing language distribution.

        :param languages: Dictionary containing language stats and percentages.
        :param total_width: Total width of the progress bar in pixels.
        :return: SVG string for the language progress bar.
        """
        progress_svg = ""
        sorted_langs = sorted(languages.items(), key=lambda x: x[1].get("size", 0), reverse=True)

        x_offset = 0
        for lang, data in sorted_langs:
            color = data.get("color", "#000000")
            percent = data.get("prop", 0)
            width = (percent / 100) * total_width

            if width > 0:
                progress_svg += f'<rect x="{x_offset:.2f}" y="0" width="{width:.2f}" height="8" fill="{color}"/>'
                x_offset += width

        return progress_svg

    @staticmethod
    def format_language_list(languages: Dict[str, Dict[str, Any]], max_items: int = 8, text_color: str = "#24292f", percent_color: str = "#57606a") -> str:
        """
        Generates HTML for a compact list of languages.

        :param languages: Dictionary containing language stats and percentages.
        :param max_items: Maximum number of languages to display.
        :param text_color: Color for language names.
        :param percent_color: Color for percentage values.
        :return: HTML string for the language list.
        """
        list_html = ""
        sorted_langs = sorted(languages.items(), key=lambda x: x[1].get("size", 0), reverse=True)

        for i, (lang, data) in enumerate(sorted_langs[:max_items]):
            color = data.get("color", "#000000")
            percent = data.get("prop", 0)
            list_html += f'''<li style="display: flex; align-items: center;">
                <span style="width: 10px; height: 10px; border-radius: 50%; background-color: {color}; margin-right: 6px;"></span>
                <span style="color: {text_color};">{lang}</span>
                <span style="color: {percent_color}; margin-left: 4px; font-size: 11px;">{percent:.1f}%</span>
            </li>'''

        return list_html
