import argparse
from servio import HTTPServer


def main():
    """
    Commandline interface
    """
    # Argument parsing
    parser = argparse.ArgumentParser(
        description="A pure python file server with no dependencies.\nDon't use this in production :)"
    )
    parser.add_argument(
        "-b", "--bind", type=str, help="Bind address", default="127.0.0.1"
    )
    parser.add_argument("-p", "--port", type=int, help="Bind port", default=9000)
    parser.add_argument(
        "-w", "--workers", type=int, help="Number of workers", default=4
    )
    parser.add_argument(
        "path", nargs="?", type=str, help="Specify directory to serve", default="./"
    )

    args = parser.parse_args()

    # Starting server
    server = HTTPServer(
        host=args.bind, port=args.port, worker_count=args.workers, root_path=args.path
    )
    server.serve_forever()

