import os
import time
import sys
import logging
from logging.handlers import TimedRotatingFileHandler


class PurpleLogger(object):
    """source https://git.eveinsight.net"""
    @classmethod
    def path(cls, file_name):
        fname = file_name.split('.', 1)[0]
        pt_name = 'logs/{}'.format(fname)
        os.makedirs(pt_name, exist_ok=True)
        return os.path.join(pt_name, fname)

    @classmethod
    def get_logger(cls, name, file_name, level=logging.INFO, console_print=False, console_level=logging.WARNING,
                   child=False, days_delete_after=30) -> logging.Logger:
        logger = logging.getLogger(name)
        if len(logger.handlers) == 0 and not child:
            logger.setLevel(level)
            f_fmt = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
            f_fmt.converter = time.gmtime
            if console_print:
                if console_level >= logging.WARNING:
                    sh_console = logging.StreamHandler(stream=sys.stderr)
                    sh_console.setFormatter(f_fmt)
                else:
                    sh_console = logging.StreamHandler(stream=sys.stdout)
                    fmt = logging.Formatter('%(asctime)s - %(message)s')
                    fmt.converter = time.gmtime
                    sh_console.setFormatter(fmt)
                sh_console.setLevel(console_level)
                logger.addHandler(sh_console)
            fh = TimedRotatingFileHandler(cls.path(file_name), when='midnight', interval=1,
                                          backupCount=days_delete_after, delay=True, utc=True, encoding="utf-8")
            fh.setFormatter(f_fmt)
            fh.setLevel(level)
            logger.addHandler(fh)
        return logger
