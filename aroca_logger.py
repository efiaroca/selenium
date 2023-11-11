import logging
import time
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")


def aroca_logger():
    # Ask user if they want to tail the log
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logging.basicConfig(
        handlers=[
            logging.FileHandler(f"logs/{today}_jmwe.log"),
            console_handler,
        ],
        format="[ %(asctime)s ]-[ %(process)d ]-[ %(levelname)s ]-[ %(message)s ]",
        level=logging.DEBUG,
    )
