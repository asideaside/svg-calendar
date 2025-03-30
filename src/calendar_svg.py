import os
import calendar
import datetime
from svgwrite import Drawing
import cairosvg
import csv
from collections import defaultdict


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

    # Load events from CSV files
    events = load_events(year, month)

    # Calculate dynamic cell size based on events
    max_event_lines = max(len(events[day]) for day in events) if events else 0
    max_event_length = max((len(event) for day in events for event in events[day]), default=0)
    largest_cell_height = max(100, 20 + max_event_lines * 20)  # Adjust height based on event count
    largest_cell_width = max(100, 20 + max_event_length * 8)  # Adjust width based on event title length
    largest_cell_size = max(largest_cell_width, largest_cell_height)  # Ensure square ratio close to 1:1

    # Use the largest square size for all day squares
    cell_width = cell_height = largest_cell_size

    # SVG settings
    padding = 20
    svg_settings = {
        "cell_width": cell_width,
        "cell_height": cell_height,
        "header_font_size": 40,  # Font size for month and year
        "line_spacing": 20,
        "day_font_size": 24,
        "event_font_size": 16,
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

    # Add calendar grid and days with events
    add_calendar_grid(dwg, month_days, start_day, y_offset, svg_settings, as_text, events)

    # Save SVG
    dwg.save()

    # Convert text to paths unless --as-text is specified
    if not as_text:
        convert_text_to_paths(file_path)

    return file_path


def load_events(year, month):
    """Load events from CSV files in the current directory and subdirectories."""
    events = defaultdict(list)
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".csv"):
                with open(os.path.join(root, file), newline="", encoding="utf-8") as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        event_date = datetime.datetime.strptime(row["date"], "%Y-%m-%d").date()
                        if event_date.year == year and event_date.month == month:
                            events[event_date.day].append(row["title"])
    return events


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


def add_calendar_grid(dwg, month_days, start_day, y_offset, settings, as_text, events):
    """Add the calendar grid and days with events to the SVG."""
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
                # Add day number slightly lower
                add_text(
                    dwg,
                    str(day),
                    (x + 10, y + 30),  # Lowered day number slightly
                    font_size=settings["day_font_size"],
                    font_family="Liberation Sans",
                    font_weight="300",
                    text_anchor="start",
                    as_text=as_text,
                )
                # Add events for the day
                if day in events:
                    event_y = y + 50  # Start below the day number with consistent spacing
                    for event in events[day]:
                        add_text(
                            dwg,
                            event,
                            (x + 10, event_y),
                            font_size=settings["event_font_size"],
                            font_family="Liberation Sans",
                            font_weight="normal",
                            text_anchor="start",
                            as_text=as_text,
                        )
                        event_y += 20  # Consistent spacing between events
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


