import aspectlib
import ctypes
import hashlib
import logging
import paramiko
import sys
import time

(
    HANDLE_ASPECT,
    SEND_KEX_INIT_ASPECT,
    READ_MESSAGE_ASPECT,
    CONSTANT_TIME_BYTES_EQ_ASPECT,
    CONNECT_ASPECT,
    PARSE_NEWKEYS_ASPECT,
    VERIFY_SIG_SSH_ASPECT,
    CHECK_BANNER_ASPECT,
    BUILD_PACKET_ASPECT,
    PARSE_KEXDH_REPLY_ASPECT,
    SEND_MESSAGE_ASPECT,
    WRITE_ALL_ASPECT,
    READLINE_ASPECT,
    ACTIVATE_OUTBOUND_ASPECT,
    COMPUTE_KEY_ASPECT,
) = range(0, 15)

SAMPLING_RATE_TABLE = {
    BUILD_PACKET_ASPECT: 0.2
}

ASPECT_TABLE = {}

trace = []

def add_event(when, what, scope, watch = {}, func_args = [], func_kwargs = {}):
    global trace

    trace.append(
        {
            "id": len(trace),
            "timestamp": int(time.time()),
            "when": when,
            "what": what,
            "scope": scope,
            "watch": watch,
            "func_args": func_args,
            "func_kwargs": func_kwargs,
        }
    )

# Using the hashlib implementation of hash function to not put more load on the
# SEcube device, which is already a bottle neck in this setup.
def compute_key(K, H, session_id, id, nbytes):
    m = paramiko.message.Message()
    m.add_mpint(K)
    m.add_bytes(H)
    m.add_byte(id.encode())
    m.add_bytes(session_id)

    out = hashlib.sha256(m.asbytes()).digest()
    while len(out) < nbytes:
        m = paramiko.message.Message()
        m.add_mpint(K)
        m.add_bytes(H)
        m.add_bytes(out)

        out += hashlib.sha256(m.asbytes()).digest()
    return out[:nbytes]

@aspectlib.Aspect
def handle_aspect(*args):
    if args[1].levelname != "ERROR":
        add_event("BEFORE", "handle", "logging.Handler")
    yield

@aspectlib.Aspect
def _send_kex_init_aspect(*args):
    add_event("BEFORE", "_send_kex_init", "paramiko.transport.Transport",
        watch={"preferred_ciphers": args[0].preferred_ciphers})
    yield

@aspectlib.Aspect
def send_message_aspect(*args):
    command_id = paramiko.py3compat.byte_ord(
        paramiko.common.asbytes(args[1])[0])
    add_event("BEFORE", "send_message", "paramiko.Packetizer", {
        "command_id": command_id,
        "sent_bytes": args[0]._Packetizer__sent_bytes,
        "sent_packets": args[0]._Packetizer__sent_packets,
    })
    yield

@aspectlib.Aspect
def read_message_aspect(*args):
    add_event("BEFORE", "read_message", "paramiko.Packetizer", watch = {
        "mac_engine_set": args[0]._Packetizer__mac_size_in > 0,
        "received_bytes": args[0]._Packetizer__received_bytes,
        "received_packets": args[0]._Packetizer__received_packets
    })
    command_id = None
    try:
        command_id, _ = yield
    except Exception as e:
        add_event(type(e).__name__, "read_message", "paramiko.Packetizer")
        raise
    finally:
        add_event("AFTER", "read_message", "paramiko.Packetizer", watch = {
            "command_id": command_id
        })

@aspectlib.Aspect
def constant_time_bytes_eq_aspect(*args):
    add_event("BEFORE", "constant_time_bytes_eq", "paramiko.util")
    yield

@aspectlib.Aspect
def connect_aspect(*args, **kwargs):
    add_event("BEFORE", "connect", "paramiko.SSHClient", watch = {
        "host_in_system_host_keys": \
            args[0]._system_host_keys.get(args[1]) is not None,
        "host_in_host_keys": args[0]._host_keys.get(args[1]) is not None,
    })
    try:
        yield
    except Exception as e:
        add_event(type(e).__name__, "connect", "paramiko.SSHClient")
        raise
    finally:
        add_event("AFTER", "connect", "paramiko.SSHClient")

@aspectlib.Aspect
def _parse_newkeys_aspect(*args):
    size = sys.getsizeof(args[0].kex_engine.x)
    address = id(args[0].kex_engine.x)

    bytes_before = (size * ctypes.c_uint8).from_address(address)
    engine_before = args[0].packetizer._Packetizer__block_engine_in
    mac_key_before = args[0].packetizer._Packetizer__mac_key_in
    try:
        yield
    finally:
        bytes_after = (size * ctypes.c_uint8).from_address(address)
        engine_after = args[0].packetizer._Packetizer__block_engine_in
        mac_key_after = args[0].packetizer._Packetizer__mac_key_in
        add_event("AFTER", "_parse_newkeys", "paramiko.Transport", watch = {
            "bytes_equal": \
                all(x == y for x, y in zip(bytes_before, bytes_after)),
            "engine_changed": engine_before != engine_after,
            "mac_key_changed": mac_key_before != mac_key_after
        })

@aspectlib.Aspect
def verify_ssh_sig_aspect(*args):
    add_event("BEFORE", "verify_ssh_sig_aspect", "paramiko.ECDSAKey")
    yield

