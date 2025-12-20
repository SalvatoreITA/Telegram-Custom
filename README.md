# Telegram Custom Notify (Legacy Wrapper)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![maintainer](https://img.shields.io/badge/maintainer-Salvo-green.svg)]()

<img src="icon.png" width="150" height="150" alt="Icona Telegram Custom">

## 🇮🇹 Descrizione
Questo componente personalizzato per **Home Assistant** permette di continuare a utilizzare la vecchia piattaforma di notifica `notify` per Telegram, aggirando l'avviso di "Deprecazione" introdotto nelle versioni recenti di HA (2024/2025).

**Il problema:** Home Assistant sta rimuovendo il supporto YAML per `platform: telegram` sotto `notify`, obbligando a migrare alle nuove "Entità di notifica". Questo romperebbe tutte le vecchie automazioni che usano `service: notify.nome_utente`.

**La soluzione:** Questo componente crea un wrapper che:
1. Mantiene attivi i servizi `notify.nome_utente`.
2. Supporta **Testo, Foto, Video e Documenti** (esattamente come l'integrazione originale).
3. Elimina l'avviso di "Riparazione/Deprecazione".
4. Non richiede di modificare le automazioni esistenti.

---

## 🚀 Installazione

### Tramite HACS (Consigliato)
1. Apri HACS nel tuo Home Assistant.
2. Vai su **Integrazioni** > **Menu (3 puntini in alto a destra)** > **Repository personalizzati**.
3. Incolla l'URL di questo repository GitHub.
4. Seleziona la categoria **Integrazione**.
5. Clicca su **Aggiungi** e poi su **Scarica**.
6. **Riavvia Home Assistant**.

### Installazione Manuale
1. Scarica la cartella `custom_components/telegram_custom` da questo repository.
2. Copiala nella cartella `config/custom_components/` del tuo Home Assistant.
3. Riavvia Home Assistant.

---

## ⚙️ Configurazione

Modifica il tuo file `configuration.yaml`.
La configurazione è identica a quella vecchia, devi solo cambiare la `platform` da `telegram` a `telegram_custom`.

```yaml
# 1. Configurazione del Bot (Standard, non cambia nulla)
telegram_bot:
  - platform: polling
    api_key: "IL_TUO_TOKEN_TELEGRAM"
    allowed_chat_ids:
      - 123456789
      - 987654321

# 2. Configurazione Notify (Usa telegram_custom)
notify:
  - name: Salvo_Telegram
    platform: telegram_custom    # <--- CAMBIA SOLO QUESTO (era 'telegram')
    chat_id: 123456789

  - name: Evelin_Telegram
    platform: telegram_custom
    chat_id: 987654321
