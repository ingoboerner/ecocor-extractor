from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
import json

from api import service_version, service_url, service_port, api, get_info, extract


spec = APISpec(
    title="EcoCor Extractor",
    version=service_version,
    openapi_version="3.0.3",
    info=dict(
        description="""This service extracts frequencies of words from a given word list in
            text segments. As input a JSON object is passed over an API which saves the text segment
            and their IDs and optionally a URL to the word list on which basis the frequencies are
            extracted. It returns a JSON in which for each word the frequency per text segment is
            saved.""",
        contact=dict(
            name="DH Network at University of Potsdam",
            email="trilcke@uni-potsdam.de"
        ),
        license=dict(
            name="GPL-3.0 license",
            url="https://www.gnu.org/licenses/gpl-3.0.html"
        )
    ),
    servers=[
        dict(
            description="Local Flask",
            url="http://localhost:5005"
        )
    ],
    externalDocs=dict(
        description="Code on Github",
        url="https://github.com/dh-network/ecocor-extractor"
    ),
    plugins=[FlaskPlugin(), MarshmallowPlugin()]
)

# Generate the OpenAPI Specification
with api.test_request_context():
    spec.path(view=get_info)
    spec.path(view=extract)


# write the OpenAPI Specification as YAML to the root folder
with open('openapi.yaml', 'w') as f:
    f.write(spec.to_yaml())

# Write the Specification to the /static folder to use in the Swagger UI
with open('static/swagger-ui/openapi.json', 'w') as f:
    json.dump(spec.to_dict(), f)



