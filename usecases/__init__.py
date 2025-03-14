from sqlalchemy.orm import Session

import logger
import logging

from database import base_engine

session = Session(base_engine, autoflush=False)

usecase_logger = logging.getLogger("usecase")