# -*- coding: utf-8 -*-

import errno

import os
import hashlib
import requests
from contextlib import contextmanager
from datetime import datetime
from http.client import HTTPException
from urllib.request import FancyURLopener
from urllib.error import URLError

from requests.packages.urllib3.exceptions import InsecureRequestWarning, \
    InsecurePlatformWarning, SNIMissingWarning

from ucs_sweeper.core.errors import FlowInterrupt

_ASSETS_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            '..', 'examples/assets')


def mkdir_p(path):
    """Create directory tree. Like 'mkdir -p'"""
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class URLopener(FancyURLopener):
    def __init__(self, *args, **kwargs):
        super(URLopener, self).__init__(*args, **kwargs)

    def http_error_default(self, url, fp, errcode, errmsg, headers):
        raise IOError('{}: {}'.format(errmsg, url))

    def http_error_308(self, url, fp, errcode, errmsg, headers, data=None):
        """Error 308 -- relocated, but turn POST into error."""
        if data is None:
            return self.http_error_302(url, fp, errcode, errmsg, headers, data)
        else:
            return self.http_error_default(url, fp, errcode, errmsg, headers)


def get_file(url, local_fn, retry=5):
    """Gets file by its url."""
    while retry:
        try:
            opener = URLopener()
            return opener.retrieve(url=url, filename=local_fn)[0]
        except (URLError, HTTPException):
            retry -= 1
        raise FlowInterrupt("Unable to download file {}".format(url.split("?")[0]))  # remove key to service ucs-storage


def get_datetime_string():
    return datetime.now().strftime("%y%m%d%H%M%S")


def getattr_r(o, attribute):
    """Gets last attribute in the ``attribute`` chain of the object ``o``,
    ex for: foo.bar.the_attr it returns the_attr
    :type o: object
    :type attribute: basestring
    """
    chain = attribute.split('.')
    for attr in chain:
        o = getattr(o, attr)
    return o


def disable_ssl_warnings(func):
    """ Decorator disabling urllib3 insecurity warnings """
    def wrapper(*args, **kwargs):
        old_filters = requests.packages.urllib3.warnings.filters
        requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        requests.packages.urllib3.disable_warnings(SNIMissingWarning)

        try:
            return func(*args, **kwargs)
        finally:
            requests.packages.urllib3.warnings.filters = old_filters

    return wrapper


def get_assets_root():
    return _ASSETS_ROOT


def get_ctime(filename):
    return datetime.fromtimestamp(os.path.getctime(filename))


def sha256sum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()


@contextmanager
def nullcontext():
    yield
