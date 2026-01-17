# Telegram Custom Notify (Legacy Wrapper)

[![it](https://img.shields.io/badge/lang-it-green.svg)](https://github.com/SalvatoreITA/telegram-custom/blob/main/README_it.md)
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/SalvatoreITA/telegram-custom/blob/main/README.md)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-1.0.1-blue.svg)]()
[![maintainer](https://img.shields.io/badge/maintainer-Salvatore_Lentini_--_DomHouse.it-green.svg)](https://www.domhouse.it)

<img src="icon.png" width="120" height="120" alt="Icona Telegram Custom">

## 🇮🇹 Descrizione
Questo componente personalizzato per **Home Assistant** permette di continuare a utilizzare la classica piattaforma `notify` per Telegram, risolvendo definitivamente l'avviso di **"Deprecazione / Servizio Notify non supportato"** (previsto per Home Assistant 05.2026).

**Il Problema:**
Home Assistant sta rimuovendo il supporto YAML per `platform: telegram` sotto la sezione `notify`, obbligando gli utenti a migrare alle nuove "Entità di notifica". Questo cambiamento "rompe" tutte le automazioni esistenti che utilizzano i servizi `notify.nome_utente`.

**La Soluzione:**
Questo componente crea un "ponte" trasparente che:
1.  ✅ **Mantiene i tuoi vecchi servizi** (es. `notify.salvo`, `notify.gruppo`).
2.  ✅ **Elimina l'avviso di riparazione/deprecazione** dalle impostazioni.
3.  ✅ **Supporta tutto:** Testo, Emoji, Foto, Video e Documenti.
4.  ✅ **Zero modifiche alle automazioni:** Non devi riscrivere i tuoi script.

---

## 🚀 Installazione

### Metodo 1: Tramite HACS (Consigliato)
1.  Apri **HACS** nel tuo Home Assistant.
2.  Vai su **Integrazioni** > **Menu (3 puntini in alto a destra)** > **Repository personalizzati**.
3.  Incolla l'URL di questo repository GitHub. 
    https://github.com/SalvatoreITA/Telegram-Custom
4.  Nella categoria seleziona **Integrazione**.
5.  Clicca su **Aggiungi** e poi su **Scarica**.
6.  **Riavvia Home Assistant**.

### Metodo 2: Manuale
1.  Scarica la cartella `custom_components/telegram_custom` da questo repository.
2.  Copiala nella cartella `config/custom_components/` del tuo Home Assistant.
3.  Riavvia Home Assistant.

---

## ⚙️ Configurazione

La configurazione è semplicissima. Devi solo modificare il tuo file `configuration.yaml` cambiando il nome della piattaforma da `telegram` a `telegram_custom`.

**Esempio configuration.yaml:**

```yaml
# 1. Configurazione Bot (Questa Deve Essere Eliminata e Deve essere integrata tramite interfaccia grafica)
telegram_bot:
  - platform: polling
    api_key: "IL_TUO_TOKEN_TELEGRAM"
    allowed_chat_ids:
      - 123456789

# 2. Configurazione Notify (Modifica SOLO il platform)
notify:
  - name: Salvo_Telegram
    platform: telegram_custom    # <--- PRIMA ERA 'telegram', ORA 'telegram_custom'
    chat_id: 123456789
```
Dopo aver modificato il file, riavvia Home Assistant per applicare le modifiche.

## 💡 Esempi di Automazioni
Una volta installato, le tue vecchie automazioni funzioneranno esattamente come prima, incluse quelle con allegati multimediali.

**1. Messaggio di testo semplice:**
Il titolo viene formattato automaticamente in grassetto (*Titolo*) e aggiunto in testa al messaggio.
```yaml
service: notify.salvo_telegram
data:
  title: "⚠️ Server"
  message: "Ciao! Il sistema è online e funzionante."
```

**2. Formattazione Automatica (HTML vs Markdown):**
Il componente riconosce automaticamente se stai usando HTML o Markdown.

Esempio HTML (rileva i tag <>):
```yaml
service: notify.salvo_telegram
data:
  title: "Meteo"
  message: "Oggi sarà <b>soleggiato</b> con possibilità di <i>pioggia</i> nel pomeriggio."
```

Esempio Markdown (standard):
```yaml
service: notify.salvo_telegram
data:
  title: "Stato Server"
  message: "CPU al *90%*.\nControllare i log `error.log`."
```

**3. Invio di una Foto (da URL):**
Quando si invia una foto, il testo del message viene usato automaticamente come didascalia (caption) dell'immagine.
```yaml
service: notify.salvo_telegram
data:
  title: Cancello
  message: "Foto Ingresso"
  data:
    photo:
      - url: "http://192.168.1.246:8123{{state_attr('camera.ingresso_condominiale','entity_picture')}}"
```

**4. Invio di una Foto (Locale):**
Quando si invia una foto, il testo del message viene usato automaticamente come didascalia (caption) dell'immagine.
```yaml
service: notify.salvo_telegram
data:
  title: "🔔 Din Don! Foto"
  message: "Qualcuno ha suonato il campanello."
  data:
    photo:
      file: "/config/www/foto/camera1.jpg"
```

**5. Invio di un Video (Locale):**
Quando si invia un video, il testo del message viene usato automaticamente come didascalia (caption) dell'immagine.
```yaml
service: notify.salvo_telegram
data:
  title: "🔔 Din Don! Video"
  message: "Qualcuno ha suonato il campanello."
  data:
    video:
      file: "/config/www/video/video1.mp4"
```

**6. Media Group Multipli:**
Invia più foto o video insieme. Nota: Il titolo e il messaggio vengono allegati alla prima foto.
```yaml
service: notify.salvo_telegram
data:
  title: "🚨 Report Completo"
  message: "Ecco tutto quello che è successo."
  data:
    media_group:
      - type: photo
        file: "/config/www/allarme/foto/camera1.jpg"
        caption: "Foto File Locale"
      - type: photo
        url: "https://domhouse.it/foto.jpg"
        caption: "Foto URL Web"
      - type: video
        file: "/config/www/allarme/foto/video1.mp4"
        caption: "Video Locale"       
```

**7. Invio Documenti e File:**
Utile per inviare log o file PDF generati da Home Assistant.
```yaml
service: notify.salvo_telegram
data:
  title: "Log Sistema"
  message: "Ecco il file di log aggiornato."
  data:
    document: "/config/home-assistant.log" # Richiede che la cartella sia in allowlist      
```
**8. Notifica Ricca in HTML:**
Puoi usare tag HTML senza preoccuparti di fare l'escape dei caratteri speciali come accadeva col Markdown.
```yaml
service: notify.salvo_telegram
data:
  title: "Buongiorno ☀️"
  # Lo script rileva i tag <> e passa automaticamente a HTML
  message: >
    Oggi ci saranno <b>{{ states('sensor.temperature') }}°C</b>.
    
    La condizione è: <i>{{ states('weather.casa') }}</i>.
    
    <a href="https://weather.com">Clicca qui per i dettagli</a>   
```

**9. Notifiche con Bottoni (Inline Keyboard)**
Il componente originale passa tutti i dati extra direttamente a Telegram. Questo permette di usare le tastiere inline per creare automazioni interattive.
```yaml
service: notify.salvo_telegram
data:
  title: "Allarme Inserito"
  message: "Nessuno in casa. Cosa vuoi fare?"
  data:
    inline_keyboard:
      - "Disinserisci:/disarm_alarm"
      - "Attiva Perimetrale:/arm_perimeter"
```

**10. Menu Persistente per Comandi**
Invece dei soliti bottoni sotto il messaggio (inline), questo cambia la tastiera del tuo telefono in un telecomando per la casa.
```yaml
service: notify.salvo_telegram
data:
  message: "🔧 Modalità Manutenzione Attiva. Seleziona comando:"
  data:
    reply_markup:
      keyboard:
        - "Riavvia HA, Backup"
        - "Spegni Tutto, Esci"
      resize_keyboard: true
      one_time_keyboard: true
```

## ⚠️ Nota Importante per i File Locali
Affinché gli esempi 1 e 3 funzionino, devi assicurarti che Home Assistant abbia il permesso di leggere le cartelle dove salvi i file. Nel tuo configuration.yaml generale, devi avere una sezione simile a questa:
```yaml
homeassistant:
  allowlist_external_dirs:
    - "/tmp"
    - "/config"
    - "/media"
```

## ❤️ Crediti
Sviluppato da [Salvatore Lentini - DomHouse.it](https://www.domhouse.it)
