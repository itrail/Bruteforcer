# -*- coding: utf-8 -*-
import sys
import logging
import logging.handlers


class Logger(object):
    def __init__(self):
        self.logger = logging.getLogger("")
        self.logger.setLevel(logging.DEBUG)
        self._formatters = dict(
            basic=logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"),
            rich=logging.Formatter(
                "%(asctime)s -> %(levelname)s -> %(filename)s -> %(name)s -> %(funcName)s() -> %(message)s"
            ),
        )

    def Init(self, loggerType, loggerInit, *args, **kwargs):
        if loggerInit:
            if loggerType == "std":
                self._stdLogger(*args, **kwargs)
        return self

    def Get(self):
        return self.logger

    def AddFormatter(self, name, scheme):
        self._formatters[name] = scheme
        return self

    def _stdLogger(self, stream=sys.stdout, level=logging.DEBUG, formatterName="rich"):
        # handler: stream
        log_handler_stream = logging.StreamHandler(stream=sys.stderr)
        log_handler_stream.setLevel(level)
        log_handler_stream.setFormatter(self._getFormatter(name=formatterName))
        self.logger.addHandler(log_handler_stream)
        return self

    def _getFormatter(self, name):
        if name in self._formatters.keys():
            return self._formatters[name]
        else:
            return self._formatters["basic"]
