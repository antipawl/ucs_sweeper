# -*- coding: utf-8 -*-

import logging
from fluent import handler
from os import getenv

from ucs_sweeper.core.result_files import get_log_filename
from ucs_sweeper.core.result_files import get_plugin_log_filename
from ucs_sweeper.support.pdi_syslog import config_logging

_INFO_FMT = '%(levelname)-8s %(asctime)s [%(tag)s][%(address)s] %(message)s'
_DEBUG_FMT = '%(levelname)s %(asctime)s %(name)s:%(filename)s:%(lineno)d [%(tag)s][%(address)s] %(message)s'
_DATE_FMT = '%H:%M:%S'
_FLUENTD_FMT = {
    "levelname": "%(levelname)s",
    "levelno": "%(levelno)d",
    "name": "%(name)s",
    "file": "%(filename)s:%(lineno)d",
    "address": "%(address)s",
    "tag": "%(tag)s",
}

loggers_tags = {'calypso.run': 'CORE',
                'calypso.metric': 'METRIC',
                'calypso.core': 'CORE',
                'calypso.ha': 'HA'
                }


class CalypsoAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs["extra"] = self.extra
        kwargs["extra"]["tag"] = kwargs["extra"].get("tag")
        kwargs["extra"]["address"] = kwargs["extra"].get("address")
        return msg, kwargs

    def __init__(self, *args, **kwargs):
        super(CalypsoAdapter, self).__init__(*args, **kwargs)
        self.warn = self.warning


class CalypsoOutputFormatter(logging.Formatter):
    def __init__(self, fmt, datefmt=None):
        super(CalypsoOutputFormatter, self).__init__(fmt, datefmt)

    def format(self, record):
        msg = super(CalypsoOutputFormatter, self).format(record)
        if record.message != "":
            parts = msg.split(record.message)
            msg = msg.replace('\n', '\n' + parts[0])
            msg = msg.replace("[None]", "")
        return msg


class SilencePluginsFilter(logging.Filter):
    def filter(self, record):
        if record.levelno < logging.WARNING and record.name in _SILENT_PLUGINS:
            return False
        return True


class PluginInfoFilter(logging.Filter):
    def filter(self, record):
        return not record.__dict__.get('plugin_only', False)


def get_stream_handler(verbose_mode=False):
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    if verbose_mode:
        stream_handler.setLevel(logging.DEBUG)
    else:
        stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(CalypsoOutputFormatter(fmt=_INFO_FMT, datefmt=_DATE_FMT))
    stream_handler.addFilter(SilencePluginsFilter())
    stream_handler.addFilter(PluginInfoFilter())
    return stream_handler


def get_info_file_handler():
    info_log_fn = get_log_filename(suffix='info')
    info_file_handler = logging.FileHandler(filename=info_log_fn, encoding="utf-8")
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(CalypsoOutputFormatter(fmt=_INFO_FMT, datefmt=_DATE_FMT))
    info_file_handler.addFilter(PluginInfoFilter())
    return info_file_handler


def get_debug_log_file_handler():
    debug_log_fn = get_log_filename(suffix='debug')
    debug_file_handler = logging.FileHandler(filename=debug_log_fn, encoding="utf-8")
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(CalypsoOutputFormatter(fmt=_DEBUG_FMT, datefmt=_DATE_FMT))
    debug_file_handler.addFilter(PluginInfoFilter())
    return debug_file_handler


def get_fluent_handler(run_id):
    fluent_handler = handler.FluentHandler(
        f"calypso.{run_id}",
        host=getenv('FLUENTD_LOGGING_SERVICE_HOST'),
        port=24224,
        nanosecond_precision=True)
    fluent_handler.setLevel(logging.DEBUG)
    fluent_handler.setFormatter(handler.FluentRecordFormatter(_FLUENTD_FMT))
    return fluent_handler


_SILENT_PLUGINS = []


def add_plugin_to_silenced(plugin_name):
    _SILENT_PLUGINS.append(plugin_name)


def _cease_furious_loggers():
    furious_loggers = ['paramiko', 'requests', 'suds', 'peewee']
    for logger_name in furious_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def configure_logging(main_config):
    atom_syslog_address = main_config.atom_syslog_address
    atom_correlation_id = main_config.atom_correlation_id
    service = main_config.service

    if service:
        setup_service_logger(run_id=main_config.run_id)
    elif atom_syslog_address:
        setup_atom_logger(atom_syslog_address, atom_correlation_id)
    else:
        setup_logger(verbose_mode=main_config.verbose_mode)


def setup_logger(stream_only=False, verbose_mode=False):
    root = logging.getLogger("calypso")
    root.setLevel(logging.DEBUG)
    root.handlers = []
    root.addHandler(get_stream_handler(verbose_mode))
    if not stream_only:
        root.addHandler(get_info_file_handler())
        root.addHandler(get_debug_log_file_handler())
    _cease_furious_loggers()


def setup_atom_logger(syslog_address, correlation_id, stream_only=False):
    root = logging.getLogger("calypso")
    root.setLevel(logging.DEBUG)
    config_logging(root, syslog_address, correlation_id)
    if not stream_only:
        root.addHandler(get_info_file_handler())
        root.addHandler(get_debug_log_file_handler())
    _cease_furious_loggers()


def setup_service_logger(run_id):
    root_logger = logging.getLogger()
    root_logger.handlers = []
    calypso_logger = logging.getLogger("calypso")
    calypso_logger.setLevel(logging.DEBUG)
    calypso_logger.handlers = []
    calypso_logger.addHandler(get_stream_handler(verbose_mode=True))
    calypso_logger.addHandler(get_fluent_handler(run_id))
    calypso_logger.addHandler(get_info_file_handler())
    calypso_logger.addHandler(get_debug_log_file_handler())
    _cease_furious_loggers()


def get_plugin_logger(plugin_name, address_tag=None):
    """
    :param plugin_name:
    :param address_tag:
    :rtype: logging.Logger
    """
    plugin_logger = logging.getLogger(f"calypso.plugin.{plugin_name}")

    current_handlers = [handler for handler in plugin_logger.handlers
                        if handler.get_name() == 'plugin_info_log']
    if not current_handlers:
        plugin_file_fn = get_plugin_log_filename(plugin_name)
        plugin_file_handler = logging.FileHandler(filename=plugin_file_fn)
        plugin_file_handler.setLevel(logging.INFO)
        plugin_file_handler.setFormatter(CalypsoOutputFormatter(fmt=_INFO_FMT,
                                                                datefmt=_DATE_FMT))
        plugin_file_handler.set_name('plugin_info_log')
        plugin_logger.addHandler(plugin_file_handler)
    return CalypsoAdapter(plugin_logger, make_logger_extra_argument(plugin_name, address_tag))


def make_logger_extra_argument(name, address):
    extra = {'tag': name}
    if address:
        extra['address'] = address
    return extra


def get_adapted_logger(name):
    logger = logging.getLogger(name)
    tag = loggers_tags.get(name, 'CORE')
    return CalypsoAdapter(logger, {'tag': tag, 'address': None})


class UniqLogger:
    def __init__(self, logger):
        self._log = logger
        self._buff = None

    def __call__(self, message):
        self.log(message)

    def log(self, message):
        if message != self._buff:
            self._buff = message
            self._log(message)


def mute_external_logger(path):
    """ @param path: indicate logger location
    Example 'sleuth2.handlers.qkviewcollect' """

    def decorator(func):
        def wrapper(*args, **kwargs):
            logging.getLogger(path).disabled = True
            try:
                func(*args, **kwargs)
            finally:
                logging.getLogger(path).disabled = False

        return wrapper

    return decorator
