import argparse
import logging
import tomllib
from pathlib import Path

from field import DielectricField
from pydantic import TypeAdapter, ValidationError

import plot

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def default_field():
    """
    Create a default example ``DielectricField``.

    This is used when no configuration file is provided via CLI.
    """
    return DielectricField(
        epsilon_r=5, r_a=13.5e-3, r_d=14.8e-3, r_b=18e-3, l=15e-2, v_0=10e3
    )


def load_field_from_toml(path: str):
    """
    Load a ``DielectricField`` configuration from a TOML file.

    This function attempts to read and validate a TOML configuration file
    containing a ``[field]`` section. The contents are validated against
    the ``DielectricField`` schema using Pydantic's ``TypeAdapter``.

    Parameters
    ----------
    path : str
        Path to the TOML configuration file.

    Returns
    -------
    DielectricField
        A validated electric field model instance.
    """

    file_path = Path(path)

    if not file_path.exists():
        logging.error("Failed to load configuration: %s", path)
        raise SystemExit(1)

    with file_path.open("rb") as f:
        data = tomllib.load(f)

    adapter = TypeAdapter(DielectricField)

    try:
        return adapter.validate_python(data["field"])
    except KeyError:
        raise ValueError("Missing [field] section in TOML configuration.")
    except ValidationError as e:
        raise ValueError(f"Invalid configuration:\n{e}") from e


def parse_args():
    """
    Parse command-line arguments for the application.

    Returns
    -------
    argparse.Namespace
        Parsed CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description="Electric field visualization for a coaxial dielectric system.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging output"
    )

    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        help="Path to TOML configuration file",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Save visualization to PNG file instead of showing it",
    )

    return parser.parse_args()


def main():
    """
    Main application entry point.
    """

    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.config and not args.config.exists():
        logging.error("Config file does not exist: %s", args.config)
        raise SystemExit(1)

    try:
        field = load_field_from_toml(args.config) if args.config else default_field()
    except Exception as e:
        logging.error(str(e))
        raise SystemExit(1)

    plt = plot.PlotBuilder(field)

    plt.enable_parallel_projection_y_up()

    plt.add_glyphs()
    plt.add_axes()
    plt.add_error_text()

    plt.auto_zoom()

    if args.output:
        plt.save_png(args.output)
        return 0

    plt.show()


if __name__ == "__main__":
    main()
