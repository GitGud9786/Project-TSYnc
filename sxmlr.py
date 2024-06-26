import socket
import errno
import logging
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import time

logger = logging.getLogger('tsync')
logger.setLevel(logging.DEBUG)


def make_safer(fn):
    def wrapped(*args):
        retries = 3
        for attempt in range(retries):
            try:
                result = fn(*args)
                if result is None:
                    result = "Success"
                return result
            except socket.error as e:
                if e.errno in (errno.ECONNREFUSED, errno.EHOSTUNREACH):
                    logger.critical("Connection error while calling RPC function '%s': %s", fn.__name__, str(e))
                    logger.critical("Failed to connect to RPC server at %s:%s (Attempt %d/%d)", args[0], args[1],
                                    attempt + 1, retries)
                    time.sleep(2)  # wait before retrying
                    continue
                else:
                    raise
            except Exception as e:
                logger.error("Unexpected error while calling RPC function '%s': %s", fn.__name__, str(e))
                return None
        return None

    return wrapped


@make_safer
def pull_file(dest_ip, dest_port, filename, source_uname, source_ip):
    connect = xmlrpc.client.ServerProxy(f"http://{dest_ip}:{dest_port}/", allow_none=True)
    logger.info("Logging from pull file of sxmlr on filename %s, source ip : %s, destination ip: %s", filename,
                source_ip, dest_ip)
    return connect.pull_file(filename, source_uname, source_ip)


@make_safer
def req_push_file(dest_ip, dest_port, filename, source_uname, source_ip, source_port):
    connect = xmlrpc.client.ServerProxy(f"http://{dest_ip}:{dest_port}/", allow_none=True)
    return connect.req_push_file(filename, source_uname, source_ip, source_port)


@make_safer
def ack_push_file(dest_ip, dest_port, filename, source_uname, source_ip, source_port):
    connect = xmlrpc.client.ServerProxy(f"http://{dest_ip}:{dest_port}/", allow_none=True)
    return connect.ack_push_file(filename, source_uname, source_ip, source_port)


@make_safer
def mark_presence(dest_ip, dest_port, source_ip, source_port):
    connect = xmlrpc.client.ServerProxy(f"http://{dest_ip}:{dest_port}/", allow_none=True)
    logger.debug("RPC call to mark presence")
    logger.debug("Available methods on RPC server: %s", connect.system.listMethods())
    connect.mark_presence(source_ip, source_port)


@make_safer
def get_client_public_key(dest_ip, dest_port):
    connect = xmlrpc.client.ServerProxy(f"http://{dest_ip}:{dest_port}/", allow_none=True)
    return connect.get_public_key()


@make_safer
def find_available(dest_ip, dest_port):
    connect = xmlrpc.client.ServerProxy(f"http://{dest_ip}:{dest_port}/", allow_none=True)
    try:
        connect.system.listMethods()
        return True
    except socket.error as e:
        if e.errno in (errno.ECONNREFUSED, errno.EHOSTUNREACH):
            return False
        else:
            raise
