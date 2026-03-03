import logging
import os
from datetime import datetime

# Log klasörünü oluştur
if not os.path.exists("logs"):
    os.makedirs("logs")

# Log dosya adını o günün tarihiyle oluştur
log_filename = f"logs/agent_{datetime.now().strftime('%Y-%m-%d')}.log"

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | [%(levelname)s] | %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler() # Terminale de yazması için
    ]
)

logger = logging.getLogger("MamiAgent")

def log_agent_step(step_name, data):
    """Agent'ın adımlarını düzenli bir şekilde kaydeder."""
    logger.info(f"{step_name.upper()} >> {data}")