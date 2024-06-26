# flake8-routable
Custom Flake8 plugins for Routable

## Contributing

### Please Read

There are a lot of other Flake8 plugins already created by the Python community. Do your research and see if a plugin already exists before you build a new one.

The Python environment used is `3.8.10`.

### First Time Setup

Before committing code for the first time run:
1. `pip install -r requirements-dev.txt` and
2. `pre-commit install`

## Rules

Here is a list of the rules supported by this Flake8 plugin:
* `ROU100` - Triple double quotes not used for docstring
* `ROU101` - Import from a tests directory
* `ROU102` - Strings should not span multiple lines except comments or docstrings
* `ROU103` - Object does not have attributes in order
* `ROU104` - Multiple blank lines are not allowed after a non-section comment
* `ROU105` - Constants are not in order
* `ROU106` - Relative imports are not allowed
* `ROU107` - Inline function import is not at top of statement
* `ROU108` - Import from model module instead of sub-packages
* `ROU109` - Disallow rename migrations
* `ROU110` - Disallow .save() with no update_fields
* `ROU111` - Disallow FeatureFlag creation in code
* `ROU112` - Tasks mush have *args, **kwargs
* `ROU113` - Tasks can not have priority in the signature

## Testing

To test the efficacy of the custom Flake8 rules you are creating ensure you reinstall the package first. Run this command in this repo's base directory: `pip install -e .`.

Confirm this plugin is loaded into Flake8 via running `flake8 --version` and finding the plugin listed in the output at the bottom.

To run this plugin on your code use Flake8 as normal.

If you'd like to run the unit tests included in this package enter the `tests/` folder and run `pytest`. Make sure `pytest` is installed as well.
