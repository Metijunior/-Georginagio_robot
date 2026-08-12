from http.server import HTTPServer, BaseHTTPRequestHandler
import threading


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/health":
            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )
            self.end_headers()

            self.wfile.write(
                b"OK"
            )

            return


        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8"
        )
        self.end_headers()

        self.wfile.write(
            b"Bot is running"
        )


    def log_message(self, format, *args):
        return


def run_server():

    server = HTTPServer(
        ("0.0.0.0", 10000),
        Handler
    )

    server.serve_forever()


def start_server():

    thread = threading.Thread(
        target=run_server,
        daemon=True
    )

    thread.start()
