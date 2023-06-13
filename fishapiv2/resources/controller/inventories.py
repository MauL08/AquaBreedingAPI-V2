from flask import Flask, Response, request, jsonify, current_app, url_for, send_from_directory, make_response
from fishapiv2.database.models import *
from flask_restful import Resource
from fishapiv2.resources.helper import *
import datetime
import json
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from bson.objectid import ObjectId

class SeedInventoriesApi(Resource):
    def get(self):
        try:
            type = request.args.get('type') if request.args.get('type') else ""

            pipeline = [
                {"$sort": {"id_int": 1}},
                {
                    '$match': {
                        'fish_seed_category': {
                            '$regex': type,
                            '$options': 'i'
                        }
                    }
                }
            ]
           
            testing = SeedInventory.objects.aggregate(pipeline)
            temp = list(testing)
            response = json.dumps(temp, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": e}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
    # @jwt_required()
    def post(self):
        try:
            # current_user = get_jwt_identity()
            # farm = str(current_user['farm_id'])
            body = {
                # "farm_id": farm,
                "fish_seed_category": request.form.get('fish_seed_category', None),
                "fish_type": request.form.get('fish_type', None),
                "brand_name": request.form.get('brand_name', None),
                "amount": request.form.get('amount', None),
                "weight": request.form.get('weight', None),
                "length": request.form.get('length', None),
                "width": request.form.get('width', None),
                "price": request.form.get('price', None),
            }
            inventory = SeedInventory(**body).save()
            id = inventory.id
            res = {"message": "success add seed to inventory", "id": id, "data": body}
            response = json.dumps(res, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

class SeedInventoryApi(Resource):
    def get(self, id):
        try:
            pipeline = {"$match": {"id_int": int(id)}},
            testing = SeedInventory.objects.aggregate(pipeline)
            temp = list(testing)
            if len(temp) == 0:
                return Response('no data found', mimetype="application/json", status=200)
            response = json.dumps(temp[0], default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": e}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        
    def put(self, id):
        try:
            # current_user = get_jwt_identity()
            # farm = str(current_user['farm_id'])
            body = {
                # "farm_id": farm,
                "id_int": int(id),
                "fish_seed_category": request.form.get('fish_seed_category', None),
                "fish_type": request.form.get('fish_type', None),
                "brand_name": request.form.get('brand_name', None),
                "amount": request.form.get('amount', None),
                "weight": request.form.get('weight', None),
                "length": request.form.get('length', None),
                "width": request.form.get('width', None),
                "price": request.form.get('price', None),
            }
            inventory = SeedInventory.objects.get(id_int = int(id)).update(**body)
            response = {"message": "success update seed inventory", "data": body}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def delete(self, id):
        try:
            # current_user = get_jwt_identity()
            # farm = str(current_user['farm_id'])
            inventory = SeedInventory.objects.get(id_int = int(id)).delete()
            response = {"message": "success delete seed inventory"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
