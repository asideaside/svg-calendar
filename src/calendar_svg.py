import os
import calendar
import datetime
from svgwrite import Drawing
import cairosvg


def generate_calendar_svg(year=None, month=None, start_day=0, file_name="calendar.svg", as_text=False):
    # Ensure the output directory exists
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Append file path to output directory
    file_path = os.path.join(output_dir, file_name)

    # Default to current year and month if not provided
    today = datetime.date.today()
    year = year or today.year
    month = month or today.month

    # Create a calendar object with the specified starting day (default: 0 = Monday)
    cal = calendar.Calendar(firstweekday=start_day)
    month_days = cal.monthdayscalendar(year, month)
    month_name = calendar.month_name[month]

    # SVG settings
    cell_width = 60
    cell_height = 40
    header_font_size = 58
    line_spacing = 60
    day_font_size = 32
    width = cell_width * 7
    height = cell_height * (len(month_days) + 2) + line_spacing + 20

    # Create SVG drawing
    dwg = Drawing(file_path, size=(width, height))
    y_offset = 10

    # Add month name (serif font)
    add_text(
        dwg,
        month_name,
        (width / 2, y_offset + header_font_size),
        font_size=header_font_size,
        font_family="serif",
        text_anchor="middle",
        as_text=as_text,
    )
    y_offset += header_font_size + line_spacing

    # Add day headers (sans-serif)
    days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
    if start_day != 0:
        days = days[start_day:] + days[:start_day]
    for i, day in enumerate(days):
        add_text(
            dwg,
            day,
            (i * cell_width + cell_width / 2, y_offset),
            font_size=day_font_size,
            font_family="sans-serif",
            text_anchor="middle",
            as_text=as_text,
        )
    
    # Add horizontal line under day headers
    line_y = y_offset + day_font_size + -20
    dwg.add(dwg.line(
        start=(0, line_y),
        end=(width, line_y),
        stroke="black",
        stroke_width=1
    ))

    y_offset = line_y + 20

    # Add grid and days (sans-serif)
    for week in month_days:
        for i, day in enumerate(week):
            if day != 0:
                add_text(
                    dwg,
                    str(day),
                    (i * cell_width + cell_width / 2, y_offset + cell_height / 2),
                    font_size=day_font_size,
                    font_family="sans-serif",
                    font_weight="300",
                    text_anchor="middle",
                    as_text=as_text,
                )
        y_offset += cell_height

    # Save SVG
    dwg.save()

    # Convert text to paths unless --as-text is specified
    if not as_text:
        convert_text_to_paths(file_path)

    return file_path


def add_text(dwg, text, insert, font_size=16, font_family="sans-serif", font_weight="normal", text_anchor="start", as_text=True):
    """Add text to the SVG."""
    dwg.add(dwg.text(
        text,
        insert=insert,
        font_size=font_size,
        font_family=font_family,
        font_weight=font_weight,
        text_anchor=text_anchor,
    ))


def convert_text_to_paths(svg_path):
    """Convert text in the SVG to paths."""
    path_svg_path = svg_path
    cairosvg.svg2svg(url=svg_path, write_to=path_svg_path)
    print(f"Text converted to paths.")


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate a calendar as an SVG file.")
    parser.add_argument("--year", type=int, help="Year of the calendar (default: current year).")
    parser.add_argument("--month", type=int, help="Month of the calendar (default: current month).")
    parser.add_argument("--start-day", type=int, default=0, help="Starting day of the week (0=Monday, 6=Sunday).")
    parser.add_argument("--output", type=str, default="calendar.svg", help="Output file name.")
    parser.add_argument("--as-text", action="store_true", help="Keep text as normal text tags (default is to convert to paths).")

    args = parser.parse_args()
    file_path = generate_calendar_svg(args.year, args.month, args.start_day, args.output, args.as_text)
    print(f"SVG calendar saved as {file_path}")
