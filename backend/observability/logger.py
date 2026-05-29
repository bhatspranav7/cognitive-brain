import logging

logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def log_event(message: str):
    logging.info(message)