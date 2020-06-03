import io
import os
import socket
import typing

from .headers import Headers


class Response:
    """
    A HTTP Response

    Parameters:
        status: The response status line (e.g. "200 OK").
        headers: The response headers.
        body: A file containing the response body.
        content: A string representing the response body. If this is
          provided, then body is ignored.
        encoding: An encoding for the content, if provided.
    """

    def __init__(
        self,
        status: str,
        headers: typing.Optional[Headers] = None,
        body: typing.Optional[typing.IO] = None,
        content: typing.Optional[str] = None,
        encoding: str = "utf-8",
    ) -> None:
        self.status = status.encode()
        self.headers = headers or Headers()
        self.body = body
        self.content = content

        if content is not None:
            self.body = io.BytesIO(content.encode(encoding))
        elif body is None:
            self.body = io.BytesIO()
        else:
            self.body = body

    def send(self, sock: socket.socket) -> None:
        """
        Write this response to a socket.
        """
        _content_length = self.headers.get("content-length")
        if _content_length is None:
            try:
                body_stat = os.fstat(self.body.fileno())
                content_length = body_stat.st_size
                print("Content-length: ", content_length)
            except OSError:
                self.body.seek(0, os.SEEK_END)
                content_length = self.body.tell()
                self.body.seek(0, os.SEEK_SET)

            if content_length > 0:
                self.headers.add("content-length", _content_length)

        headers = b"HTTP/1.1 " + self.status + b"\r\n"
        for header_name, header_value in self.headers:
            headers += f"{header_name}: {header_value}\r\n".encode()

        sock.sendall(headers + b"\r\n")
        if _content_length:
            # Socket's sendfile figures out whether the parameter is a regular file
            # or not. If it is a regular file, then it uses the high-performance
            # sendfile system call to write the file to the socket. Else, it falls
            # back to regular send calls.
            sock.sendfile(self.body)
