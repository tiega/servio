from threading import Thread
import mimetypes
import os
from queue import Queue, Empty
import socket
import typing

from .request import Request, iter_lines
from .response import Response
from .serve_file import serve_file


class HTTPServer:
    def __init__(self, host="127.0.0.1", port=9000, worker_count=16) -> None:
        self.host = host
        self.port = port
        self.worker_count = worker_count
        self.worker_backlog = worker_count * 8
        self.connection_queue: Queue = Queue(self.worker_backlog)

    def serve_forever(self) -> None:
        print(f"Starting {self.worker_count} workers...")
        workers = []
        for _ in range(self.worker_count):
            worker = HTTPWorker(connection_queue=self.connection_queue)
            worker.start()
            workers.append(worker)

        with socket.socket() as server_socket:
            # tell the kernel to reuse sockets that are in `TIME_WAIT` state
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(self.worker_backlog)
            print(f"Listening on {self.host}:{self.port}...")

            while True:
                try:
                    self.connection_queue.put(server_socket.accept())
                except KeyboardInterrupt:
                    break

            print("Shutting down workers...")
            for worker in workers:
                worker.stop()

            print("Bye!")


class HTTPWorker(Thread):
    def __init__(self, connection_queue: Queue) -> None:
        super().__init__(daemon=True)

        self.connection_queue: Queue = connection_queue
        self.running: bool = False

    def stop(self) -> None:
        self.running = False

    def run(self) -> None:
        self.running = True
        while self.running:
            try:
                # Get client sock and addr from queue
                client_sock, client_addr = self.connection_queue.get(timeout=1)
            except Empty:
                continue

            try:
                self.handle_client(client_sock, client_addr)

            except Exception as e:
                print(f"Unhandled error: {e}")
                continue
            finally:
                self.connection_queue.task_done()

    def handle_client(
        self, client_sock: socket.socket, client_addr: typing.Tuple[str, int]
    ) -> None:
        with client_sock:
            try:
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
            except Exception as e:
                print(f"Failed to parse request: {e}")
                response = Response(status="400 Bad Request", content="Bad Request")
                response.send(client_sock)

