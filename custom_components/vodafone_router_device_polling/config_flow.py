import voluptuous as vol
import logging
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, ENTRY_DATA_HOST, OPTION_PASSWORD, OPTION_USERNAME
from .vodafone_box import VodafoneBox

_LOGGER = logging.getLogger(__name__)

class VodafoneConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vodafone Station."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        _LOGGER.debug("Starting config flow step: user")
        errors = {}

        if user_input is not None:
            _LOGGER.info("Processing user input for Vodafone Station configuration")
            host = user_input[ENTRY_DATA_HOST]
            username = user_input[OPTION_USERNAME]
            password = user_input[OPTION_PASSWORD]
            
            _LOGGER.debug("Testing connection to Vodafone Station at %s with username %s", host, username)

            box = VodafoneBox(host)
            try:
                await self.hass.async_add_executor_job(box.login, username, password)
                _LOGGER.info("Connection test successful for %s", host)
            except Exception as e:
                _LOGGER.error("Connection test failed for %s: %s", host, e, exc_info=True)
                errors["base"] = "cannot_connect"
            else:
                _LOGGER.info("Creating config entry for Vodafone Station at %s", host)
                return self.async_create_entry(
                    title=f"Vodafone Station ({host})",
                    data={ENTRY_DATA_HOST: host},  # non-sensitive
                    options={
                        OPTION_USERNAME: username,
                        OPTION_PASSWORD: password
                    }
                )

        schema = vol.Schema({
            vol.Required(ENTRY_DATA_HOST): str,
            vol.Required(OPTION_USERNAME): str,
            vol.Required(OPTION_PASSWORD): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reauth(self, user_input=None):
        """Handle re-authentication when login fails."""
        return await self.async_step_user(user_input)
