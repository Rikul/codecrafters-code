import asyncio
from . import config
from .display import log
from .background_agent import BackgroundAgent
from .message_queue import MessageQueue

async def start_server() -> None:

    log.info("Starting server...")
    telegram_channel = None
    mq = MessageQueue()

    if config.get("telegram"):
        bot_token = config.telegram.get("BOT_TOKEN")

        if not bot_token:
            log.error("Telegram BOT_TOKEN not set in config, skipping Telegram channel")
            return

        from .telegram_channel import TelegramChannel
        telegram_channel = TelegramChannel(mq, bot_token=bot_token, allow_from=config.telegram.get("ALLOW_FROM", []))

    if not telegram_channel:
        log.error("No channels configured, exiting...")
        return

    telegram_channel.start()
    telegram_agent = BackgroundAgent(mq=mq, channel=telegram_channel)

    await asyncio.gather(
        telegram_channel.run_polling(),
        telegram_agent.process_incoming(),
        mq.process_outgoing(),
    )