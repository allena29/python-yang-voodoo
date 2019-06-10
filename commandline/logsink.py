import logging
import socket
import time


class LogWrap():

    ENABLED_INFO = True
    ENABLED_DEBUG = True

    REMOTE_LOG_IP = "127.0.0.1"
    REMOTE_LOG_PORT = 6666

    def __init__(self, component, enable_terminal=False, enable_remote=True):
        format = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=999, format=format)
        self.ENABLED = enable_terminal
        if self.ENABLED:
            self.log = logging.getLogger(component)
            self.log.setLevel(logging.DEBUG)
        self.ENABLED_REMOTE = enable_remote

        if self.ENABLED_REMOTE:
            self.log_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    @staticmethod
    def _args_wildcard_to_printf(*args):
        if isinstance(args, tuple):
            # (('Using cli startup to do %s', 'O:configure'),)
            args = list(args[0])
            if len(args) == 0:
                return ''
            message = args.pop(0)
            if len(args) == 0:
                pass
            if len(args) == 1:
                message = message % (args[0])
            else:
                message = message % tuple(args)
        else:
            message = args
        return (message)

    def _pad_truncate_to_size(self, message, size=1024):
        if len(message) < size:
            message = message + ' '*(1024-len(message))
        elif len(message) > 1024:
            message = message[:1024]
        return message.encode()

    def info(self, *args):
        if self.ENABLED and self.ENABLED_INFO:
            self.log.info(args)
        if self.ENABLED_REMOTE and self.ENABLED_INFO:
            message = 'INFO ' + LogWrap._args_wildcard_to_printf(args)
            message = self._pad_truncate_to_size('INFO: %s %s' % (str(time.time()), message))
            self.log_socket.sendto(message, (self.REMOTE_LOG_IP, self.REMOTE_LOG_PORT))

    def error(self, *args):
        if self.ENABLED:
            self.log.error(args)
        if self.ENABLED_REMOTE:
            message = 'INFO ' + LogWrap._args_wildcard_to_printf(args)
            message = self._pad_truncate_to_size('INFO: %s %s' % (str(time.time()), message))
            self.log_socket.sendto(message, (self.REMOTE_LOG_IP, self.REMOTE_LOG_PORT))

    def debug(self, *args):
        if self.ENABLED and self.ENABLED_DEBUG:
            self.log.debug(args)

        if self.ENABLED_REMOTE and self.ENABLED_DEBUG:
            message = 'DEBUG ' + LogWrap._args_wildcard_to_printf(args)
            message = self._pad_truncate_to_size('INFO: %s %s' % (str(time.time()), message))


if __name__ == '__main__':

    IP = '127.0.0.1'
    PORT = 6666
    print('Listening for logs')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((IP, PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        print(str(data[:200]).rstrip())
        time.sleep(0.015)
