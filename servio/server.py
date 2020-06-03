import mimetypes
import os
import socket
import typing

from .request import Request, iter_lines
from .response import Response
from .serve_file import serve_file


class HTTPServer:
    def __init__(self, host="127.0.0.1", port=9000) -> None:
        self.host = host
        self.port = port

    def serve_forever(self) -> None:
        with socket.socket() as server_socket:
            # tell the kernel to reuse sockets that are in `TIME_WAIT` state
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))

            # 0 is the number of pending connections the socket may have before
            # new connections are refused. Since this server is going to process
            # one connection at a time, we want to refuse any additional connections
            server_socket.listen(0)
            print(f"Listening on {self.host}:{self.port}...")

            while True:
                client_sock, client_addr = server_socket.accept()
                print(f"New connection from {client_addr}")
                self.handle_client(client_sock, client_addr)

    def handle_client(
        self, client_sock: socket.socket, client_addr: typing.Tuple[str, int]
    ) -> None:
        with client_sock:
            # try:
            request = Request.from_socket(client_sock)
            if "100-continue" in request.headers.get("expect", ""):
                client_sock.sendall(b"HTTP/1.1 100 Continue\r\n\r\n")

            try:
                content_length = int(request.headers.get("content-length", "0"))
            except ValueError:
                content_length = 0

            if content_length:
                body = request.body.read(content_length)
                print("Request body", body)

            if request.method != "GET":
                response = Response(
                    status="405 Method Not Allowed", content="Method Not Allowed"
                )
                response.send(client_sock)
                return

            serve_file(client_sock, request.path)
            # except Exception as e:
            # print(f"Failed to parse request: {e}")
            # response = Response(status="400 Bad Request", content="Bad Request")
            # response.send(client_sock)

