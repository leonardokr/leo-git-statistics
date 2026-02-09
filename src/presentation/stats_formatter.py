from typing import Dict, Any

class StatsFormatter:
    """
    Provides static methods for formatting GitHub statistics into human-readable strings or HTML.
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
    def format_language_progress(languages: Dict[str, Dict[str, Any]]) -> str:
        """
        Generates HTML for a progress bar representing language distribution.

        :param languages: Dictionary containing language stats and percentages.
        :return: HTML string for the language progress bar.
        """
        progress_html = ""
        sorted_langs = sorted(languages.items(), key=lambda x: x[1].get("size", 0), reverse=True)
        
        for lang, data in sorted_langs:
            color = data.get("color", "#000000")
            percent = data.get("prop", 0)
            progress_html += (f'<span style="background-color: {color};'
                             f'width: {percent:0.5f}%;" '
                             f'class="progress-item"></span>')
        return progress_html

    @staticmethod
    def format_language_list(languages: Dict[str, Dict[str, Any]], delay_between: int = 150) -> str:
        """
        Generates HTML for an animated list of languages.

        :param languages: Dictionary containing language stats and percentages.
        :param delay_between: Animation delays between list items in milliseconds.
        :return: HTML string for the language list.
        """
        list_html = ""
        sorted_langs = sorted(languages.items(), key=lambda x: x[1].get("size", 0), reverse=True)
        
        for i, (lang, data) in enumerate(sorted_langs):
            color = data.get("color", "#000000")
            percent = data.get("prop", 0)
            list_html += f"""
            <li style="animation-delay: {i * delay_between}ms;">
                    <span class="lang-dot" style="background-color: {color};"></span>
                    <span class="lang">
                        {lang}
                    </span>
                    <span class="percent">
                        {percent:0.1f}%
                    </span>
            </li>"""
        return list_html
