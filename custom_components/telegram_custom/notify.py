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
        if "animation" in data: return "animation", "send_animation"
        if "location" in data: return "location", "send_location"
        if "audio" in data: return "audio", "send_voice"
        if "voice" in data: return "voice", "send_voice"
        return None, "send_message"

    # -------------------------
    # AUTO-DETECT FORMATTAZIONE
    # -------------------------
    def detect_format(self, text: str):
        if not isinstance(text, str): return "markdown"
        text_lower = text.lower()
        if any(tag in text_lower for tag in ["<b>", "<i>", "<u>", "<a "]):
            return "html"
        return "markdown"

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
            raw_mode = str(data["parse_mode"]).lower()
            if raw_mode == "html": parse_mode = "html"
            elif raw_mode in ["markdown", "md"]: parse_mode = "markdown"
            elif raw_mode in ["markdownv2", "md2"]: parse_mode = "markdownv2"
            else: parse_mode = "markdown"
        else:
            parse_mode = self.detect_format(message or title or "")

        # 2. Formatta Titolo
        title_fmt = ""
        if title:
            if parse_mode == "markdown": title_fmt = f"*{title}*"
            elif parse_mode == "html": title_fmt = f"<b>{self.md_to_html(title)}</b>"
            elif parse_mode == "markdownv2": title_fmt = f"*{self.escape_md2(title)}*"

        # -----------------------------------------------------------
        # GESTIONE MEDIA GROUP
        # -----------------------------------------------------------
        if "media_group" in data:
            items = data.get("media_group", [])
            for i, item in enumerate(items):
                try:
                    url_or_file = self._extract_url(item)
                    if not url_or_file: continue

                    m_type = item.get("type", "photo")
                    if m_type == "video": service_call = "send_video"
                    elif m_type == "audio": service_call = "send_voice"
                    else: service_call = "send_photo"

                    caption_raw = item.get("caption", "")
                    if i == 0 and message: caption_raw = f"{message}\n{caption_raw}"

                    if parse_mode == "markdown" and i == 0 and title_fmt: caption = f"{title_fmt}\n{caption_raw}"
                    elif parse_mode == "html" and i == 0 and title_fmt: caption = f"{title_fmt}\n{caption_raw}"
                    elif parse_mode == "markdownv2":
                        caption = self.escape_md2(caption_raw)
                        if i == 0 and title_fmt: caption = f"{title_fmt}\n{caption}"
                    else: caption = f"{title_fmt}\n{caption_raw}" if (i==0 and title_fmt) else caption_raw

                    payload = {"target": self._chat_id, "caption": caption, "parse_mode": parse_mode}
                    is_local = str(url_or_file).strip().startswith(("/", "./", "file://"))
                    if is_local: payload["file"] = url_or_file
                    else: payload["url"] = url_or_file

                    await self._hass.services.async_call("telegram_bot", service_call, payload, blocking=False)
                except Exception as e:
                    _LOGGER.error("TelegramCustom: Errore gruppo %s: %s", i, e)
            return

        # -----------------------------------------------------------
        # GESTIONE MEDIA SINGOLO / LOCATION / TESTO
        # -----------------------------------------------------------
        media_key, service_to_call = self._detect_media_type(data)
        service_data = {"target": self._chat_id, "parse_mode": parse_mode}

        if media_key == "location":
            item = data.get("location")
            if isinstance(item, list): item = item[0]
            service_data["latitude"] = item.get("latitude")
            service_data["longitude"] = item.get("longitude")
            
            # Gestione tastiere per location
            reply_markup = data.get("reply_markup")
            if reply_markup:
                if "inline_keyboard" in reply_markup: service_data["inline_keyboard"] = reply_markup["inline_keyboard"]
                if "keyboard" in reply_markup: service_data["keyboard"] = reply_markup["keyboard"]
            elif "inline_keyboard" in data: 
                service_data["inline_keyboard"] = data["inline_keyboard"]

            service_data.pop("parse_mode", None)
            try:
                await self._hass.services.async_call("telegram_bot", "send_location", service_data, blocking=True)
            except Exception as e:
                _LOGGER.error("TelegramCustom: Errore location: %s", e)
            
            # Messaggio accompagnamento
            final_msg = message
            if parse_mode == "markdownv2": final_msg = self.escape_md2(message)
            if title_fmt: final_msg = f"{title_fmt}\n{final_msg}"
            if final_msg:
                await self._hass.services.async_call("telegram_bot", "send_message", 
                    {"target": self._chat_id, "message": final_msg, "parse_mode": parse_mode}, blocking=False)
            return

        elif media_key:
            item = data.get(media_key)
            url_or_file = self._extract_url(item)
            if not url_or_file: return await self._send_fallback_text(message)

            caption_raw = message
            if isinstance(item, dict): caption_raw = item.get("caption", message)
            elif isinstance(item, list) and isinstance(item[0], dict): caption_raw = item[0].get("caption", message)

            if parse_mode == "markdownv2":
                 safe_cap = self.escape_md2(caption_raw)
                 caption = f"{title_fmt}\n{safe_cap}" if title_fmt else safe_cap
            else: caption = f"{title_fmt}\n{caption_raw}" if title_fmt else caption_raw

            service_data["caption"] = caption
            is_local = str(url_or_file).strip().startswith(("/", "./", "file://"))
            if is_local: service_data["file"] = url_or_file
            else: service_data["url"] = url_or_file
        else:
            final_msg = message
            if parse_mode == "markdownv2": final_msg = self.escape_md2(message)
            if title_fmt: final_msg = f"{title_fmt}\n{final_msg}"
            
            if len(final_msg) > 4000:
                for part in self.split_message(final_msg):
                    await self._hass.services.async_call("telegram_bot", "send_message",
                        {"target": self._chat_id, "message": part, "parse_mode": parse_mode}, blocking=False)
                return
            service_data["message"] = final_msg

        # -----------------------------------------------------------
        # PULIZIA DATI
        # -----------------------------------------------------------
        excluded_keys = [
            "photo", "video", "document", "animation", "audio", "voice",
            "location", "media_group", "parse_mode", "actions", "push",
            "entity_id", "sticky", "channel", "group", "id", "metadata", "context",
            "reply_markup" # Importante escluderlo per passarlo processato sotto
        ]

        for key, value in data.items():
            if key not in excluded_keys:
                service_data[key] = value

        # -----------------------------------------------------------
        # GESTIONE TASTIERE (FIX DEFINITIVO)
        # -----------------------------------------------------------
        if media_key != "location":
            # 1. Recupera reply_markup
            rm = data.get("reply_markup")

            if rm:
                # FIX: Non passare "reply_markup" intero, ma estrai le chiavi
                # perché il servizio telegram_bot di HA vuole i parametri separati
                if "keyboard" in rm:
                    service_data["keyboard"] = rm["keyboard"]
                    service_data["resize_keyboard"] = rm.get("resize_keyboard", True)
                    service_data["one_time_keyboard"] = rm.get("one_time_keyboard", False)
                
                if "inline_keyboard" in rm:
                    service_data["inline_keyboard"] = rm["inline_keyboard"]
            
            # 2. Supporto legacy (se scritto fuori da reply_markup)
            elif "keyboard" in data:
                service_data["keyboard"] = data["keyboard"]
                service_data["resize_keyboard"] = data.get("resize_keyboard", True)
                service_data["one_time_keyboard"] = data.get("one_time_keyboard", False)
            elif "inline_keyboard" in data:
                service_data["inline_keyboard"] = data["inline_keyboard"]

        _LOGGER.debug("TelegramCustom invio a %s con dati: %s", service_to_call, service_data)

        try:
            await self._hass.services.async_call(
                "telegram_bot",
                service_to_call,
                service_data,
                blocking=False,
            )
        except Exception as e:
            _LOGGER.error("TelegramCustom: Errore %s: %s", service_to_call, e)
            await self._send_fallback_text(message)