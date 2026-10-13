"""Start and stop an OBS recording from the command line."""

import base64
import hashlib
import json
import os
import socket
import struct
import subprocess
import sys
import time
from pathlib import Path

CONFIG_PATH = Path.home() / (
    "Library/Application Support/obs-studio/plugin_config/obs-websocket/config.json"
)
OBS_APP = "OBS"


def obs_running():
    result = subprocess.run(["pgrep", "-x", OBS_APP], capture_output=True)
    return result.returncode == 0


def load_config():
    if not CONFIG_PATH.is_file():
        raise SystemExit(f"OBS WebSocket settings were not found at {CONFIG_PATH}")
    with CONFIG_PATH.open(encoding="utf-8") as handle:
        config = json.load(handle)
    if not config.get("server_enabled"):
        raise SystemExit(
            "OBS WebSocket is turned off. In OBS, open Tools → WebSocket Server "
            "Settings, enable the server, then quit OBS and run this command again."
        )
    return config


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("OBS closed the WebSocket")
        data += chunk
    return data


def send_frame(sock, opcode, payload):
    mask = os.urandom(4)
    masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
    header = bytearray([0x80 | opcode])
    length = len(payload)
    if length < 126:
        header.append(0x80 | length)
    elif length < 65536:
        header.append(0x80 | 126)
        header.extend(struct.pack(">H", length))
    else:
        header.append(0x80 | 127)
        header.extend(struct.pack(">Q", length))
    sock.sendall(header + mask + masked)


def send_json(sock, message):
    send_frame(sock, 0x1, json.dumps(message).encode())


def recv_json(sock):
    while True:
        first, second = recv_exact(sock, 2)
        opcode = first & 0x0F
        length = second & 0x7F
        if length == 126:
            length = struct.unpack(">H", recv_exact(sock, 2))[0]
        elif length == 127:
            length = struct.unpack(">Q", recv_exact(sock, 8))[0]
        if second & 0x80:
            mask = recv_exact(sock, 4)
            payload = bytes(
                byte ^ mask[index % 4]
                for index, byte in enumerate(recv_exact(sock, length))
            )
        else:
            payload = recv_exact(sock, length)
        if opcode == 0x9:
            send_frame(sock, 0xA, payload)
            continue
        if opcode == 0x8:
            raise ConnectionError("OBS closed the WebSocket")
        if opcode == 0x1:
            return json.loads(payload)


def connect(port, password):
    sock = socket.create_connection(("127.0.0.1", port), timeout=5)
    sock.settimeout(120)
    key = base64.b64encode(os.urandom(16)).decode()
    request = (
        f"GET / HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        "\r\n"
    )
    sock.sendall(request.encode())
    response = b""
    while b"\r\n\r\n" not in response:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("OBS closed the WebSocket during the handshake")
        response += chunk
    if b" 101 " not in response.split(b"\r\n", 1)[0]:
        raise ConnectionError("OBS did not accept the WebSocket connection")

    hello = recv_json(sock)
    if hello.get("op") != 0:
        raise ConnectionError(f"Unexpected greeting from OBS: {hello}")
    identify = {"op": 1, "d": {"rpcVersion": 1, "eventSubscriptions": 0}}
    authentication = hello["d"].get("authentication")
    if authentication:
        secret = base64.b64encode(
            hashlib.sha256((password + authentication["salt"]).encode()).digest()
        ).decode()
        identify["d"]["authentication"] = base64.b64encode(
            hashlib.sha256((secret + authentication["challenge"]).encode()).digest()
        ).decode()
    send_json(sock, identify)
    identified = recv_json(sock)
    if identified.get("op") != 2:
        raise ConnectionError("OBS rejected the WebSocket login")
    return sock


def request(sock, request_type):
    send_json(
        sock,
        {"op": 6, "d": {"requestType": request_type, "requestId": request_type}},
    )
    while True:
        message = recv_json(sock)
        if message.get("op") == 7 and message["d"].get("requestId") == request_type:
            return message["d"]


def wait_for_socket(port, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False


def recording_active(sock):
    status = request(sock, "GetRecordStatus")
    if not status["requestStatus"]["result"]:
        comment = status["requestStatus"].get("comment", "could not read recording status")
        raise SystemExit(f"OBS error: {comment}")
    return status["responseData"]["outputActive"]


def start_recording():
    config = load_config()
    port = int(config.get("server_port", 4455))
    if not obs_running():
        subprocess.run(
            ["open", "-a", OBS_APP, "--args", "--startrecording"],
            check=True,
        )
        print("Opening OBS and starting the recording...")
        if not wait_for_socket(port, timeout=60):
            raise SystemExit("OBS opened, but the WebSocket server did not start.")
    else:
        print("OBS is already open. Starting the recording...")

    try:
        sock = connect(port, config.get("server_password", ""))
    except (ConnectionError, OSError):
        raise SystemExit(
            "Could not reach OBS. If OBS was already open, quit it and run make record again."
        ) from None
    try:
        if recording_active(sock):
            print("Recording.")
            return
        started = request(sock, "StartRecord")
    finally:
        sock.close()
    if not started["requestStatus"]["result"]:
        comment = started["requestStatus"].get("comment", "could not start recording")
        raise SystemExit(f"OBS error: {comment}")
    print("Recording.")


def stop_and_quit():
    if not obs_running():
        print("OBS is not open.")
        return

    config = load_config()
    port = int(config.get("server_port", 4455))
    try:
        sock = connect(port, config.get("server_password", ""))
    except (ConnectionError, OSError):
        raise SystemExit(
            "Could not reach OBS. Quit OBS, then run make finish again."
        ) from None
    try:
        if recording_active(sock):
            stopped = request(sock, "StopRecord")
            if not stopped["requestStatus"]["result"]:
                comment = stopped["requestStatus"].get("comment", "could not stop recording")
                raise SystemExit(f"OBS error: {comment}")
            print("Recording stopped.")
        else:
            print("OBS was not recording.")
    finally:
        sock.close()

    subprocess.run(["osascript", "-e", f'tell application "{OBS_APP}" to quit'], check=False)
    deadline = time.time() + 20
    while time.time() < deadline and obs_running():
        time.sleep(0.5)
    if obs_running():
        raise SystemExit("The recording was stopped, but OBS is still open.")
    print("OBS closed.")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"record", "finish"}:
        raise SystemExit("Usage: obs_control.py record|finish")
    if sys.argv[1] == "record":
        start_recording()
    else:
        stop_and_quit()


if __name__ == "__main__":
    main()
