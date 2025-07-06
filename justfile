# Install dependencies
install:
    uv sync --dev

# Run tests
test:
    uv run pytest tests/ -v

# Run tests quietly
test-q:
    uv run pytest -q

# Format code
fmt:
    uvx ruff format .

# Lint code
lint:
    uvx ruff check .

# Fix linting issues
lint-fix:
    uvx ruff check . --fix

# Run both linting and tests
check: lint test

# Clean build artifacts
clean:
    rm -rf dist/
    rm -rf build/
    rm -rf *.egg-info/

# Build the project
build:
    uv build

# Run the CLI tool
run *args:
    uv run youmirror {{args}}

# Install the project in development mode
dev:
    uv sync --dev

# Show project tree
tree:
    uv tree
