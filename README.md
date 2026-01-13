# Telegram Custom Notify (Legacy Wrapper)

[![it](https://img.shields.io/badge/lang-it-green.svg)](https://github.com/SalvatoreITA/telegram-custom/blob/main/README_it.md)
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/SalvatoreITA/telegram-custom/blob/main/README.md)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![maintainer](https://img.shields.io/badge/maintainer-Salvatore_Lentini_--_DomHouse.it-green.svg)](https://www.domhouse.it)

<img src="icon.png" width="120" height="120" alt="Telegram Custom Icon">

## 🇺🇸 Description
This custom component for **Home Assistant** allows you to continue using the classic `notify` platform for Telegram, permanently solving the **"Deprecation / Notify service not supported"** warning (scheduled for Home Assistant 05.2026).

**The Problem:**
Home Assistant is removing YAML support for `platform: telegram` under the `notify` section, forcing users to migrate to the new "Notification Entities". This change "breaks" all existing automations that use `notify.username` services.

**The Solution:**
This component creates a transparent "bridge" that:
1.  ✅ **Keeps your old services** (e.g., `notify.salvo`, `notify.group`).
2.  ✅ **Eliminates the repair/deprecation warning** from settings.
3.  ✅ **Supports everything:** Text, Emojis, Photos, Videos, and Documents.
4.  ✅ **Zero changes to automations:** You don't have to rewrite your scripts.

---

## 🚀 Installation

### Method 1: Via HACS (Recommended)
1.  Open **HACS** in your Home Assistant.
2.  Go to **Integrations** > **Menu (3 dots top right)** > **Custom repositories**.
3.  Paste this GitHub repository URL:
    `https://github.com/SalvatoreITA/Telegram-Custom`
4.  Select **Integration** as the category.
5.  Click **Add** and then **Download**.
6.  **Restart Home Assistant**.

### Method 2: Manual
1.  Download the `custom_components/telegram_custom` folder from this repository.
2.  Copy it to the `config/custom_components/` folder of your Home Assistant instance.
3.  Restart Home Assistant.

---

## ⚙️ Configuration

Configuration is extremely simple. You just need to modify your `configuration.yaml` file by changing the platform name from `telegram` to `telegram_custom`.

**Example configuration.yaml:**

```yaml
# 1. Bot Configuration (This MUST be removed and integrated via the UI)
telegram_bot:
  - platform: polling
    api_key: "YOUR_TELEGRAM_TOKEN"
    allowed_chat_ids:
      - 123456789

# 2. Notify Configuration (Modify ONLY the platform)
notify:
  - name: Salvo_Telegram
    platform: telegram_custom    # <--- WAS 'telegram', NOW 'telegram_custom'
    chat_id: 123456789
```
After modifying the file, restart Home Assistant to apply the changes.

## 💡 Automation Examples
Once installed, your old automations will work exactly as before, including those with multimedia attachments.

**Simple text message:**
```yaml
service: notify.salvo_telegram
data:
  message: "Hello! The system is online and running."
```
## ❤️ Credits
Developed by Salvatore Lentini - DomHouse.it for the Home Assistant community, to preserve the simplicity of classic YAML configuration.
