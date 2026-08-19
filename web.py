"""Point d'entrée unique pour Render : Flask + bot Telegram."""

import logging
import os
import threading

from app import create_app


app = create_app()


def _demarrer_bot():
    try:
        from bot import run_bot
        run_bot()
    except Exception:
        app.logger.exception("Le bot Telegram s'est arrêté")


if os.environ.get("START_TELEGRAM_BOT", "").lower() in {"1", "true", "yes"}:
    threading.Thread(target=_demarrer_bot, name="telegram-bot", daemon=True).start()
else:
    logging.getLogger(__name__).info("Bot Telegram désactivé (START_TELEGRAM_BOT absent).")
