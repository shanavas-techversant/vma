from flask import Blueprint
from flask_restful import Resource, Api

from vma_app.db import get_schema
from serializer import serialize

internal_blueprint = Blueprint("internal", __name__, url_prefix="/api/v1/internal")
api = Api(internal_blueprint)


class DBSchema(Resource):
    def get(self):
        schema = get_schema()
        return {"schema": serialize(schema)}


api.add_resource(DBSchema, "/schema")
