from typing import Dict, Any, List, Tuple
import colorsys


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

    @staticmethod
    def _generate_palette_colors(
        count: int,
        hue: int = 210,
        saturation_range: List[int] = None,
        lightness_range: List[int] = None
    ) -> List[str]:
        """
        Generates a list of colors within a specified HSL range.

        :param count: Number of colors to generate.
        :param hue: Base hue value (0-360).
        :param saturation_range: [min, max] saturation percentage (0-100).
        :param lightness_range: [min, max] lightness percentage (0-100).
        :return: List of hex color strings.
        """
        if saturation_range is None:
            saturation_range = [60, 85]
        if lightness_range is None:
            lightness_range = [35, 65]

        colors = []
        sat_min, sat_max = saturation_range[0] / 100, saturation_range[1] / 100
        light_min, light_max = lightness_range[0] / 100, lightness_range[1] / 100

        for i in range(count):
            t = i / max(count - 1, 1)
            saturation = sat_min + (sat_max - sat_min) * (1 - t)
            lightness = light_min + (light_max - light_min) * t

            r, g, b = colorsys.hls_to_rgb(hue / 360, lightness, saturation)
            hex_color = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
            colors.append(hex_color)

        return colors

    @staticmethod
    def _treemap_slice_dice(
        values: List[float],
        x: float,
        y: float,
        width: float,
        height: float,
        vertical: bool = True
    ) -> List[Tuple[float, float, float, float]]:
        """
        Slice-and-dice treemap algorithm.

        :param values: List of values (proportions).
        :param x: Starting x position.
        :param y: Starting y position.
        :param width: Total width available.
        :param height: Total height available.
        :param vertical: Start with vertical slicing.
        :return: List of tuples (x, y, width, height) for each rectangle.
        """
        if not values or width <= 0 or height <= 0:
            return []

        total = sum(values)
        if total == 0:
            return []

        rects = []
        n = len(values)

        if n == 1:
            return [(x, y, width, height)]

        if n == 2:
            ratio = values[0] / total
            if vertical:
                w1 = width * ratio
                rects.append((x, y, w1, height))
                rects.append((x + w1, y, width - w1, height))
            else:
                h1 = height * ratio
                rects.append((x, y, width, h1))
                rects.append((x, y + h1, width, height - h1))
            return rects

        mid = n // 2
        left_values = values[:mid]
        right_values = values[mid:]
        left_sum = sum(left_values)
        right_sum = sum(right_values)
        ratio = left_sum / total if total > 0 else 0.5

        if vertical:
            left_width = width * ratio
            rects.extend(StatsFormatter._treemap_slice_dice(
                left_values, x, y, left_width, height, not vertical
            ))
            rects.extend(StatsFormatter._treemap_slice_dice(
                right_values, x + left_width, y, width - left_width, height, not vertical
            ))
        else:
            left_height = height * ratio
            rects.extend(StatsFormatter._treemap_slice_dice(
                left_values, x, y, width, left_height, not vertical
            ))
            rects.extend(StatsFormatter._treemap_slice_dice(
                right_values, x, y + left_height, width, height - left_height, not vertical
            ))

        return rects

    @staticmethod
    def format_puzzle_blocks(
        languages: Dict[str, Dict[str, Any]],
        width: int = 400,
        height: int = 200,
        hue: int = 210,
        saturation_range: List[int] = None,
        lightness_range: List[int] = None
    ) -> str:
        """
        Generates SVG rect elements for a treemap-style puzzle of languages.

        :param languages: Dictionary containing language stats and percentages.
        :param width: Total width of the puzzle area.
        :param height: Total height of the puzzle area.
        :param hue: Base hue for the color palette.
        :param saturation_range: [min, max] saturation.
        :param lightness_range: [min, max] lightness.
        :return: SVG string with puzzle blocks.
        """
        sorted_langs = sorted(languages.items(), key=lambda x: x[1].get("size", 0), reverse=True)

        if not sorted_langs:
            return ""

        values = [data.get("prop", 0) for _, data in sorted_langs]
        names = [lang for lang, _ in sorted_langs]
        percentages = values[:]

        colors = StatsFormatter._generate_palette_colors(
            len(sorted_langs),
            hue,
            saturation_range,
            lightness_range
        )

        rects = StatsFormatter._treemap_slice_dice(values, 0, 0, width, height)

        svg_blocks = ""
        for i, ((x, y, w, h), name, pct) in enumerate(zip(rects, names, percentages)):
            if w > 0 and h > 0:
                delay_class = f"delay-{min(i + 1, 8)}"
                svg_blocks += f'<rect class="puzzle-rect {delay_class}" x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{colors[i]}"/>\n'

                center_x = x + w / 2
                center_y = y + h / 2

                if w > 40 and h > 25:
                    svg_blocks += f'<text class="puzzle-text" x="{center_x:.2f}" y="{center_y - 2:.2f}" text-anchor="middle" dominant-baseline="middle">{name}</text>\n'
                    svg_blocks += f'<text class="puzzle-percent" x="{center_x:.2f}" y="{center_y + 10:.2f}" text-anchor="middle" dominant-baseline="middle">{pct:.1f}%</text>\n'
                elif w > 30 and h > 18:
                    svg_blocks += f'<text class="puzzle-percent" x="{center_x:.2f}" y="{center_y:.2f}" text-anchor="middle" dominant-baseline="middle">{pct:.1f}%</text>\n'

        return svg_blocks