@aspectlib.Aspect
def _check_banner_aspect(*args):
    try:
        yield
    except Exception as e:
        add_event(type(e).__name__, "_check_banner", "paramiko.Transport")
        raise

@aspectlib.Aspect
def _build_packet_aspect(*args):
    packet_length = None
    padding_length = None
    try:
        packet = yield
        packet_length = len(packet)
        padding_length = packet[4]
    finally:
        add_event("AFTER", "_build_packet", "paramiko.Packetizer", watch = {
            "packet_length": packet_length,
            "padding_length": padding_length
        })

@aspectlib.Aspect
def _parse_kexdh_reply_aspect(*args):
    add_event("BEFORE", "_parse_kexdh_reply",
        "paramiko.kex_group14.KexGroup14")
    try:
        yield
    finally:
        add_event("AFTER", "_parse_kexdh_reply",
            "paramiko.kex_group14.KexGroup14")

@aspectlib.Aspect
def write_all_aspect(*args):
    # If the identification string has been sent to the SSH server, we can stop
    # instrumenting this function
    if b"SSH-" in args[1]:
        add_event("BEFORE", "write_all", "paramiko.Packetizer", watch = {
            "message": args[1].decode()
        })
        ASPECT_TABLE[WRITE_ALL_ASPECT].rollback()
    yield

@aspectlib.Aspect
def readline_aspect(*args):
    line = yield

    # If the identification string has been received, we can stop instrumenting
    # this function
    if "SSH-" in line:
        add_event("AFTER", "readline", "paramiko.Packetizer", watch = {
            "message": line
        })
        ASPECT_TABLE[READLINE_ASPECT].rollback()

@aspectlib.Aspect
def _activate_outbound_aspect(*args):
    engine_before = args[0].packetizer._Packetizer__block_engine_out
    mac_key_before = args[0].packetizer._Packetizer__mac_key_out
    try:
        yield
    finally:
        engine_after = args[0].packetizer._Packetizer__block_engine_out
        mac_key_after = args[0].packetizer._Packetizer__mac_key_out
        add_event("AFTER", "_activate_outbound", "paramiko.Transport", watch = {
            "engine_changed": engine_before != engine_after,
            "mac_key_changed": mac_key_before != mac_key_after
        })

@aspectlib.Aspect
def _compute_key_aspect(*args):
    our_key = compute_key(args[0].K, args[0].H, args[0].session_id,
                      args[1], args[2])
    paramiko_key = yield
    add_event("AFTER", "_compute_key", "paramiko.Transport", watch = {
        "key_match": all(x == y for x, y in zip(our_key, paramiko_key)),
    })

def weave():
    ASPECT_TABLE[HANDLE_ASPECT] = aspectlib.weave(
        logging.Handler.handle, handle_aspect)

    ASPECT_TABLE[SEND_KEX_INIT_ASPECT] = aspectlib.weave(
        paramiko.transport.Transport._send_kex_init, _send_kex_init_aspect)

    ASPECT_TABLE[SEND_MESSAGE_ASPECT] = aspectlib.weave(
        paramiko.Packetizer.send_message, send_message_aspect)

    ASPECT_TABLE[READ_MESSAGE_ASPECT] = aspectlib.weave(
        paramiko.Packetizer.read_message, read_message_aspect)

    ASPECT_TABLE[CONSTANT_TIME_BYTES_EQ_ASPECT] = aspectlib.weave(
        paramiko.util.constant_time_bytes_eq, constant_time_bytes_eq_aspect)

    ASPECT_TABLE[CONNECT_ASPECT] = aspectlib.weave(
        paramiko.SSHClient.connect, connect_aspect)

    # ASPECT_TABLE[PARSE_NEWKEYS_ASPECT] = aspectlib.weave(
    #     paramiko.Transport._parse_newkeys, _parse_newkeys_aspect)

    ASPECT_TABLE[VERIFY_SIG_SSH_ASPECT] = aspectlib.weave(
        paramiko.ECDSAKey.verify_ssh_sig, verify_ssh_sig_aspect)

    ASPECT_TABLE[CHECK_BANNER_ASPECT] = aspectlib.weave(
        paramiko.Transport._check_banner, _check_banner_aspect)

    ASPECT_TABLE[BUILD_PACKET_ASPECT] = aspectlib.weave(
        paramiko.Packetizer._build_packet, _build_packet_aspect)

    ASPECT_TABLE[PARSE_KEXDH_REPLY_ASPECT] = aspectlib.weave(
        paramiko.kex_group14.KexGroup14._parse_kexdh_reply,
        _parse_kexdh_reply_aspect)

    ASPECT_TABLE[WRITE_ALL_ASPECT] = aspectlib.weave(
        paramiko.Packetizer.write_all, write_all_aspect)

    ASPECT_TABLE[READLINE_ASPECT] = aspectlib.weave(
        paramiko.Packetizer.readline, readline_aspect)

    ASPECT_TABLE[ACTIVATE_OUTBOUND_ASPECT] = aspectlib.weave(
        paramiko.Transport._activate_outbound, _activate_outbound_aspect)

    ASPECT_TABLE[COMPUTE_KEY_ASPECT] = aspectlib.weave(
        paramiko.Transport._compute_key, _compute_key_aspect)

    paramiko.Transport._handler_table[paramiko.common.MSG_NEWKEYS] = \
        paramiko.Transport._parse_newkeys
