"""This plugin sends messages to a remote syslog server for Calypso on ATOM
"""

import datetime
import json
import traceback
import logging
import logging.handlers
import socket

from datetime import datetime

LOG = logging.getLogger('pdi_ansible_syslog')


class PdiSyslogHandler(logging.handlers.SysLogHandler):
    """Set the address of the syslog server.
    """
    def __init__(self, address, *args, **kwargs):
        logging.handlers.SysLogHandler.__init__(self, address, *args, **kwargs)


class PdiSyslogFormatter(logging.Formatter):

    BUILTIN_ATTRS = (
        'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
        'funcName', 'levelname', 'levelno', 'lineno', 'module',
        'msecs', 'message', 'msg', 'name', 'pathname', 'process',
        'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName')

    def __init__(self, tag=None, *args, **kwargs):
        self.tag = tag
        fmt = '%(message)s'
        logging.Formatter.__init__(self, fmt, *args, **kwargs)

    def format(self, record):
        args = record.__dict__
        msg = {}

        # unix timestamp in ISO 8611 utc format with milliseconds
        now = datetime.utcfromtimestamp(args.get('created', 0))
        milliseconds = now.microsecond / 1000
        now = now.replace(microsecond=0)
        timestamp = '%s.%sZ' % (now.isoformat(), milliseconds)
        msg['time'] = timestamp

        # copy all extra args
        for key, value in args.items():
            if key not in self.BUILTIN_ATTRS:
                msg[key] = value

        # copy white listed built-in fields
        for key in ('name', 'msg', 'levelname'):
            if key in args:
                msg[key] = args[key]

        # add the exception info
        if args.get('exc_info', None) is not None:
            exc_type, exc_value, _tb = args['exc_info']
            tb = ''.join(traceback.format_exception(exc_type,
                                                    exc_value, _tb))
            msg['exc_type'] = exc_type
            msg['exc_value'] = exc_value
            msg['traceback'] = tb

        # format a valid syslog message
        # <PRI>TIMESTAMP HOSTNAME TAG[PID]: MSG
        message = json.dumps(msg)
        tag = self.tag
        if not tag:
            tag = args['processName']
        message = '%s %s %s[%s]: %s' % (timestamp, socket.getfqdn(),
                                        tag, args['process'], message)
        return message


class PdiSyslogFilter(logging.Filter):
    """Put additional information in the record for logging.
    """
    def __init__(self, name='', correlation_id=''):
        logging.Filter.__init__(self, name)
        self.correlation_id = correlation_id

    def filter(self, record):
        record.correlation_id = self.correlation_id
        return logging.Filter.filter(self, record)


def get_syslog_handler(log, syslog_address, correlation_id):

    if syslog_address:
        parts = syslog_address.split(':')
        if len(parts) == 2:
            syslog_server = parts[0]
            syslog_server_port = int(parts[1])

            address = (syslog_server, syslog_server_port)
            log.info(
                'syslog configured: %s:%s, correlation_id: %s' %
                (syslog_server, syslog_server_port, correlation_id)
            )

            syslog_handler = PdiSyslogHandler(address=address)
            syslog_handler.addFilter(PdiSyslogFilter(correlation_id=correlation_id))
            syslog_handler.setFormatter(PdiSyslogFormatter())
            return syslog_handler
        else:
            log.error('syslog_address is not in correct format "host:port": %s' % syslog_address)
    else:
        log.info('syslog_address value is not set')


def config_logging(log, syslog_address, correlation_id):
    handler = get_syslog_handler(log, syslog_address, correlation_id)
    if handler:
        log.addHandler(handler)


