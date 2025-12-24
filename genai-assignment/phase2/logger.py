import logging
import sys
from pathlib import Path

def setup_logger():
    """
    Configures a centralized logger for the application.
    Writes logs to both the console (stdout) and a file (logs/chatbot.log).
    """
    
    #Create a logger
    logger = logging.getLogger("medical_chatbot")
    logger.setLevel(logging.INFO)

    #Prevent adding handlers multiple times 
    if logger.hasHandlers():
        return logger

    #Create 'logs' directory if it doesn't exist
    log_dir = Path(__file__).parent / ".." / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / "chatbot.log"

    #Define format 
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    #File Handler (Writes to disk, supports Hebrew via utf-8)
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setFormatter(formatter)

    #Stream Handler (Writes to console)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    #Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

# Create the singleton instance
logger = setup_logger()