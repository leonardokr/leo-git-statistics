from typing import Dict, Any, List
import math

from src.presentation.visual_algorithms import generate_palette_colors, treemap_slice_dice


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
    def format_language_progress(languages: Dict[str, Dict[str, Any]], total_width: int = 455) -> str:
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

    @staticmethod
    def format_puzzle_blocks(
        languages: Dict[str, Dict[str, Any]],
        width: int = 400,
        height: int = 200,
        hue: int = 210,
        saturation_range: List[int] = None,
        lightness_range: List[int] = None,
        hue_spread: int = 60,
        gap: int = 2
    ) -> str:
        """
        Generates SVG rect elements for a treemap-style puzzle of languages.

        :param languages: Dictionary containing language stats and percentages.
        :param width: Total width of the puzzle area.
        :param height: Total height of the puzzle area.
        :param hue: Base hue for the color palette.
        :param saturation_range: [min, max] saturation.
        :param lightness_range: [min, max] lightness.
        :param hue_spread: Total spread of hues around the base (0-180).
        :param gap: Gap between blocks in pixels.
        :return: SVG string with puzzle blocks.
        """
        sorted_langs = sorted(languages.items(), key=lambda x: x[1].get("size", 0), reverse=True)

        if not sorted_langs:
            return ""

        raw_values = [data.get("prop", 0) for _, data in sorted_langs]
        names = [lang for lang, _ in sorted_langs]
        percentages = raw_values[:]

        scaled_values = [math.sqrt(v) for v in raw_values]
        scale_total = sum(scaled_values)
        if scale_total > 0:
            scaled_values = [v / scale_total * 100 for v in scaled_values]

        colors = generate_palette_colors(
            len(sorted_langs),
            hue,
            saturation_range,
            lightness_range,
            hue_spread
        )

        rects = treemap_slice_dice(scaled_values, 0, 0, width, height)

        svg_blocks = ""
        half_gap = gap / 2
        for i, ((x, y, w, h), name, pct) in enumerate(zip(rects, names, percentages)):
            if w > gap and h > gap:
                delay_class = f"delay-{min(i + 1, 8)}"
                rx = min(4, w / 4, h / 4)

                adj_x = x + half_gap
                adj_y = y + half_gap
                adj_w = w - gap
                adj_h = h - gap

                svg_blocks += f'<rect class="puzzle-rect {delay_class}" x="{adj_x:.2f}" y="{adj_y:.2f}" width="{adj_w:.2f}" height="{adj_h:.2f}" rx="{rx:.1f}" fill="{colors[i]}"/>\n'

                center_x = x + w / 2
                center_y = y + h / 2

                if adj_w > 40 and adj_h > 25:
                    svg_blocks += f'<text class="puzzle-text" x="{center_x:.2f}" y="{center_y - 2:.2f}" text-anchor="middle" dominant-baseline="middle">{name}</text>\n'
                    svg_blocks += f'<text class="puzzle-percent" x="{center_x:.2f}" y="{center_y + 10:.2f}" text-anchor="middle" dominant-baseline="middle">{pct:.1f}%</text>\n'
                elif adj_w > 30 and adj_h > 18:
                    svg_blocks += f'<text class="puzzle-percent" x="{center_x:.2f}" y="{center_y:.2f}" text-anchor="middle" dominant-baseline="middle">{pct:.1f}%</text>\n'

        return svg_blocks
