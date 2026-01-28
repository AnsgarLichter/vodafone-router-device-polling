# Vodafone Station – Home Assistant Integration

This custom integration connects Home Assistant to a Vodafone Station router
and exposes device connectivity information.

## Features

- Secure login using the router’s native crypto
- Polls router every 30 seconds
- Binary sensor for device connectivity
- Local-only (no cloud)

## Installation (HACS)

1. Go to **HACS → Integrations**
2. Open the menu (⋮) → **Custom repositories**
3. Add this repository:
   - Type: Integration
4. Install **Vodafone Station**
5. Restart Home Assistant

## Configuration

- Go to **Settings → Devices & Services**
- Add **Vodafone Station**
- Enter:
  - Router IP
  - Username
  - Password

## Notes

- Password is never logged
- Tested on Vodafone Station firmware XXXX