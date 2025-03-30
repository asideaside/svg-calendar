import os
import calendar
import datetime
from svgwrite import Drawing
import cairosvg
import csv
from collections import defaultdict


def confirm_overwrite(file_path, overwrite=False):
    """Prompt the user for confirmation to overwrite an existing file."""
    if os.path.exists(file_path) and not overwrite:
        response = input(f"The file '{file_path}' already exists. Overwrite? (Y/n): ").strip().lower()
        if response not in ("y", "yes", ""):
            print("Operation canceled.")
            exit(0)


def resolve_file_path(file_name):
    """Resolve the file path relative to the script's directory."""
    return os.path.join(os.path.dirname(__file__), file_name)


def load_csv(file_path, required_columns, debug=False):
    """Load a CSV file and validate required columns."""
    if not os.path.exists(file_path):
        if debug:
            print(f"File '{file_path}' not found.")
        return []

    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(row for row in csvfile if not row.strip().startswith("#"))  # Skip comments
        if not all(col in reader.fieldnames for col in required_columns):
            raise KeyError(f"The file '{file_path}' must contain the columns: {', '.join(required_columns)}")
        return list(reader)


def load_emoji_map(emoji_file, debug=False):
    """Load the emoji map from a CSV file."""
    emoji_file_path = resolve_file_path(emoji_file)
    emoji_map = {}
    rows = load_csv(emoji_file_path, ["type", "emoji"], debug)
    for row in rows:
        emoji_map[row["type"].strip().lower()] = row["emoji"].strip()
        if debug:
            print(f"Loaded emoji: {row['emoji']} for type: {row['type']}")
    return emoji_map


def validate_event_date(month, day, debug=False):
    """Validate the month and day of an event."""
    try:
        datetime.date(2000, month, day)  # Use a dummy year to validate the date
        return True
    except ValueError:
        if debug:
            print(f"Invalid date: month={month}, day={day}")
        return False


def load_events(year, month, events_file, emoji_file, debug=False):
    """Load events from the specified events CSV file and map emojis."""
    events_file_path = resolve_file_path(events_file)
    emoji_map = load_emoji_map(emoji_file, debug)
    events = defaultdict(list)

    rows = load_csv(events_file_path, ["month", "day", "title", "type"], debug)
    for row in rows:
        try:
            event_month = int(row["month"])
            event_day = int(row["day"])

            # Validate the date
            if not validate_event_date(event_month, event_day, debug):
                continue

            if event_month == month:
                event_type = row.get("type", "").strip().lower()
                emoji = emoji_map.get(event_type, "")
                event_title = f"{emoji} {row['title']}" if emoji else row["title"]
                events[event_day].append(event_title)
                if debug:
                    print(f"Loaded event: {event_title} on {event_month:02d}-{event_day:02d}")
        except (ValueError, KeyError) as e:
            if debug:
                print(f"Skipping row in file {events_file_path}: {e}")
    return events


def wrap_text(text, max_width, font_size):
    """Wrap text to fit within a specified width."""
    import textwrap
    max_chars = max_width // (font_size // 2)  # Approximate character limit per line
    return textwrap.wrap(text, width=max_chars)


def add_text(dwg, text, insert, font_size=16, font_family="fonts/NotoColorEmoji.ttf, Liberation Sans, Arial, sans-serif", font_weight="normal", text_anchor="start", fill="black", as_text=True):
    """Add text to the SVG."""
    print(f"Adding text: '{text}' with font: {font_family}")
    dwg.add(dwg.text(
        text,
        insert=insert,
        font_size=font_size,
        font_family=font_family,  # Use local font with fallbacks
        font_weight=font_weight,
        text_anchor=text_anchor,
        fill=fill,
    ))


def add_month_and_year(dwg, year, month_name, settings, as_text):
    """Add the month and year to the SVG on the same line."""
    y_offset = settings["padding"]
    add_text(
        dwg,
        f"{month_name} {year}",
        (settings["width"] / 2, y_offset + settings["header_font_size"]),
        font_size=settings["header_font_size"],
        font_family="fonts/NotoColorEmoji.ttf, Liberation Sans, Arial, sans-serif",  # Use local font with fallbacks
        text_anchor="middle",
        fill="#46c2f2",
        as_text=as_text,
    )
    return y_offset + settings["header_font_size"] + settings["line_spacing"]


