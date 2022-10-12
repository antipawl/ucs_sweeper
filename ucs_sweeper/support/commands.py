
import re
from collections import namedtuple
from subprocess import Popen, PIPE, TimeoutExpired

from ucs_sweeper.core.errors import default_error, CommandTimeoutError


SSH_CMD = ("ssh -q -n -o StrictHostKeyChecking=no -o CheckHostIP=no "
           "-o UserKnownHostsFile=/dev/null -o ConnectionAttempts=15 ")
ANSI_ESCAPE = re.compile(r"(\x1b\[|\x9b)[0-?]*[ -\/]*[@-~]|\x0f", re.I)

EXPIRED_TIME = -1

RunCmdResult = namedtuple('RunCmdResult', ['rc', 'stdout', 'stderr'])


def runcmd(cmd, raise_err=False, log=None, timeout=None):
    """Run given command.

    Return tuple of (RC, stdout, stderr)."""
    execprocess = Popen(cmd,
                        stdout=PIPE,
                        stderr=PIPE,
                        shell=True)

    returncode = None
    stdout = None
    stderr = None
    try:
        (stdout, stderr) = execprocess.communicate(timeout=timeout)
        returncode = execprocess.returncode

        stdout = ANSI_ESCAPE.sub('', stdout.decode('utf-8'))
        stderr = ANSI_ESCAPE.sub('', stderr.decode('utf-8'))

        # Start from new line for easy reading of the log output:
        title, msg = _format_output(cmd, returncode, stdout, stderr)

        if raise_err and returncode:
            err = "Command failed: {}".format('\n{}\n{}'.format(title, msg))
            raise default_error(raise_err)(err)

        if log:
            log(f"{title}\n{msg}")

    except TimeoutExpired:
        if raise_err:
            err = "Command failed to complete within %ds" % timeout
            raise default_error(raise_err, CommandTimeoutError)(err)
        return None, None
    finally:
        return RunCmdResult(rc=returncode, stdout=stdout, stderr=stderr)


def runcmd_ssh(address, cmd, username='root', log=None, raise_err=False,
               delim='"', escape_double_quotes=True,
               verbose=True, force_tty=False, extra_opts='', timeout=None):
    """Run command via ssh given username and remote address.
    Escaping double quotes works only if the delimiter is set to '"'

    Return tuple of (RC, stdout, stderr)."""
    sshcmd = SSH_CMD
    if force_tty:
        # Force pseudo-tty allocation:
        sshcmd += "-tt "
    sshcmd += extra_opts

    if delim == '"' and escape_double_quotes:
        cmd = cmd.replace('"', r'\"')

    cmd = '%s@%s %s%s%s' % (username, address, delim, cmd, delim)
    if log:
        log("Running ssh command: " + cmd)

    return runcmd(
        "{} {}".format(sshcmd, cmd), raise_err, log if verbose else None, timeout)


def scp_file(file_name, dest_name, dest_addr, time_secs=30,
             username='root', log=None, raise_err=False):

    cmd = 'scp -o StrictHostKeyChecking=no -o CheckHostIP=no " \
           "-o UserKnownHostsFile=/dev/null -o ConnectionAttempts=15 %s %s@%s:%s' %\
          (file_name, username, dest_addr, dest_name)
    rc, stdout, stderr = runcmd(
        cmd, raise_err=raise_err, timeout=time_secs, log=log)

    if raise_err and (rc != 0 or any(stderr)):
        err = ['SCP copy error (RC %s) for cmd: %s' % (rc, cmd),
               'STDOUT: %s' % "".join(stdout),
               'STDERR: %s' % "".join(stderr)]
        raise default_error(raise_err)('\n'.join(err))

    return RunCmdResult(rc=rc, stdout=stdout, stderr=stderr)


def scp_file_from(file_name, dest_addr, local_name, time_secs=30,
                  username='root', log=None, raise_err=False):

    cmd = 'scp %s@%s:%s %s' % (username, dest_addr, file_name, local_name)
    rc, stdout, stderr = runcmd(
        cmd, raise_err=raise_err, timeout=time_secs)

    if raise_err and (rc != 0 or any(stderr)):
        err = ['SCP copy error (RC %s) for cmd: %s' % (rc, cmd),
               'STDOUT: %s' % "".join(stdout),
               'STDERR: %s' % "".join(stderr)]
        raise default_error(raise_err)('\n'.join(err))

    return RunCmdResult(rc=rc, stdout=stdout, stderr=stderr)


def _format_output(cmd, rc, stdout, stderr):
    title = 'RUN: {}'.format(cmd).replace(SSH_CMD, "ssh")
    msg = 'OUT: {}\nERR: {}\nRC={}'.format(stdout, stderr, rc)\
          .replace(SSH_CMD, "ssh")
    return title, msg
