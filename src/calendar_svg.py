import os
import calendar
import datetime
from svgwrite import Drawing
import cairosvg


def generate_calendar_svg(
    year=None, month=None, start_day=6, file_name="calendar.svg", as_text=False, show_day_names=False
):
    """Generate a calendar SVG file."""
    # Ensure the output directory exists
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Default to Sunday if start_day is not provided
    start_day = start_day or 6

    # Default to current year and month if not provided
    today = datetime.date.today()
    year = year or today.year
    month = month or today.month

    # Create a calendar object
    cal = calendar.Calendar(firstweekday=start_day)
    month_days = cal.monthdayscalendar(year, month)
    month_name = calendar.month_name[month]

    # SVG settings
    padding = 20
    cell_width = 100  # Expanded to fit more text
    cell_height = 100  # Expanded to fit more text
    svg_settings = {
        "cell_width": cell_width,
        "cell_height": cell_height,
        "header_font_size": 40,  # Font size for month and year
        "line_spacing": 20,
        "day_font_size": 24,
        "width": cell_width * 7 + padding * 2,
        "height": cell_height * (len(month_days) + (2 if show_day_names else 1)) + padding * 2,
        "padding": padding,
    }

    # Create SVG drawing
    file_path = os.path.join(output_dir, file_name)
    dwg = Drawing(file_path, size=(svg_settings["width"], svg_settings["height"]))

    # Add month and year
    y_offset = add_month_and_year(dwg, year, month_name, svg_settings, as_text)

    # Add day headers if enabled
    if show_day_names:
        y_offset = add_day_headers(dwg, start_day, y_offset, svg_settings, as_text)

    # Add calendar grid and days
    add_calendar_grid(dwg, month_days, start_day, y_offset, svg_settings, as_text)

    # Save SVG
    dwg.save()

    # Convert text to paths unless --as-text is specified
    if not as_text:
        convert_text_to_paths(file_path)

    return file_path


def add_month_and_year(dwg, year, month_name, settings, as_text):
    """Add the month and year to the SVG on the same line."""
    y_offset = settings["padding"]
    add_text(
        dwg,
        f"{month_name} {year}",
        (settings["width"] / 2, y_offset + settings["header_font_size"]),
        font_size=settings["header_font_size"],
        font_family="Liberation Sans",  # Changed to Liberation Sans
        text_anchor="middle",
        fill="#46c2f2",
        as_text=as_text,
    )
    return y_offset + settings["header_font_size"] + settings["line_spacing"]


def add_day_headers(dwg, start_day, y_offset, settings, as_text):
    """Add day headers to the SVG."""
    days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
    if start_day != 0:
        days = days[start_day:] + days[:start_day]
    for i, day in enumerate(days):
        add_text(
            dwg,
            day,
            (i * settings["cell_width"] + settings["cell_width"] / 2 + settings["padding"], y_offset),
            font_size=settings["day_font_size"],
            font_family="Liberation Sans",  # Changed to Liberation Sans
            text_anchor="middle",
            as_text=as_text,
        )
    
    # Add horizontal line under day headers
    line_y = y_offset + settings["day_font_size"] - 10
    dwg.add(dwg.line(
        start=(settings["padding"], line_y),
        end=(settings["width"] - settings["padding"], line_y),
        stroke="black",
        stroke_width=1
    ))
    return line_y + settings["line_spacing"]


def add_calendar_grid(dwg, month_days, start_day, y_offset, settings, as_text):
    """Add the calendar grid and days to the SVG."""
    for week in month_days:
        for i, day in enumerate(week):
            if day != 0:
                # Calculate the actual weekday (0=Monday, 6=Sunday)
                actual_weekday = (i + start_day) % 7
                # Determine background color (orange for Sundays, light blue otherwise)
                background_color = "orange" if actual_weekday == 6 else "lightblue"
                x = i * settings["cell_width"] + settings["padding"]
                y = y_offset
                dwg.add(dwg.rect(
                    insert=(x + 5, y + 5),
                    size=(settings["cell_width"] - 10, settings["cell_height"] - 10),  # Ensure square background
                    rx=10,  # Rounded corners
                    ry=10,
                    fill=background_color,
                    fill_opacity=0.3
                ))
                # Add day number in the upper-left corner
                add_text(
                    dwg,
                    str(day),
                    (x + 10, y + 25),  # Adjusted for upper-left alignment
                    font_size=settings["day_font_size"],
                    font_family="Liberation Sans",  # Changed to Liberation Sans
                    font_weight="300",
                    text_anchor="start",
                    as_text=as_text,
                )
        y_offset += settings["cell_height"]


def add_text(dwg, text, insert, font_size=16, font_family="Liberation Sans", font_weight="normal", text_anchor="start", fill="black", as_text=True):
    """Add text to the SVG."""
    dwg.add(dwg.text(
        text,
        insert=insert,
        font_size=font_size,
        font_family=font_family,  # Changed to Liberation Sans
        font_weight=font_weight,
        text_anchor=text_anchor,
        fill=fill,
    ))


def convert_text_to_paths(svg_path):
    """Convert text in the SVG to paths."""
    path_svg_path = svg_path
    cairosvg.svg2svg(url=svg_path, write_to=path_svg_path)
    print(f"Text converted to paths.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate a calendar as an SVG file.")
    parser.add_argument("--year", type=int, help="Year of the calendar (default: current year).")
    parser.add_argument("--month", type=int, help="Month of the calendar (default: current month).")
    parser.add_argument("--start-day", type=int, default=0, help="Starting day of the week (0=Monday, 6=Sunday).")
    parser.add_argument("--output", type=str, default="calendar.svg", help="Output file name.")
    parser.add_argument("--as-text", action="store_true", help="Keep text as normal text tags (default is to convert to paths).")
    parser.add_argument("--show-day-names", action="store_true", help="Show day names and line below them.")

    args = parser.parse_args()
    file_path = generate_calendar_svg(
        args.year, args.month, args.start_day, args.output, args.as_text, args.show_day_names
    )
    print(f"SVG calendar saved as {file_path}")
