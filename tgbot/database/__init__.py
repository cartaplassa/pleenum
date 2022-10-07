import os
import logging

from tgbot.database.declaration import User, Pleenum, Member
from tgbot.database.declaration import Base, engine, BASE_DIR, DB_FILENAME


if not os.path.exists(os.path.join(BASE_DIR, DB_FILENAME)):
    logging.warning(f"Database at {os.path.join(BASE_DIR, DB_FILENAME)} not found, creating new one")
    Base.metadata.create_all(engine)
else:
    logging.info("Database found")
