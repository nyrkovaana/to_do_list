from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import json

TASKS_FILE = "tasks.txt"


def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f)


def run(handler_class=BaseHTTPRequestHandler):
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, handler_class)
    try:
        print("Server is running...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


class HttpGetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(json.dumps(tasks).encode())

    def do_POST(self):
        if self.path == "/tasks":
            content_length = int(self.headers.get('Content-Length'))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            task = {
                "title": data["title"],
                "priority": data["priority"],
                "isDone": False,
                "id": len(tasks) + 1
            }
            tasks.append(task)
            save_tasks(tasks)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(task).encode())
        elif self.path.startswith("/tasks/") and self.path.endswith("/complete"):
            try:
                task_id = int(self.path.split('/')[2])
                task = next((t for t in tasks if t["id"] == task_id), None)

                if task:
                    task["isDone"] = True
                    save_tasks(tasks)

                    self.send_response(200)
                    self.end_headers()
                else:
                    self.send_response(404)
                    self.end_headers()
            except (ValueError, IndexError):
                self.send_response(404)
                self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()


tasks = load_tasks()
run(handler_class=HttpGetHandler)
