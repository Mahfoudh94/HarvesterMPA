import logging
from logging import handlers
import os

daily_handler = handlers.TimedRotatingFileHandler("logs/current.log", when="MIDNIGHT", backupCount=7)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s :: %(name)s :: %(levelname)s ::\n%(message)s",
    handlers=[daily_handler]
)

if not os.path.exists("logs"):
    os.makedirs("logs")
if not os.path.exists("logs/current.log"):
    with open("logs/current.log", "w") as f:
        pass

base_logger = logging.getLogger('base')
