import logging
import logging.config
import os

def setup_logging(default_level=logging.INFO, log_file='project.log'):
    """
    Sets up logging configuration.
    """
    log_dir = os.path.join(os.path.dirname(__file__), '../logs')
    os.makedirs(log_dir, exist_ok=True)  # Ensure the logs directory exists
    log_path = os.path.join(log_dir, log_file)

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'level': logging.DEBUG
            },
            'file': {
                'class': 'logging.FileHandler',
                'formatter': 'detailed',
                'level': logging.INFO,
                'filename': log_path
            },
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': default_level,
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
            'apps': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': False,
            },
        }
    }

    logging.config.dictConfig(logging_config)
