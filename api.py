import os
import flask
from flask import jsonify, request
from extractor.main import process_text

# Version of the EcoCor Extractor Service
service_version = "0.0.1"

service_url = str(os.environ.get("SERVICE_URL", "http://localhost"))
"""SERVICE_URL: url where the service can be accessed.
Normally, it's somehow set when running the flask dev server
but it needs to be adapted, when one wants to access the docker container
default is "localhost".
"""

service_port = int(os.environ.get("SERVICE_PORT", 5005))
"""SERVICE_PORT: Port of the running service.
flask's default port would be 5000, because of the AirPlay Reciever Issue, changed it to 5005.
"""

# Debug Mode: Activates the flask Debug Mode
if os.environ.get("SERVICE_DEBUG", "TRUE") == "FALSE":
    debug = False
else:
    debug = True

# Setup of flask API
api = flask.Flask(__name__)
# enable UTF-8 support
api.config["JSON_AS_ASCII"] = False


@api.route("/", methods=["GET"])
def swagger_ui():
    """Displays the OpenAPI Documentation of the API
    TODO: implement
    """
    # return send_from_directory("static/swagger-ui", "index.html")
    return jsonify("OK")


@api.route("/info", methods=["GET"])
def get_info():
    """Information about the API
    ---
    get:
        summary: About the service
        description: Returns information about the API
        operationId: get_info
        responses:
            200:
                description: Information about the API
    """
    response_data = dict(
        name="EcoCor Extractor",
        version=service_version
    )

    return jsonify(response_data)


@api.route("/extract", methods=["POST"])
def extract():
    """Extract word frequencies from segment data based on a wordlist.

    Processes the text with the process_text function of the extractor module.
    """
    result = process_text(request.data)

    return jsonify(result)


# Run the Service:
api.run(debug=debug, host='0.0.0.0', port=service_port)