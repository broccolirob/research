"""Command line entry point for the project."""

from research import get_greeting


def main() -> None:
    """Run the application."""
    print(get_greeting())


if __name__ == "__main__":
    main()
