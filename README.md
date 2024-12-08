# Calendar SVG Generator

Generates monthly a specified calendar month as an SVG. You can specify the year, month, and starting day of the week, and customize options such as font styles, sizes, and text weights.

## Features

- Generate clean and visually customizable calendar SVGs.
- Specify:
  - **Year**: Defaults to the current year if not provided.
  - **Month**: Defaults to the current month if not provided.
  - **Starting Day of the Week**: Choose any day as the first column (e.g., Monday, Sunday).

## Requirements

- Tested on Python 3.12
- Installed dependencies:
  - `svgwrite`

## Installation

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd calendar_svg_generator
   ```

2. Install dependencies using `uv`:

   ```bash
   uv add svgwrite
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
| `--use-paths` | Convert text to curves (paths)                | Off            |

### Example Commands

1. Generate a calendar for December 2024, starting on Monday:

   ```bash
   uv run src/calendar_svg.py --year 2024 --month 12 --start-day 0 --output december_calendar.svg
   ```

2. Generate a calendar with text converted to curves:

   ```bash
   uv run src/calendar_svg.py --use-paths
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
