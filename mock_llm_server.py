"""Tiny offline OpenAI-compatible mock (for testing the pipeline with zero keys)."""
import json, time
from http.server import BaseHTTPRequestHandler, HTTPServer
class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def do_POST(self):
        body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        prompt=json.dumps(body.get("messages"))
        if "json" in prompt.lower() or body.get("response_format"):
            txt='{"prediction_in_decimal": 0.35}'
        else:
            txt="Mock reasoning: base rates suggest status quo.\nProbability: 35%"
        out={"id":"x","object":"chat.completion","created":int(time.time()),"model":body.get("model"),
             "choices":[{"index":0,"finish_reason":"stop","message":{"role":"assistant","content":txt}}],
             "usage":{"prompt_tokens":1,"completion_tokens":1,"total_tokens":2}}
        b=json.dumps(out).encode();self.send_response(200);self.send_header("Content-Type","application/json");self.end_headers();self.wfile.write(b)
HTTPServer(("127.0.0.1",8765),H).serve_forever()
