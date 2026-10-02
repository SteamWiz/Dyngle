# Dyngle

⚠️ DISCLAIMER: This is a hobby/personal project. Not a commercial product. Not for production use.

## Run lightweight local workflows

**NOTE** Usage documentation lives in the `docs/` directory of the repo, published at https://dyngle.steamwiz.io. The text below is for developers.

## Development setup

Requires Python 3.13 or higher.

Dyngle dogfoods itself. Instead of using Make, it uses Dyngle for developer controls. Use a `pipx`-installed version of Dyngle to run the commands, for isolation from work in progress. All commands assume the `pwd` is the root of the project. Shared Dyngle operations live in the `.conf` submodule ([SteamWiz/Conf](https://github.com/SteamWiz/Conf)), so clone with `--recurse-submodules` or run `git submodule update --init`.

- `dyngle run init` - Create the virtual environment and install poetry
- `dyngle run dependencies` - Install the required packages using poetry
- `dyngle run test` - Run the full unit test suite and check coverage (same as CI/CD)
- `dyngle run style` - Run style checks
- `dyngle run build` - Create a local build

GitHub Actions performs the entire build/test/release cycle using the shared [SteamWiz actions](https://github.com/SteamWiz/actions), and publishes the docs site to Cloudflare Pages on every push to `main`.

## Libraries

This application makes heavy use of [WizLib](https://wizlib.steamwiz.io/) and all code changes are expected to comply with, and take advantage of, the framework.
