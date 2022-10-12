# -*- coding: utf-8 -*-

from os import path
from tempfile import mkdtemp

from ucs_sweeper.core.helpers import get_datetime_string
from ucs_sweeper.core.helpers import mkdir_p

_RESULT_FILES_DIR = None


def get_root():
    global _RESULT_FILES_DIR
    if not _RESULT_FILES_DIR:
        _RESULT_FILES_DIR = mkdtemp(prefix='calypso_results_{}_'.format(
            get_datetime_string()))

    return _RESULT_FILES_DIR


def get_plugin_dir(plugin):
    """
    :type plugin: calypso.plugins.plugin.Plugin
    :return: Plugin's dedicated directory for storing result files.
    :rtype: basestring
    """
    output_dir = path.join(get_root(), 'plugins',
                           plugin.__class__.__name__)
    mkdir_p(output_dir)
    return output_dir


def get_log_filename(suffix='main'):
    return path.join(get_root(), 'calypso_{}.log'.format(suffix))


def get_plugin_log_filename(plugin_name):
    plugin_log_dir = path.join(get_root(), 'plugins')
    mkdir_p(plugin_log_dir)
    return path.join(plugin_log_dir, '{}.log'.format(plugin_name))


def cleanup():
    global _RESULT_FILES_DIR
    _RESULT_FILES_DIR = None
