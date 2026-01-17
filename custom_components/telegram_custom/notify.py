import logging
import voluptuous as vol

from homeassistant.components.notify import (
    ATTR_DATA,
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

    # --------------------------------------------------------------------------
    # HELPER METHODS
    # --------------------------------------------------------------------------

    @staticmethod
    def _extract_url(item):
        """Estrae l'url da dizionari, liste o stringhe."""
        if isinstance(item, list) and item:
            if isinstance(item[0], dict):
                return item[0].get("url")
            if isinstance(item[0], str):
                return item[0]
        if isinstance(item, dict):
            return item.get("url")
        if isinstance(item, str):
            return item
        return None

    @staticmethod
    def _detect_media(data: dict):
        """Capisce automaticamente che tipo di media stai inviando."""
        media_map = {
            "photo": "send_photo",
            "video": "send_video",
            "document": "send_document",
            "animation": "send_animation",
            "audio": "send_audio",
            "media_group": "send_media_group",
        }
        for key, service in media_map.items():
            if key in data:
                return key, service
        return None, "send_message"

    def detect_format(self, text: str):
        """Capisce se stai usando HTML o Markdown automaticamente."""
        if not isinstance(text, str):
            return "Markdown"
        if "<b>" in text or "<i>" in text or "<u>" in text or "<a " in text:
            return "HTML"
        return "Markdown"

    def escape_md2(self, text: str):
        """Pulisce il testo per evitare errori con MarkdownV2."""
        if not isinstance(text, str):
            return text
        escape_chars = r"_*[]()~`>#+-=|{}.!\\"
        for c in escape_chars:
            text = text.replace(c, "\\" + c)
        return text.replace("\n", "\\n")

    @staticmethod
    def md_to_html(text: str):
        """Converte Markdown base in testo pulito per HTML."""
        if not isinstance(text, str):
            return text
        text = text.replace("*", "").replace("_", "").replace("`", "")
        return text

    @staticmethod
    def split_message(text: str, max_len: int = 4000):
        """Divide i messaggi troppo lunghi."""
        if not text:
            return [""]
        return [text[i:i + max_len] for i in range(0, len(text), max_len)]

    # --------------------------------------------------------------------------
    # GESTIONE ERRORI E FALLBACK
    # --------------------------------------------------------------------------

    async def send_as_document(self, text: str, caption: str = ""):
        """Salvataggio: se tutto fallisce, invia un file di testo."""
        try:
            await self._hass.services.async_call(
                "telegram_bot",
                "send_document",
                {
                    "target": self._chat_id,
                    "caption": caption,
                    "filename": "messaggio_errore.txt",
                    "document": text,
                },
                blocking=False,
            )
        except Exception as e:
            _LOGGER.error("TelegramCustom: Errore nel fallback documento: %s", e)
            await self._send_fallback_text(text)

    async def _send_fallback_text(self, message):
        """Ultima spiaggia: invio testo semplice."""
        await self._hass.services.async_call(
            "telegram_bot",
            "send_message",
            {"target": self._chat_id, "message": message},
            blocking=False,
        )

    # --------------------------------------------------------------------------
    # LOGICA PRINCIPALE DI INVIO (Async)
    # --------------------------------------------------------------------------

    async def async_send_message(self, message="", **kwargs):
        """Funzione principale di invio aggiornata e potenziata."""
        data = kwargs.get(ATTR_DATA) or {}
        title = kwargs.get(ATTR_TITLE)

        # 1. Rilevamento Formattazione (HTML/Markdown)
        if "parse_mode" in data:
            parse_mode = str(data["parse_mode"])
            # Normalizzazione input utente
            if parse_mode.lower() == "html": parse_mode = "HTML"
            elif parse_mode.lower() in ["markdown", "md"]: parse_mode = "Markdown"
            elif parse_mode.lower() in ["markdownv2", "md2"]: parse_mode = "MarkdownV2"
        else:
            parse_mode = self.detect_format(message or title or "")

        # 2. Formattazione del Titolo
        title_formatted = ""
        if title:
            if parse_mode == "Markdown":
                title_formatted = f"*{title}*"
            elif parse_mode == "HTML":
                title_formatted = f"<b>{self.md_to_html(title)}</b>"
            elif parse_mode == "MarkdownV2":
                title_formatted = f"*{self.escape_md2(title)}*"

        # 3. Preparazione dati base
        service_data = {
            "target": self._chat_id,
            "parse_mode": parse_mode,
        }

        # 4. Controllo Media (Foto, Video, Gruppi, ecc)
        media_key, service_to_call = self._detect_media(data)

        # CASO A: Gruppo di Media (Album)
        if media_key == "media_group":
            items = data.get("media_group", [])
            media_payload = []
            for item in items:
                url = self._extract_url(item)
                if url:
                    media_type = item.get("type", "photo")
                    caption = item.get("caption", message)
                    # Applica titolo alla prima caption se necessario
                    if len(media_payload) == 0 and title_formatted:
                         caption = f"{title_formatted}\n{caption}"

                    media_payload.append({
                        "type": media_type,
                        "media": url,
                        "caption": caption if media_type == "photo" else None
                    })
            service_data["media"] = media_payload

        # CASO B: Media Singolo (Foto/Video/Doc)
        elif media_key:
            item = data.get(media_key)
            url = self._extract_url(item)

            if url:
                # Gestione caption
                caption_raw = message
                if isinstance(item, dict): caption_raw = item.get("caption", message)
                elif isinstance(item, list) and isinstance(item[0], dict): caption_raw = item[0].get("caption", message)

                # Unione Titolo + Caption
                if parse_mode == "MarkdownV2":
                     caption = f"{title_formatted}\n{self.escape_md2(caption_raw)}" if title_formatted else self.escape_md2(caption_raw)
                else:
                     caption = f"{title_formatted}\n{caption_raw}" if title_formatted else caption_raw

                service_data["url"] = url
                service_data["caption"] = caption
                # Rimuovi 'message' standard perché usiamo 'caption'
                service_data.pop("message", None)
            else:
                # Se l'url non è valido, torna a messaggio di testo
                return await self._send_fallback_text(message)

        # CASO C: Solo Testo
        else:
            final_msg = message
            if parse_mode == "MarkdownV2":
                final_msg = self.escape_md2(message)

            if title_formatted:
                final_msg = f"{title_formatted}\n{final_msg}"

            # Controllo lunghezza massima
            if len(final_msg) > 4000:
                chunks = self.split_message(final_msg)
                for part in chunks:
                    try:
                        await self._hass.services.async_call(
                            "telegram_bot", "send_message",
                            {"target": self._chat_id, "message": part, "parse_mode": parse_mode},
                            blocking=False
                        )
                    except Exception:
                        await self.send_as_document(final_msg, caption="Messaggio troppo lungo")
                return

            service_data["message"] = final_msg

        # 5. Aggiunta parametri extra (Tastiere, Notifiche silenziose, ecc)
        for key, value in data.items():
            if key not in ["photo", "video", "document", "animation", "audio", "media_group", "parse_mode"]:
                service_data[key] = value

        # Gestione speciale per le tastiere (inline o normali)
        if "inline_keyboard" in data:
            service_data["inline_keyboard"] = data["inline_keyboard"]

        # 6. Esecuzione Chiamata al servizio
        try:
            await self._hass.services.async_call(
                "telegram_bot",
                service_to_call,
                service_data,
                blocking=False,
            )
        except Exception as e:
            _LOGGER.error("TelegramCustom: Errore invio %s: %s", service_to_call, e)
            # Fallback intelligente
            msg_content = service_data.get("message") or service_data.get("caption") or message
            await self.send_as_document(msg_content, caption=f"Errore invio: {title or 'Notifica'}")
