import logging
import voluptuous as vol
import os

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
    return TelegramCustomService(hass, config[CONF_CHAT_ID])


class TelegramCustomService(BaseNotificationService):
    def __init__(self, hass, chat_id: int):
        self._hass = hass
        self._chat_id = chat_id

    # -------------------------
    # Helper: estrazione URL o FILE path
    # -------------------------
    @staticmethod
    def _extract_url(item):
        """Estrae 'url' o 'file' dai dati."""
        val = None
        if isinstance(item, list) and item:
            if isinstance(item[0], dict):
                val = item[0].get("url") or item[0].get("file")
            elif isinstance(item[0], str):
                val = item[0]
        elif isinstance(item, dict):
            val = item.get("url") or item.get("file")
        elif isinstance(item, str):
            val = item
        return val

    # -------------------------
    # Helper: identifica il tipo di media
    # -------------------------
    @staticmethod
    def _detect_media_type(data: dict):
        """Ritorna il tipo di media e il servizio standard da chiamare."""
        if "photo" in data: return "photo", "send_photo"
        if "video" in data: return "video", "send_video"
        if "document" in data: return "document", "send_document"
        if "audio" in data: return "audio", "send_audio"
        if "animation" in data: return "animation", "send_animation"
        return None, "send_message"

    # -------------------------
    # AUTO-DETECT FORMATTAZIONE
    # -------------------------
    def detect_format(self, text: str):
        if not isinstance(text, str): return "Markdown"
        if "<b>" in text or "<i>" in text or "<u>" in text or "<a " in text:
            return "HTML"
        return "Markdown"

    # -------------------------
    # Escape MarkdownV2
    # -------------------------
    def escape_md2(self, text: str):
        if not isinstance(text, str): return text
        escape_chars = r"_*[]()~`>#+-=|{}.!\\"
        for c in escape_chars:
            text = text.replace(c, "\\" + c)
        return text.replace("\n", "\\n")

    @staticmethod
    def md_to_html(text: str):
        if not isinstance(text, str): return text
        return text.replace("*", "").replace("_", "").replace("`", "")

    @staticmethod
    def split_message(text: str, max_len: int = 4000):
        if not text: return [""]
        return [text[i:i + max_len] for i in range(0, len(text), max_len)]

    # -------------------------
    # FALLBACK Semplificato
    # -------------------------
    async def _send_fallback_text(self, message):
        """Invia un semplice messaggio di testo se il resto fallisce."""
        try:
            await self._hass.services.async_call(
                "telegram_bot",
                "send_message",
                {
                    "target": self._chat_id,
                    "message": f"⚠️ Errore invio media. Messaggio originale:\n{message}",
                },
                blocking=False,
            )
        except Exception as e:
            _LOGGER.error("TelegramCustom: Fallback fallito: %s", e)

    # -------------------------
    # Metodo principale
    # -------------------------
    async def async_send_message(self, message="", **kwargs):
        data = kwargs.get(ATTR_DATA) or {}
        title = kwargs.get(ATTR_TITLE)

        # 1. Rileva Parse Mode
        if "parse_mode" in data:
            parse_mode = str(data["parse_mode"]).lower()
            if parse_mode == "html": parse_mode = "HTML"
            elif parse_mode in ["markdown", "md"]: parse_mode = "Markdown"
            elif parse_mode in ["markdownv2", "md2"]: parse_mode = "MarkdownV2"
            else: parse_mode = "Markdown"
        else:
            parse_mode = self.detect_format(message or title or "")

        # 2. Formatta Titolo
        title_fmt = ""
        if title:
            if parse_mode == "Markdown": title_fmt = f"*{title}*"
            elif parse_mode == "HTML": title_fmt = f"<b>{self.md_to_html(title)}</b>"
            elif parse_mode == "MarkdownV2": title_fmt = f"*{self.escape_md2(title)}*"

        # -----------------------------------------------------------
        # GESTIONE MEDIA GROUP (ALBUM) - FIX SEQUENZIALE
        # -----------------------------------------------------------
        # Home Assistant non supporta nativamente send_media_group.
        # Iteriamo e inviamo i file uno alla volta.
        if "media_group" in data:
            items = data.get("media_group", [])
            for i, item in enumerate(items):
                try:
                    # Estrai URL o File
                    url_or_file = self._extract_url(item)
                    if not url_or_file: continue

                    # Tipo (photo o video)
                    m_type = item.get("type", "photo")
                    service_call = "send_video" if m_type == "video" else "send_photo"

                    # Caption: mettiamo il titolo/messaggio solo sulla prima foto
                    caption_raw = item.get("caption", "")
                    if i == 0 and message:
                         caption_raw = f"{message}\n{caption_raw}"

                    # Formattazione Caption
                    if parse_mode == "Markdown" and i == 0 and title_fmt:
                        caption = f"{title_fmt}\n{caption_raw}"
                    elif parse_mode == "HTML" and i == 0 and title_fmt:
                        caption = f"{title_fmt}\n{caption_raw}"
                    elif parse_mode == "MarkdownV2":
                        caption = self.escape_md2(caption_raw)
                        if i == 0 and title_fmt:
                             caption = f"{title_fmt}\n{caption}"
                    else:
                        caption = f"{title_fmt}\n{caption_raw}" if (i==0 and title_fmt) else caption_raw

                    # Payload singolo
                    payload = {
                        "target": self._chat_id,
                        "caption": caption,
                        "parse_mode": parse_mode
                    }

                    # Controllo Locale vs URL
                    is_local = str(url_or_file).strip().startswith(("/", "./", "file://"))
                    if is_local:
                        payload["file"] = url_or_file
                    else:
                        payload["url"] = url_or_file

                    # Invio Singolo
                    await self._hass.services.async_call(
                        "telegram_bot",
                        service_call,
                        payload,
                        blocking=False,
                    )
                except Exception as e:
                    _LOGGER.error("TelegramCustom: Errore invio elemento gruppo %s: %s", i, e)

            # Fine elaborazione gruppo
            return

        # -----------------------------------------------------------
        # GESTIONE MEDIA SINGOLO / TESTO
        # -----------------------------------------------------------
        media_key, service_to_call = self._detect_media_type(data)

        service_data = {
            "target": self._chat_id,
            "parse_mode": parse_mode,
        }

        # CASO MEDIA SINGOLO
        if media_key:
            item = data.get(media_key)
            url_or_file = self._extract_url(item)

            if not url_or_file:
                # Fallback a solo testo
                return await self._send_fallback_text(message)

            # Gestione Caption
            caption_raw = message
            if isinstance(item, dict): caption_raw = item.get("caption", message)
            elif isinstance(item, list) and isinstance(item[0], dict): caption_raw = item[0].get("caption", message)

            if parse_mode == "Markdown" and title_fmt: caption = f"{title_fmt}\n{caption_raw}"
            elif parse_mode == "HTML" and title_fmt: caption = f"{title_fmt}\n{caption_raw}"
            elif parse_mode == "MarkdownV2":
                 safe_cap = self.escape_md2(caption_raw)
                 caption = f"{title_fmt}\n{safe_cap}" if title_fmt else safe_cap
            else: caption = f"{title_fmt}\n{caption_raw}" if title_fmt else caption_raw

            is_local = str(url_or_file).strip().startswith(("/", "./", "file://"))
            if is_local: service_data["file"] = url_or_file
            else: service_data["url"] = url_or_file

            service_data["caption"] = caption
            # Rimuovi parametri non necessari
            service_data.pop("message", None)

        # CASO SOLO TESTO
        else:
            final_msg = message
            if parse_mode == "MarkdownV2": final_msg = self.escape_md2(message)
            if title_fmt: final_msg = f"{title_fmt}\n{final_msg}"

            if len(final_msg) > 4000:
                chunks = self.split_message(final_msg)
                for part in chunks:
                    await self._hass.services.async_call("telegram_bot", "send_message",
                        {"target": self._chat_id, "message": part, "parse_mode": parse_mode}, blocking=False)
                return

            service_data["message"] = final_msg

        # Parametri extra (Tastiere, etc)
        for key, value in data.items():
            if key not in ["photo", "video", "document", "animation", "audio", "media_group", "parse_mode"]:
                service_data[key] = value

        # Gestione Keyboard
        if "inline_keyboard" in data: service_data["inline_keyboard"] = data["inline_keyboard"]
        reply_markup = data.get("reply_markup")
        if reply_markup:
            if "inline_keyboard" in reply_markup: service_data["inline_keyboard"] = reply_markup["inline_keyboard"]
            if "keyboard" in reply_markup:
                service_data["keyboard"] = reply_markup["keyboard"]
                service_data["resize_keyboard"] = reply_markup.get("resize_keyboard", True)
                service_data["one_time_keyboard"] = reply_markup.get("one_time_keyboard", False)

        # Esecuzione
        try:
            await self._hass.services.async_call(
                "telegram_bot",
                service_to_call,
                service_data,
                blocking=False,
            )
        except Exception as e:
            _LOGGER.error("TelegramCustom: Errore invio %s: %s", service_to_call, e)
            await self._send_fallback_text(message)