def add_day_headers(dwg, start_day, y_offset, settings, as_text):
    """Add day headers to the SVG."""
    # Define the default day headers
    days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']

    # Rotate the day headers based on the start_day
    if start_day != 0:
        days = days[start_day:] + days[:start_day]

    # Add each day header to the SVG
    for i, day in enumerate(days):
        add_text(
            dwg,
            day,
            (i * settings["cell_width"] + settings["cell_width"] / 2 + settings["padding"], y_offset),
            font_size=settings["day_font_size"],
            font_family="fonts/NotoColorEmoji.ttf, Liberation Sans, Arial, sans-serif",  # Use local font with fallbacks
            text_anchor="middle",
            as_text=as_text,
        )

    # Add a line below the day headers
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
                actual_weekday = (i + start_day) % 7
                background_color = "orange" if actual_weekday == 6 else "lightblue"
                x = i * settings["cell_width"] + settings["padding"]
                y = y_offset

                # Calculate the maximum rendered width of all events for this day
                max_event_width = 0
                for event in events.get(day, []):
                    # Estimate the rendered width of the event text
                    event_width = sum(
                        2 if char in "🎂🔰🎓🧪" else 1 for char in event
                    ) * (settings["event_font_size"] // 2)
                    max_event_width = max(max_event_width, event_width)

                # Add extra padding for emojis and spacing
                dynamic_cell_width = max(settings["cell_width"], max_event_width + 20)

                # Debugging: Log the calculated dimensions
                print(f"Day {day}: dynamic_cell_width={dynamic_cell_width}, max_event_width={max_event_width}")

                # Adjust the day square size dynamically
                dwg.add(dwg.rect(
                    insert=(x + 5, y + 5),
                    size=(dynamic_cell_width - 10, settings["cell_height"] - 10),
                    rx=10,
                    ry=10,
                    fill=background_color,
                    fill_opacity=0.3
                ))

                # Add day number
                add_text(
                    dwg,
                    str(day),
                    (x + 10, y + 30),
                    font_size=settings["day_font_size"],
                    font_family="Liberation Sans, Arial, sans-serif",  # Use a text-specific font
                    font_weight="300",
                    text_anchor="start",
                    as_text=as_text,
                )

                # Add events for the day
                event_y = y + 50
                for event in events.get(day, []):
                    # Split the emoji and the text
                    if event.startswith("🎂") or event.startswith("🔰") or event.startswith("🎓") or event.startswith("🧪"):
                        emoji, title = event.split(" ", 1)
                    else:
                        emoji, title = "", event

                    # Add the emoji
                    if emoji:
                        add_text(
                            dwg,
                            emoji,
                            (x + 10, event_y),
                            font_size=settings["event_font_size"],
                            font_family="Noto Color Emoji",  # Use emoji-specific font
                            font_weight="normal",
                            text_anchor="start",
                            as_text=as_text,
                        )

                    # Add the title with a small offset
                    add_text(
                        dwg,
                        title,
                        (x + 30, event_y),  # Offset the title to the right of the emoji
                        font_size=settings["event_font_size"],
                        font_family="Liberation Sans, Arial, sans-serif",  # Use text-specific font
                        font_weight="normal",
                        text_anchor="start",
                        as_text=as_text,
                    )
                    event_y += 25  # Fixed spacing between events
        y_offset += settings["cell_height"]


def generate_calendar_svg(
    year=None, month=None, start_day=6, file_name=None, as_text=False, show_day_names=False,
    events_file="events.csv", emoji_file="emoji.csv", debug=False, overwrite=False
):
    """Generate a calendar SVG file."""
    # Ensure the output directory exists
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Default to Sunday if start_day is not provided
    start_day = start_day or 6  # 6 corresponds to Sunday in Python's calendar module

    # Default to current year and month if not provided
    today = datetime.date.today()
    year = year or today.year
    month = month or today.month

    # Default output file name for monthly calendar
    if not file_name:
        file_name = f"calendar_monthly_{year}-{month:02d}.svg"

    # Create a calendar object
    cal = calendar.Calendar(firstweekday=start_day)
    month_days = cal.monthdayscalendar(year, month)
    month_name = calendar.month_name[month]

    # Load events from CSV files
    events = load_events(year, month, events_file, emoji_file, debug)

    # Calculate dynamic cell size based on events
    max_event_lines = max(len(events[day]) for day in events) if events else 0
    max_event_length = max(
        (len(event) + 2 if event.startswith("🎂") or event.startswith("🔰") or event.startswith("🎓") or event.startswith("🧪") else len(event))
        for day in events for event in events[day]
    ) if events else 0
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

    # Confirm overwrite if the file already exists
    confirm_overwrite(file_path, overwrite)

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

    return file_path


def generate_annual_calendar_svg(
    year, file_name=None, as_text=False, show_day_names=False, events_file="events.csv", emoji_file="emoji.csv", debug=False, overwrite=False
):
    """Generate an annual calendar SVG file with a 3x4 grid of monthly calendars."""
    # Ensure the output directory exists
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Default output file name for annual calendar
    if not file_name:
        file_name = f"calendar_annual_{year}.svg"

    file_path = os.path.join(output_dir, file_name)

    # Confirm overwrite if the file already exists
    confirm_overwrite(file_path, overwrite)

    # Default starting day is Sunday
    start_day = 6  # 6 corresponds to Sunday in Python's calendar module

    # SVG settings
    months_per_row = 3  # Number of months per row
    padding = 20  # Padding around the entire calendar
    horizontal_spacing = 10  # Horizontal spacing between monthly calendars

    # Calculate the maximum cell size across all months
    max_event_lines = 0
    max_event_length = 0
    all_events = {month: load_events(year, month, events_file, emoji_file, debug) for month in range(1, 13)}

    for month in range(1, 13):
        events = all_events[month]
        month_event_lines = max(len(events[day]) for day in events) if events else 0
        month_event_length = max((len(event) for day in events for event in events[day]), default=0)
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
    dwg = Drawing(file_path, size=(svg_width, svg_height))

    # Generate each month's calendar and place it in the grid
    for month in range(1, 13):
        if debug:
            print(f"Generating calendar for {year}-{month:02d}")
        x_offset = ((month - 1) % months_per_row) * (max_month_width + horizontal_spacing) + padding
        y_offset = ((month - 1) // months_per_row) * max_month_height + padding
        add_month_to_annual_calendar(
            dwg, year, month, x_offset, y_offset, max_month_width, max_month_height,
            as_text, show_day_names, max_cell_size, all_events[month]
        )

    # Save the annual calendar
    dwg.save()

    print(f"Annual SVG calendar saved as {file_path}")


def calculate_month_event_metrics(year, month):
    """Calculate the maximum number of event lines and the longest event title for a given month."""
    events = load_events(year, month)
    max_event_lines = max(len(events[day]) for day in events) if events else 0
    max_event_length = max((len(event) for day in events for event in events[day]), default=0)
    return max_event_lines, max_event_length


def add_month_to_annual_calendar(dwg, year, month, x_offset, y_offset, width, height, as_text, show_day_names, max_cell_size, events):
    """Add a single month's calendar to the annual calendar SVG."""
    # Create a calendar object
    cal = calendar.Calendar(firstweekday=6)  # Default to Sunday
    month_days = cal.monthdayscalendar(year, month)
    month_name = calendar.month_name[month]

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


def convert_text_to_paths(svg_path):
    """Convert text in the SVG to paths."""
    path_svg_path = svg_path.replace(".svg", "_paths.svg")
    cairosvg.svg2svg(url=svg_path, write_to=path_svg_path)
    print(f"Text converted to paths.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate a calendar as an SVG file.")
    parser.add_argument("--year", type=int, help="Year of the calendar (default: current year).")
    parser.add_argument("--month", type=int, help="Month of the calendar (default: current month).")
    parser.add_argument("--start-day", type=int, default=6, help="Starting day of the week (0=Monday, 6=Sunday).")
    parser.add_argument("--output", type=str, help="Output file name.")
    parser.add_argument("--as-text", action="store_false", help="Convert text to paths (default: keep text as normal text tags).")
    parser.add_argument("--show-day-names", action="store_true", help="Show day names and line below them.")
    parser.add_argument("--annual", action="store_true", help="Generate an annual calendar.")
    parser.add_argument("--events-file", type=str, default="events.csv", help="CSV file containing calendar events (default: events.csv).")
    parser.add_argument("--emoji-file", type=str, default="emoji.csv", help="CSV file containing emoji mappings for event types (default: emoji.csv).")
    parser.add_argument("--debug", action="store_true", help="Enable debug information.")
    parser.add_argument("--overwrite", action="store_true", help="Always overwrite output files without prompting.")

    args = parser.parse_args()

    if args.debug:
        print(args)

    if args.annual:
        generate_annual_calendar_svg(
            year=args.year or datetime.date.today().year,
            file_name=args.output or f"calendar_annual_{args.year or datetime.date.today().year}.svg",
            as_text=args.as_text,
            show_day_names=args.show_day_names,
            events_file=args.events_file,
            emoji_file=args.emoji_file,
            debug=args.debug,
            overwrite=args.overwrite,
        )
    else:
        generate_calendar_svg(
            year=args.year or datetime.date.today().year,
            month=args.month or datetime.date.today().month,
            start_day=args.start_day,
            file_name=args.output or f"calendar_monthly_{args.year or datetime.date.today().year}-{args.month or datetime.date.today().month:02d}.svg",
            as_text=args.as_text,
            show_day_names=args.show_day_names,
            events_file=args.events_file,
            emoji_file=args.emoji_file,
            debug=args.debug,
            overwrite=args.overwrite,
        )