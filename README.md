# Telegram Custom Notify (Legacy Wrapper)

[![it](https://img.shields.io/badge/lang-it-green.svg)](https://github.com/SalvatoreITA/telegram-custom/blob/main/README_it.md)
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/SalvatoreITA/telegram-custom/blob/main/README.md)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-1.0.2-blue.svg)]()
[![maintainer](https://img.shields.io/badge/maintainer-Salvatore_Lentini_--_DomHouse.it-green.svg)](https://www.domhouse.it)

<div align="center">
  <img src="icon.png" width="150" alt="Telegram Custom Notify Icon">
  <h1>Telegram Custom Notify</h1>
  <p><b>Advanced Notifications for Home Assistant</b></p>
</div>

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
Once installed, your old automations will work exactly as before, including those with media attachments.

**1. Plain text message:**
The title is automatically formatted in bold (*Title*) and added to the top of the message.
```yaml
service: notify.salvo_telegram
data:
  title: "⚠️ Server"
  message: "Hello! The system is online and working."
```

**2. Automatic Formatting (HTML vs. Markdown):**
The component automatically detects whether you're using HTML or Markdown.

HTML example (detects <> tags):
```yaml
service: notify.salvo_telegram
data:
  title: "Weather"
  message: "Today will be <b>sunny</b> with a chance of <i>rain</i> in the afternoon."
```

Markdown example (standard):
```yaml
service: notify.salvo_telegram
data:
  title: "Server Status"
  message: "CPU at *90%*.\nCheck `error.log`."
```

**3. Sending a Photo (from URL):**
When sending a photo, the text in the message is automatically used as the image caption.
```yaml
service: notify.salvo_telegram
data:
  title: Cancello
  message: "Foto Ingresso"
  data:
    photo:
      - url: "http://192.168.1.246:8123{{state_attr('camera.cancellino'','entity_picture')}}"
```

**4. Sending a Photo (Local):**
When sending a photo, the text in the message is automatically used as the image caption.
```yaml
service: notify.salvo_telegram
data:
  title: "🔔 Din Don! Foto"
  message: "Someone rang the doorbell."
  data:
    photo:
      file: "/config/www/allarme/foto/camera1.jpg"
```

**5. Sending a Video (Local):**
When sending a video, the text from the message is automatically used as the image caption.
```yaml
service: notify.salvo_telegram
data:
  title: "🔔 Din Don! Video"
  message: "Someone rang the doorbell."
  data:
    video:
      file: "/config/www/allarme/foto/video1.mp4"
```

**6. Multiple Media Groups:**
Send multiple photos or videos at once. Note: The title and message are attached to the first photo.
```yaml
service: notify.salvo_telegram
data:
  title: "🚨 Full Report"
  message: "Here's everything that happened."
  data:
    media_group:
      - type: photo
        file: "/config/www/allarme/foto/camera1.jpg"
        caption: "Photo Local File"
      - type: photo
        url: "https://domhouse.it/foto.jpg"
        caption: "Photo Web URL"
      - type: video
        file: "/config/www/allarme/foto/video1.mp4"
        caption: "Local Video"
```

**7. Send Documents and Files:**
Useful for sending the log of the PDF file generated by Home Assistant.
```yaml
service: notify.salvo_telegram
data:
  title: "System Log"
  message: "Here is the updated log file."
  data:
    document: "/config/home-assistant.log" # Requires the folder to be in letlist 
```

**8. Rich HTML Notification:**
You can use HTML tags without worrying about escaping special characters like you would with Markdown.
```yaml
service: notify.salvo_telegram
data:
  title: "Good morning ☀️"
  # The script detects <> tags and automatically switches to HTML
  message: >
    Today will be <b>{{ states('sensor.temperature') }}°C</b>.

    The condition is: <i>{{ states('weather.casa') }}</i>.

    <a href="https://weather.com">Click here for details</a> 
```

**9. Notifications with Buttons (Inline Keyboard)**
The original component passes all extra data directly to Telegram. This allows you to use inline keyboards to create interactive automations.
```yaml
service: notify.salvo_telegram
data:
  title: "Alarm Armed"
  message: "No one home. What do you want to do?"
  data:
    inline_keyboard:
      - "Disarm:/disarm_alarm"
      - "Arm Perimeter:/arm_perimeter"
```

**10. Persistent Menu for Commands**
Instead of the usual inline buttons, this turns your phone's keyboard into a home remote control.
```yaml
service: notify.salvo_telegram
data:
  message: "🔧 Maintenance Mode Active. Select command:"
  data:
    reply_markup:
      keyboard:
        - "Restart HA, Backup"
        - "Shut Down All, Exit"
      resize_keyboard: true
      one_time_keyboard: true
```

**11. Send a saved MP3 file (Ringtone or Alarm)**
If you have any audio files (e.g. a siren, a pre-recorded voice alert) in the /config/www/ folder.
```yaml
service: notify.salvo_telegram
data:
  title: "🔊 Notify"
  message: "Alarm activated!"
  data:
    audio:
      file: "/config/www/notifichehome/fischio.mp3"
      caption: "Internal Siren"
```

**12. Submit a Song or Podcast from a URL**
If the audio is online.
```yaml
service: notify.salvo_telegram
data:
  title: "🎵 Song"
  message: "Audio track"
  data:
    audio:
      url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
      caption: "Music Demo"
```

**13. Fixed Position (e.g. Home, Work)**
Useful for sending specific coordinates.
```yaml
service: notify.salvo_telegram
data:
  message: "Here's where I parked! 🚗"
  data:
    location:
      latitude: 41.9028
      longitude: 12.4964
```

**14. Real-Time Location (Car/Person)**
Send the exact location of a device_tracker or person.
```yaml
service: notify.salvo_telegram
data:
  message: Real Time Car Position 🚗
  data:
    location:
      latitude: "{{ state_attr('device_tracker.595_traccar', 'latitude') }}"
      longitude: "{{ state_attr('device_tracker.595_traccar', 'longitude') }}"
```

## ⚠️ Important Note for Local Files
For examples 1 and 3 to work, you must ensure that Home Assistant has permission to read the folders where you save files. In your general configuration.yaml, you must have a section similar to this:
```yaml
homeassistant:
  allowlist_external_dirs:
    - "/tmp"
    - "/config"
    - "/media"
```

## ❤️ Credits
Developed by [Salvatore Lentini - DomHouse.it](https://www.domhouse.it)
