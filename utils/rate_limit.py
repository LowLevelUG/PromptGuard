from flask import jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def init_limiter(app):

    limiter = Limiter(
      get_remote_address,
      storage_uri="redis://localhost:6379",
      storage_options={"socket_connect_timeout": 30},
      strategy="fixed-window",
    )

    @app.errorhandler(429)
    def ratelimit_error(e):
        return jsonify(
            error="Rate limit exceeded",
            message="You have hit the request limit. Please try again later."
        ), 429

    return limiter

