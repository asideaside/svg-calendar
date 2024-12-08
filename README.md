
# Calendar SVG Generator

Generates a monthly calendar as an SVG. You can specify the year, month, and starting day of the week. By default, text in the SVG is converted to paths for better compatibility, but you can retain normal text using a flag.

## Features

- Generates clean and visually customizable calendar SVGs.
- Default behavior converts text to paths for compatibility.
- Specify:
  - **Year**: Defaults to the current year if not provided.
  - **Month**: Defaults to the current month if not provided.
  - **Starting Day of the Week**: Choose any day as the first column (e.g., Monday, Sunday).
- Option to retain normal text tags in the SVG.

## Requirements

- Tested on Python 3.12
- Installed dependencies:
  - `svgwrite`
  - `cairosvg`

## Installation

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd calendar_svg_generator
   ```

2. Install dependencies using `uv`:

   ```bash
   uv add svgwrite cairosvg
   ```

## Usage

Run the script with the following options:

```bash
uv run src/calendar_svg.py [OPTIONS]
```

### Options

| Option        | Description                                   | Default        |
| ------------- | --------------------------------------------- | -------------- |
| `--year`      | Year for the calendar                         | Current year   |
| `--month`     | Month for the calendar                        | Current month  |
| `--start-day` | Starting day of the week (0=Monday, 6=Sunday) | 0 (Monday)     |
| `--output`    | Output file name                              | `calendar.svg` |
| `--as-text`   | Keep text as normal text tags (default is to convert to paths). | Off |

### Example Commands

1. Generate a calendar for December 2024, starting on Monday (default behavior, text converted to paths):

   ```bash
   uv run src/calendar_svg.py --year 2024 --month 12 --output december_calendar.svg
   ```

2. Generate a calendar with normal text (not converted to paths):

   ```bash
   uv run src/calendar_svg.py --year 2024 --month 12 --output december_calendar.svg --as-text
   ```

## Project Structure

```
calendar_svg_generator/
├── src/
│   └── calendar_svg.py    # Main script
├── README.md              # Documentation
├── uv.lock                # Dependency lock file
└── pyproject.toml         # Project configuration
```

## Contributing

Feel free to submit issues, fork the repository, and make pull requests. Contributions are welcome!

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
