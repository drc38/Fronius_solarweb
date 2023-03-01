# Fronius Solar.Web Home Assistant integration

![coverage badge](./coverage.svg)
[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![hacs_downloads](https://img.shields.io/github/downloads/drc38/Fronius_solarweb/latest/total)](https://github.com/drc38/Fronius_solarweb/releases/latest)

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

Standalone Home Assistant integration using the Fronius Solar.web API. It is intended if your Fronius is on a different network to HA, otherwise you are best to use the built-in integration which will have more sensors and a faster refresh rate.

# Installation

## HACS

HACS is recommended as it provides automated install and will notify you when updates are available.

This assumes you have [HACS](https://github.com/hacs/integration) installed and know how to use it. If you need help with this, go to the HACS project documentation.

Add custom repository in _HACS_

1. Click on HACS in your menu to open the HACS panel, then click on integrations (https://your.domain/hacs/integrations).
1. Click on the 3 dots in the top right corner.
1. Select "Custom repositories"
1. Add the URL to the repository: `https://github.com/drc38/Fronius_solarweb`
1. Select the integration category.
1. Click the "ADD" button.

Once done, you should see the new repository, appearing in a list like this. Click the **Download** button

## Manual Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `solarweb`.
4. Download _all_ the files from the `custom_components/solarweb/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Integrations" click "+" and search for "solarweb"

# Configuration

Configuration of the integration is done within the Integrations Panel in Home Assistant.

1. Navigate to Integrations
1. Click _Add Integration_
1. Search for Fronius Solar.Web
1. Enter your PV System ID and API details from your [Solar.Web](https://www.solarweb.com/) account

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Credits

This project was generated from [@oncleben31](https://github.com/oncleben31)'s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template.

Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template

---

[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/drc38/Fronius_solarweb.svg
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40drc38-blue.svg
[releases-shield]: https://img.shields.io/github/release/drc38/Fronius_solarweb.svg
[releases]: https://github.com/drc38/Fronius_solarweb/releases
[user_profile]: https://github.com/drc38
