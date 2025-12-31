# Explain My Config

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![CLI](https://img.shields.io/badge/type-CLI-orange.svg)

[![Config](https://img.shields.io/badge/-config-lightgrey.svg)](.)
[![ENV](https://img.shields.io/badge/-.env-yellow.svg)](.)
[![JSON](https://img.shields.io/badge/-JSON-green.svg)](.)
[![YAML](https://img.shields.io/badge/-YAML-red.svg)](.)
[![Beginner Friendly](https://img.shields.io/badge/-beginner--friendly-brightgreen.svg)](.)
[![Developer Tools](https://img.shields.io/badge/-developer--tools-blueviolet.svg)](.)


A simple CLI tool that reads configuration files (`.env`, `.json`, `.yaml`) and outputs plain-English explanations of each key/value pair for beginners.

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/explain-my-config.git
cd explain-my-config

# Install the package
pip install -e .
```

## Usage

```bash
# Explain a .env file
explain-my-config ./config.env

# Explain a JSON file
explain-my-config ./config.json

# Explain a YAML file
explain-my-config ./config.yaml
```

## Example

Given a `.env` file:

```env
DB_POOL_SIZE=10
DEBUG=false
PORT=8080
```

The output will be:

```
DB_POOL_SIZE = 10
-> Controls how many database connections can exist at the same time.

DEBUG = false
-> Enables or disables debug mode for development.

PORT = 8080
-> The network port the application listens on.
```

## Supported File Types

- `.env` - Environment variable files (KEY=VALUE format)
- `.json` - JSON configuration files
- `.yaml` / `.yml` - YAML configuration files

## Features

- Built-in dictionary of common configuration keys with explanations
- Smart fallback explanations for unknown keys based on:
  - Key name analysis (splits by underscore)
  - Value type detection (URL, number, boolean, path)
- Handles nested JSON/YAML structures with dot notation
- Gracefully handles comments, empty lines, and quoted values
- Clean, readable output

## Project Structure

```
explain-my-config/
├── explain_my_config/
│   ├── __init__.py      # Package initialization
│   ├── cli.py           # CLI entry point
│   ├── parser.py        # File parsing logic
│   ├── explainer.py     # Explanation generation
│   └── utils.py         # Helper functions
├── tests/               # Sample test files
├── README.md
├── LICENSE
└── pyproject.toml
```

## Development

```bash
# Install in development mode
pip install -e .

# Run directly with Python
python -m explain_my_config.cli ./config.env
```

## Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.
