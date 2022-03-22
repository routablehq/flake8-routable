# flake8-routable
Custom Flake8 plugins for Routable

## Contributing

**Please read before contributing to this repo.**

There are a lot of other Flake8 plugins already created by the Python community. Do your research and see if a plugin already exists before you build a new one.

## Rules

Here is a list of the rules supported by this Flake8 plugin:
* ROU100 - Doc string is not formatted with triple-double-quotes
* ROU101 - Import from a tests directory

## Testing

To test the efficacy of the custom Flake8 rules you are creating ensure you reinstall the package first. Run this command in this repo's base directory: `pip install -e .`.

Confirm this plugin is loaded into Flake8 via running `flake8 --version` and finding the plugin listed in the output at the bottom.

To run this plugin on your code use Flake8 as normal.

If you'd like to run the unit tests included in this package enter the `tests/` folder and run `pytest`. Make sure `pytest` is installed as well.
