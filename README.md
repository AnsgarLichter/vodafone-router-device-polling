# ha-vodafone-router

This custom integration connects Home Assistant to a Vodafone Station router.
Currently, the only functionality is to expose connected devices as device trackers or binary sensors.
If you want to use another feature from the router's functionalities, feel free to open an issue or submit a PR yourself!

## Features

- Secure login using the router’s native crypto
- Polls router every 30 seconds (configurable)
- Exposes connected devices as binary sensors or device trackers (configurable)
- Local-only

## Installation (HACS)

1. Install `HACS`: [Download HACS](https://www.hacs.xyz/docs/use/)
2. [![Open your Home Assistant instance and add the repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository?owner=ansgarlichter&repository=ha_vodafone_router&category=integration)
3. Press the `Add` button
4. [![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ha_vodafone_router)
5. Configure the connection to your router
    - Router IP address
    - Username
    - Password
    - Scan interval (optional)
    - MAC addresses (optional - if omitted all connected devices will be created as an entity)
6. Go to `Settings -> Devices & Services --> Entities` and see the added entities and their status

## Notes

- Tested on Vodafone Router with firmware AR01.05.063.15_082825_735.SIP.20.VF
