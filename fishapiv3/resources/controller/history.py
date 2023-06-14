from flask import Flask, Response, request, jsonify, current_app, url_for, send_from_directory, make_response
from fishapiv3.database.models import *
from flask_restful import Resource
from fishapiv3.resources.helper import *
from datetime import datetime
import json
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from bson.objectid import ObjectId

class SeedHistoryApi(Resource):
    def get(self):
        try:
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d') if request.args.get('start_date') else ""
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') if request.args.get('end_date') else ""

            pipeline = [
                {
                    '$match': {
                        'created_at': {
                            '$gte': start_date,
                            '$lte': end_date,
                        }
                    }
                },
                {"$sort": {"fish_seed_id": 1}}
            ]

            testing = SeedHistory.objects.aggregate(pipeline)
            temp = list(testing)
            response = json.dumps(temp, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": e}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def post(self):
        try:
            body = {
                "fish_seed_id": request.form.get('fish_seed_id', None),
                "original_amount": request.form.get('original_amount', None),
                "usage": request.form.get('usage', None),
                "pond": request.form.get('pond', None),
            }

            seed_history = SeedHistory(**body).save()
            id = seed_history.id
            res = {"message": "success add seed history","id": id, "data": body}
            response = json.dumps(res, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
