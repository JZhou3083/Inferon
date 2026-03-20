import logging
import json


class JsonFormatter(logging.Formatter):
    def format(self, record):
        base = {
            "time": self.formatTime(record),
            "level": record.levelname,
        }

        # 👇 核心升级点
        if isinstance(record.msg, dict):
            base.update(record.msg)
        else:
            base["message"] = str(record.msg)

        return json.dumps(base)


def setup_logger():
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    logger = logging.getLogger("inferon")
    logger.setLevel(logging.INFO)

    # 避免重复 handler
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


# 全局 logger
logger = setup_logger()