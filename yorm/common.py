"""Common exceptions, classes, and functions."""

import os
import shutil
import logging

import yaml

verbosity = 0  # global verbosity setting for controlling string formatting
PRINT_VERBOSITY = 0  # minimum verbosity to using `print`
STR_VERBOSITY = 3  # minimum verbosity to use verbose `__str__`
MAX_VERBOSITY = 4  # maximum verbosity level implemented


def _trace(self, message, *args, **kws):  # pragma: no cover (manual test)
    """Handler for a new TRACE logging level."""
    if self.isEnabledFor(logging.DEBUG - 1):
        self._log(logging.DEBUG - 1, message, args, **kws)  # pylint: disable=W0212


logging.addLevelName(logging.DEBUG - 1, "TRACE")
logging.Logger.trace = _trace

logger = logging.getLogger
log = logger(__name__)


# exception classes ##########################################################


class YORMException(Exception):

    """Base class for all YORM exceptions."""

    pass


class FileError(YORMException, FileNotFoundError):

    """Raised when text cannot be read from a file."""

    pass


class ContentError(YORMException, yaml.error.YAMLError, ValueError):

    """Raised when YAML cannot be parsed from text."""

    pass


class ConversionError(YORMException, ValueError):

    """Raised when a value cannot be converted to the specified type."""

    pass


# decorators #################################################################


class classproperty(object):

    """Read-only class property decorator."""

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


# disk helper functions ######################################################


def create_dirname(path):
    """Ensure a parent directory exists for a path."""
    dirpath = os.path.dirname(path)
    if dirpath and not os.path.isdir(dirpath):
        log.trace("creating directory {}...".format(dirpath))
        os.makedirs(dirpath)


def read_text(path, encoding='utf-8'):
    """Read text from a file.

    :param path: file path to read from
    :param encoding: input file encoding

    :return: string

    """
    log.trace("reading text from '{}'...".format(path))
    with open(path, 'r', encoding=encoding) as stream:
        text = stream.read()
    return text


def load_yaml(text, path):
    """Parse a dictionary from YAML text.

    :param text: string containing dumped YAML data
    :param path: file path for error messages

    :return: dictionary

    """
    # Load the YAML data
    try:
        data = yaml.load(text) or {}
    except yaml.error.YAMLError as exc:
        msg = "invalid contents: {}:\n{}".format(path, exc)
        raise ContentError(msg) from None
    # Ensure data is a dictionary
    if not isinstance(data, dict):
        msg = "invalid contents: {}".format(path)
        raise ContentError(msg)
    # Return the parsed data
    return data


def write_text(text, path, encoding='utf-8'):
    """Write text to a file.

    :param text: string
    :param path: file to write text
    :param encoding: output file encoding

    :return: path of new file

    """
    if text:
        log.trace("writing text to '{}'...".format(path))
    with open(path, 'wb') as stream:
        data = text.encode(encoding)
        stream.write(data)
    return path


def touch(path):
    """Ensure a file exists."""
    if not os.path.exists(path):
        log.trace("creating empty '{}'...".format(path))
        write_text('', path)


def delete(path):
    """Delete a file or directory with error handling."""
    # TODO: determine if directory deletion should be part of this library
    if os.path.isdir(path):  # pragma: no cover (unused)
        try:
            log.trace("deleting '{}'...".format(path))
            shutil.rmtree(path)
        except IOError:
            # bug: http://code.activestate.com/lists/python-list/159050
            msg = "unable to delete: {}".format(path)
            log.warning(msg)
    elif os.path.isfile(path):
        log.trace("deleting '{}'...".format(path))
        os.remove(path)
