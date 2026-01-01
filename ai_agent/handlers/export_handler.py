import os
import logging
from config.config import Config
from datetime import datetime

class ExportHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.export_dir = Config.EXPORT_DIR
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    def export_to_text(self, content, filename=None):
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}.txt"

        filepath = os.path.join(self.export_dir, filename)
        try:
            with open(filepath, "w") as f:
                f.write(content)
            self.logger.info(f"Exported content to {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to export: {e}")
            return None

    def export_code(self, code, language="python", filename=None):
        extension_map = {
            "python": ".py",
            "javascript": ".js",
            "shell": ".sh",
            "html": ".html"
        }
        ext = extension_map.get(language.lower(), ".txt")

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"code_{timestamp}{ext}"
        elif not filename.endswith(ext):
            filename += ext

        return self.export_to_text(code, filename)
