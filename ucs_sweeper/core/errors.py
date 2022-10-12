# -*- coding: utf-8 -*-


class CalypsoError(Exception):
    def __init__(self, message):
        self.message = message


class AuthenticationError(CalypsoError):
    pass


class SetupError(CalypsoError):
    pass


class UcsLoadOnly(CalypsoError):
    pass


class FlowInterrupt(CalypsoError):
    pass


class HaError(FlowInterrupt):
    pass


class InvalidConfiguration(CalypsoError):
    pass


class InstallFail(CalypsoError):
    def __init__(self, *args, **kwargs):
        self.ip = kwargs.pop('ip', None)
        super().__init__(args)


class InstallTimeoutFail(InstallFail):
    pass


class PluginResult(CalypsoError):
    result = None

    def __init__(self, *args, **kwargs):
        """Do not use it directly from Plugins. Use the heirs."""
        self.ip = kwargs.pop('ip', None)
        self.message = args[0] if args else None
        super().__init__(args)


class PluginError(PluginResult):
    result = 'ERROR'


class PluginFail(PluginResult):
    result = 'FAIL'


class PluginWarn(PluginResult):
    result = 'WARN'


class PluginPass(PluginResult):
    result = 'PASS'


class PluginInfo(PluginResult):
    result = "INFO"


class CommandError(CalypsoError):
    pass


class CommandTimeoutError(CommandError):
    pass


class ConnectionError(CalypsoError):
    pass


class TimeoutError(ConnectionError):
    pass


class ConnectionRefused(ConnectionError):
    pass


class PersistenceBroken(ConnectionError):
    pass


def default_error(err, default=CommandError):
    """If `err' is subclass of Exception return `err' else return `default'
    """
    if isinstance(err, type) and issubclass(err, Exception):
        return err
    return default
