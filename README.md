# Weather Service

A simple weather service built with FastAPI.

## Setting up development environment

This project uses [Rye](https://rye.astral.sh/) as the package manager, which needs to be installed on your development workstation. For Debian-like environments, you can install Rye using:

```bash
curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION="--yes" bash
```

After installation, initialize the project dependencies:

```bash
rye sync
```

## Useful commands

### Code quality checks
Run all linting tools (black, mypy, ruff, typos):
```bash
rye run all-checks
```

### Development server
Run the local development server:
```bash
fastapi run src/weather_service/main.py --app app --reload
```

### Additional commands
Install dependencies:
```bash
rye sync
```

Run tests:
```bash
rye run test
```

Build the project:
```bash
rye build
```

## Project structure

```
weather-service/
├── src/
│   └── weather_service/
│       └── main.py
├── pyproject.toml
└── README.md
```