def generate_annual_calendar_svg(year, file_name="annual_calendar.svg", as_text=False, show_day_names=False):
    """Generate an annual calendar SVG file with a 3x4 grid of monthly calendars."""
    # Ensure the output directory exists
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # SVG settings
    months_per_row = 3  # Number of months per row
    padding = 20  # Padding around the entire calendar
    horizontal_spacing = 10  # Horizontal spacing between monthly calendars

    # Calculate the maximum cell size across all months
    max_event_lines = 0
    max_event_length = 0
    for month in range(1, 13):
        month_event_lines, month_event_length = calculate_month_event_metrics(year, month)
        max_event_lines = max(max_event_lines, month_event_lines)
        max_event_length = max(max_event_length, month_event_length)

    # Calculate the largest cell size based on the maximum event metrics
    largest_cell_height = max(100, 20 + max_event_lines * 20)  # Adjust height based on event count
    largest_cell_width = max(100, 20 + max_event_length * 8)  # Adjust width based on event title length
    max_cell_size = max(largest_cell_width, largest_cell_height)  # Ensure square ratio close to 1:1

    # Calculate the dimensions of each month's calendar
    max_month_width = max_cell_size * 7  # 7 columns
    max_month_height = max_cell_size * 6 + 100  # 6 rows + header
    svg_width = max_month_width * months_per_row + padding * 2 + horizontal_spacing * (months_per_row - 1)
    svg_height = max_month_height * 4 + padding * 2  # 4 rows of months

    # Create SVG drawing
    file_path = os.path.join(output_dir, file_name)
    dwg = Drawing(file_path, size=(svg_width, svg_height))

    # Generate each month's calendar and place it in the grid
    for month in range(1, 13):
        x_offset = ((month - 1) % months_per_row) * (max_month_width + horizontal_spacing) + padding
        y_offset = ((month - 1) // months_per_row) * max_month_height + padding
        add_month_to_annual_calendar(dwg, year, month, x_offset, y_offset, max_month_width, max_month_height, as_text, show_day_names, max_cell_size)

    # Save the annual calendar
    dwg.save()

    # Convert text to paths unless --as-text is specified
    if not as_text:
        convert_text_to_paths(file_path)

    print(f"Annual SVG calendar saved as {file_path}")


def calculate_month_event_metrics(year, month):
    """Calculate the maximum number of event lines and the longest event title for a given month."""
    events = load_events(year, month)
    max_event_lines = max(len(events[day]) for day in events) if events else 0
    max_event_length = max((len(event) for day in events for event in events[day]), default=0)
    return max_event_lines, max_event_length


def add_month_to_annual_calendar(dwg, year, month, x_offset, y_offset, width, height, as_text, show_day_names, max_cell_size):
    """Add a single month's calendar to the annual calendar SVG."""
    # Create a calendar object
    cal = calendar.Calendar(firstweekday=6)  # Default to Sunday
    month_days = cal.monthdayscalendar(year, month)
    month_name = calendar.month_name[month]

    # Load events from CSV files
    events = load_events(year, month)

    # Use the maximum square size for all months
    cell_width = cell_height = max_cell_size

    # Add month name
    add_text(
        dwg,
        f"{month_name} {year}",
        (x_offset + width / 2, y_offset + 50),  # Centered month-year line
        font_size=36,  # Much larger font size for month-year line
        font_family="Liberation Sans",
        text_anchor="middle",
        fill="#46c2f2",
        as_text=as_text,
    )

    # Add day headers if enabled
    if show_day_names:
        days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
        for i, day in enumerate(days):
            add_text(
                dwg,
                day,
                (x_offset + i * cell_width + cell_width / 2, y_offset + 80),
                font_size=16,
                font_family="Liberation Sans",
                text_anchor="middle",
                as_text=as_text,
            )

    # Add calendar grid and days with events
    y_offset += 100  # Adjust for header
    for week in month_days:
        for i, day in enumerate(week):
            if day != 0:
                # Determine background color (orange for Sundays, light blue otherwise)
                background_color = "orange" if (i + 6) % 7 == 6 else "lightblue"
                x = x_offset + i * cell_width
                y = y_offset
                dwg.add(dwg.rect(
                    insert=(x + 5, y + 5),
                    size=(cell_width - 10, cell_height - 10),
                    rx=10,
                    ry=10,
                    fill=background_color,
                    fill_opacity=0.3
                ))
                # Add day number
                add_text(
                    dwg,
                    str(day),
                    (x + 10, y + 25),
                    font_size=14,
                    font_family="Liberation Sans",
                    text_anchor="start",
                    as_text=as_text,
                )
                # Add events for the day
                if day in events:
                    event_y = y + 40
                    for event in events[day]:
                        add_text(
                            dwg,
                            event,
                            (x + 10, event_y),
                            font_size=12,
                            font_family="Liberation Sans",
                            text_anchor="start",
                            as_text=as_text,
                        )
                        event_y += 20  # Fixed spacing between events
        y_offset += cell_height


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate a calendar as an SVG file.")
    parser.add_argument("--year", type=int, help="Year of the calendar (default: current year).")
    parser.add_argument("--month", type=int, help="Month of the calendar (default: current month).")
    parser.add_argument("--start-day", type=int, default=0, help="Starting day of the week (0=Monday, 6=Sunday).")
    parser.add_argument("--output", type=str, default="calendar.svg", help="Output file name.")
    parser.add_argument("--as-text", action="store_true", help="Keep text as normal text tags (default is to convert to paths).")
    parser.add_argument("--show-day-names", action="store_true", help="Show day names and line below them.")
    parser.add_argument("--annual", action="store_true", help="Generate an annual calendar.")

    args = parser.parse_args()

    if args.annual:
        generate_annual_calendar_svg(args.year or datetime.date.today().year, args.output, args.as_text, args.show_day_names)
    else:
        file_path = generate_calendar_svg(
            args.year, args.month, args.start_day, args.output, args.as_text, args.show_day_names
        )
        print(f"SVG calendar saved as {file_path}")
