# imports - standard imports
import os

# imports - third-party imports
from flask import request, jsonify
import addict

# imports - module imports
from candis.config              import CONFIG
from candis.util                import (
    assign_if_none, get_rand_uuid_str, get_timestamp_str, merge_dicts
)
from candis.resource            import R
from candis.ios                 import Pipeline
from candis.ios                 import json as JSON
from candis.app.server.app      import app
from candis.app.server.response import Response

# TODO: Create a default handler that accepts JSON serializable data.
# HINT: Can be written better?
@app.route(CONFIG.App.Routes.API.Pipeline.RUN, methods = ['POST'])
def run():
    response       = Response()

    parameters     = addict.Dict(request.get_json())

    if parameters.path and parameters.name and parameters.format:
        relpath    = os.path.join(parameters.path, parameters.name)

        # TODO: Check if file exists, else respond error.
        if parameters.format == 'pipeline':
            try:
                cdat, pipe = Pipeline.load(relpath)
                pipe.run(cdat, save = CONFIG.DEBUG, verbose = CONFIG.DEBUG)

                while pipe.status == Pipeline.RUNNING:
                    JSON.write(relpath, pipe.stages)

            except (IOError, ValueError) as e:
                response.set_error(Response.Error.UNPROCESSABLE_ENTITY, str(e))
        else:
            response.set_error(Response.Error.UNPROCESSABLE_ENTITY)
    else:
        response.set_error(Response.Error.UNPROCESSABLE_ENTITY)

    dict_       = response.to_dict()
    json_       = jsonify(dict_)
    code        = response.code

    return json_, code
