# TV XML EPG

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]


_Integration to add [TV XML][tvxml_wiki] EPG to Home Assistant._

## HACS (recommended)

1. Add `https://github.com/shadow578/homeassistant_tvxml-epg` as a custom repository, choose `Integration` as Category and add.
2. In the HACS UI, search for `TVXML EPG` and install it.
3. Restart Home Assistant
4. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "TVXML EPG"

## Manual

1. Using the tool of choice open the directory for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory there, you need to create it.
2. In the `custom_components` directory create a new folder called `tvxml_epg`.
3. Download _all_ the files from the `custom_components/tvxml_epg/` directory in this repository.
4. Place the files you downloaded in the new directory you created.
5. Restart Home Assistant
6. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "TVXML EPG"

## Configuration

Configuration is done using the UI.


You'll be prompted to enter a URL as a TXML data source.
After the initial setup, you'll can configure the update interval in the integration options.

Additionally, consider disabling all channels you don't need and disable the "enable newly added entities" option in system settings.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[tvxml_wiki]: https://wiki.xmltv.org/index.php/XMLTVFormat
[commits-shield]: https://img.shields.io/github/commit-activity/y/shadow578/homeassistant_tvxml-epg.svg?style=for-the-badge
[commits]: https://github.com/shadow578/homeassistant_tvxml-epg/commits/main
[license-shield]: https://img.shields.io/github/license/shadow578/homeassistant_tvxml-epg.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40shadow578-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/shadow578/homeassistant_tvxml-epg.svg?style=for-the-badge
[releases]: https://github.com/shadow578/homeassistant_tvxml-epg/releases
