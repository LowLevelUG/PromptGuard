from flask import Flask, redirect
from flasgger.base import Swagger
from utils.enums import SwaggerDocs
from utils.openapi import config
from dotenv.main import find_dotenv, load_dotenv
from sys import argv

# Looks for the .env file and loads it
load_dotenv(find_dotenv())

app: Flask = Flask(__name__)

# Use latest OpenApi specifications
app.config['SWAGGER'] = Swagger.DEFAULT_CONFIG
app.config['SWAGGER']['openapi'] = SwaggerDocs.OPENAPI_VERSION.value
app.config['SWAGGER']['title'] = SwaggerDocs.TITLE.value

# Initialize Swagger
Swagger(app=app, template=config)

# Import blueprints
from blueprints.register import register_bp, register_limiter
from blueprints.validate import validate_bp, validate_limiter
from blueprints.revoke import revoke_bp
from blueprints.ask import ask_bp, ask_limiter

# Register blueprints with the app
app.register_blueprint(register_bp)
app.register_blueprint(validate_bp)
app.register_blueprint(revoke_bp)
app.register_blueprint(ask_bp)

register_limiter.init_app(app)
validate_limiter.init_app(app)
ask_limiter.init_app(app)

# Reroute to Swagger docs
@app.route('/')
def root():
    return redirect(SwaggerDocs.ROUTE.value)


if __name__ == '__main__':
    if len(argv) > 1:
        app.run(host='0.0.0.0', port=80)
    else:
        app.run()
