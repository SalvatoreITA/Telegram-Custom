# Telegram Custom Notify (Legacy Wrapper)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![maintainer](https://img.shields.io/badge/maintainer-Salvatore_Lentini_--_DomHouse.it-green.svg)](https://www.domhouse.it)

<img src="icon.png" width="120" height="120" alt="Icona Telegram Custom">

## 🇮🇹 Descrizione
Questo componente personalizzato per **Home Assistant** permette di continuare a utilizzare la classica piattaforma `notify` per Telegram, risolvendo definitivamente l'avviso di **"Deprecazione / Servizio Notify non supportato"** (previsto per Home Assistant 2026).

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
# 1. Configurazione Bot (Questa NON cambia, serve per la connessione)
telegram_bot:
  - platform: polling
    api_key: "IL_TUO_TOKEN_TELEGRAM"
    allowed_chat_ids:
      - 123456789
      - 987654321

# 2. Configurazione Notify (Modifica SOLO la platform)
notify:
  - name: Salvo_Telegram
    platform: telegram_custom    # <--- PRIMA ERA 'telegram', ORA 'telegram_custom'
    chat_id: 123456789
