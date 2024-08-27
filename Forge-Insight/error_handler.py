import logging
import traceback
from config import LOG_FILE, LOG_LEVEL, LOG_FORMAT

class ErrorHandler:
    def __init__(self):
        self.logger = self.setup_logger()
        self.ui_callback = None

    def setup_logger(self):
        logger = logging.getLogger('ForgeInsight')
        logger.setLevel(LOG_LEVEL)
        
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)
        
        return logger

    def set_ui_callback(self, callback):
        self.ui_callback = callback

    def handle_error(self, error, error_type="Error"):
        error_message = f"{error_type}: {str(error)}"
        stack_trace = traceback.format_exc()
        
        self.logger.error(f"{error_message}\n{stack_trace}")
        
        if self.ui_callback:
            self.ui_callback(error_message, stack_trace)

    def log_info(self, message):
        self.logger.info(message)

    def log_warning(self, message):
        self.logger.warning(message)

    def log_debug(self, message):
        self.logger.debug(message)

    def get_recent_logs(self, num_lines=50):
        with open(LOG_FILE, 'r') as log_file:
            return ''.join(log_file.readlines()[-num_lines:])