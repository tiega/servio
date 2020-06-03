import mimetypes
import os
import socket
import typing

from .response import Response


SERVER_ROOT = os.path.abspath(".")


def serve_file(sock: socket.socket, path: str) -> None:
    """
    Given a socket and the relative path to a file (relative to SERVER_ROOT),
    send that file to the socket if it exists. If the file doesn't exist,
    send a "404 Not Found" response.
    """
    if path == "/":
        path = "/index.html"

    abspath = os.path.normpath(os.path.join(SERVER_ROOT, path.lstrip("/")))
    if not abspath.startswith(SERVER_ROOT):
        response = Response(status="404 Not Found", content="Not Found")
        response.send(sock)
        return

    try:
        with open(abspath, "rb") as f:
            content_type, encoding = mimetypes.guess_type(abspath)
            if content_type is None:
                content_type = "application/octet-stream"

            if encoding is not None:
                content_type += f"; charset={encoding}"

            stat = os.fstat(f.fileno())

            response = Response(status="200 OK", body=f)
            response.headers.add("content-type", content_type)
            response.headers.add("content-length", str(stat.st_size))
            response.send(sock)
            return
    except FileNotFoundError:
        response = Response(status="404 Not Found", content="Not Found")
        response.send(sock)
        return

