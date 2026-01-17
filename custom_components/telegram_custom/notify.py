import logging
import voluptuous as vol
from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_MESSAGE,
    ATTR_TITLE,
    BaseNotificationService,
    PLATFORM_SCHEMA,
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_CHAT_ID = "chat_id"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_CHAT_ID): cv.positive_int,
})

def get_service(hass, config, discovery_info=None):
    chat_id = config.get(CONF_CHAT_ID)
    return TelegramCustomService(hass, chat_id)

class TelegramCustomService(BaseNotificationService):
    def __init__(self, hass, chat_id):
        self._hass = hass
        self._chat_id = chat_id

    def send_message(self, message="", **kwargs):
        data = kwargs.get(ATTR_DATA) or {}
        title = kwargs.get(ATTR_TITLE)

        # Prepara il payload base
        service_data = {"target": self._chat_id}

        # Se c'è un titolo, lo aggiungiamo al messaggio
        if title:
            message = f"*{title}*\n{message}"

        service_data["message"] = message

        # Gestione avanzata (Foto, Video, ecc)
        # Se nel data c'è "photo", "video" o "document", cambiamo servizio
        service_to_call = "send_message"

        if data:
            if "photo" in data:
                service_to_call = "send_photo"
                service_data["url"] = data["photo"][0].get("url") if isinstance(data["photo"], list) else data.get("photo")
                service_data["caption"] = message
                del service_data["message"] # send_photo usa caption, non message
            elif "video" in data:
                service_to_call = "send_video"
                service_data["url"] = data["video"][0].get("url") if isinstance(data["video"], list) else data.get("video")
                service_data["caption"] = message
                del service_data["message"]
            # Aggiungi qui altre logiche se usi tastiere o altro,
            # ma per testo e media base questo basta.

            # Passa il resto dei dati (es. tastiere inline)
            for key, value in data.items():
                if key not in ["photo", "video"]:
                    service_data[key] = value

        # Chiama il servizio ufficiale telegram_bot
        self._hass.services.call("telegram_bot", service_to_call, service_data)
