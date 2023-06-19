from flask import Flask, Response, request, jsonify, current_app, url_for, send_from_directory, make_response
from fishapiv3.database.models import *
from flask_restful import Resource
from fishapiv3.resources.helper import *
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
                "image": request.form.get('image', None)
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
                res = {"message": 'no data found'}
                response = json.dumps(res, default=str)
                return Response(response, mimetype="application/json", status=200)
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
                "image": request.form.get('image', None)
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

class FeedInventoriesApi(Resource):
    def get(self):
        try:
            type = request.args.get('type') if request.args.get('type') else ""

            pipeline = [
                {"$sort": {"id_int": 1}},
                {
                    '$match': {
                        'feed_category': {
                            '$regex': type,
                            '$options': 'i'
                        }
                    }
                }
            ]
           
            testing = FeedInventory.objects.aggregate(pipeline)
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
                "feed_category": request.form.get('feed_category', None),
                "brand_name": request.form.get('brand_name', None),
                "description": request.form.get('description', None),
                "price": request.form.get('price', None),
                "amount": request.form.get('amount', None),
                "producer": request.form.get('producer', None),
                "protein": request.form.get('protein', None),
                "carbohydrate": request.form.get('carbohydrate', None),
                "min_expired_period": request.form.get('min_expired_period', None),
                "max_expired_period": request.form.get('max_expired_period', None),
                "image": request.form.get('image', None),
            }
            inventory = FeedInventory(**body).save()
            id = inventory.id
            res = {"message": "success add feed to inventory", "id": id, "data": body}
            response = json.dumps(res, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

class FeedInventoryApi(Resource):
    def get(self, id):
        try:
            pipeline = {"$match": {"id_int": int(id)}},
            testing = FeedInventory.objects.aggregate(pipeline)
            temp = list(testing)
            if len(temp) == 0:
                res = {"message": 'no data found'}
                response = json.dumps(res, default=str)
                return Response(response, mimetype="application/json", status=200)
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
                "feed_category": request.form.get('feed_category', None),
                "brand_name": request.form.get('brand_name', None),
                "description": request.form.get('description', None),
                "price": request.form.get('price', None),
                "amount": request.form.get('amount', None),
                "producer": request.form.get('producer', None),
                "protein": request.form.get('protein', None),
                "carbohydrate": request.form.get('carbohydrate', None),
                "min_expired_period": request.form.get('min_expired_period', None),
                "max_expired_period": request.form.get('max_expired_period', None),
                "image": request.form.get('image', None),
            }
            inventory = FeedInventory.objects.get(id_int = int(id)).update(**body)
            response = {"message": "success update feed inventory", "data": body}
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
            inventory = FeedInventory.objects.get(id_int = int(id)).delete()
            response = {"message": "success delete feed inventory"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

class SuplemenInventoriesApi(Resource):
    def get(self):
        try:
            type = request.args.get('type') if request.args.get('type') else ""

            pipeline = [
                {"$sort": {"id_int": 1}},
                {
                    '$match': {
                        'function': {
                            '$regex': type,
                            '$options': 'i'
                        }
                    }
                }
            ]
           
            testing = SuplemenInventory.objects.aggregate(pipeline)
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
                "function": request.form.get('function', None),
                "name": request.form.get('name', None),
                "description": request.form.get('description', None),
                "price": request.form.get('price', None),
                "amount": request.form.get('amount', None),
                "type": request.form.get('type', None),
                "min_expired_period": request.form.get('min_expired_period', None),
                "max_expired_period": request.form.get('max_expired_period', None),
                "image": request.form.get('image', None)
            }
            inventory = SuplemenInventory(**body).save()
            id = inventory.id
            res = {"message": "success add suplemen to inventory", "id": id, "data": body}
            response = json.dumps(res, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

class SuplemenInventoryApi(Resource):
    def get(self, id):
        try:
            pipeline = {"$match": {"id_int": int(id)}},
            testing = SuplemenInventory.objects.aggregate(pipeline)
            temp = list(testing)
            if len(temp) == 0:
                res = {"message": 'no data found'}
                response = json.dumps(res, default=str)
                return Response(response, mimetype="application/json", status=200)
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
                "function": request.form.get('function', None),
                "name": request.form.get('name', None),
                "description": request.form.get('description', None),
                "price": request.form.get('price', None),
                "amount": request.form.get('amount', None),
                "type": request.form.get('type', None),
                "min_expired_amount": request.form.get('min_expired_amount', None),
                "max_expired_amount": request.form.get('max_expired_amount', None),
                "image": request.form.get('image', None)
            }
            inventory = SuplemenInventory.objects.get(id_int = int(id)).update(**body)
            response = {"message": "success update suplemen inventory", "data": body}
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
            inventory = SuplemenInventory.objects.get(id_int = int(id)).delete()
            response = {"message": "success delete suplemen inventory"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

class ElectricInventoriesApi(Resource):
    def get(self):
        try:
            start_date = datetime.datetime.strptime(request.args.get('start_date'), '%Y-%m-%d') if request.args.get('start_date') else ""
            end_date = datetime.datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') + datetime.timedelta(days=1) if request.args.get('end_date') else ""


            pipeline = [
                {"$sort": {"id_int": 1}},
                {
                    '$match': {
                        'created_at': {
                            '$gte': start_date,
                            '$lte': end_date,
                        }
                    }
                },
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
                "name": request.form.get('name', None),
                "price": request.form.get('price', None),
                "type": request.form.get('type', None),
                "daya": request.form.get('daya', None),
                "image": request.form.get('image', None),
            }
            inventory = ElectricInventory(**body).save()
            id = inventory.id
            res = {"message": "success add electric to inventory", "id": id, "data": body}
            response = json.dumps(res, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

class ElectricInventoryApi(Resource):
    def get(self, id):
        try:
            pipeline = {"$match": {"id_int": int(id)}},
            testing = ElectricInventory.objects.aggregate(pipeline)
            temp = list(testing)
            if len(temp) == 0:
                res = {"message": 'no data found'}
                response = json.dumps(res, default=str)
                return Response(response, mimetype="application/json", status=200)
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
                "name": request.form.get('name', None),
                "price": request.form.get('price', None),
                "type": request.form.get('type', None),
                "daya": request.form.get('daya', None),
                "image": request.form.get('image', None),
            }
            inventory = ElectricInventory.objects.get(id_int = int(id)).update(**body)
            response = {"message": "success update electric inventory", "data": body}
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
            inventory = ElectricInventory.objects.get(id_int = int(id)).delete()
            response = {"message": "success delete electric inventory"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

class AssetInventoriesApi(Resource):
    def get(self):
        try:
            type = request.args.get('type') if request.args.get('type') else ""

            pipeline = [
                {"$sort": {"id_int": 1}},
                {
                    '$match': {
                        'asset_category': {
                            '$regex': type,
                            '$options': 'i'
                        }
                    }
                }
            ]
           
            testing = AssetInventory.objects.aggregate(pipeline)
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
                "asset_category": request.form.get('asset_category', None),
                "name": request.form.get('name', None),
                "description": request.form.get('description', None),
                "amount": request.form.get('amount', None),
                "price": request.form.get('price', None),
                "image": request.form.get('image', None),
            }
            inventory = AssetInventory(**body).save()
            id = inventory.id
            res = {"message": "success add asset to inventory", "id": id, "data": body}
            response = json.dumps(res, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

class AssetInventoryApi(Resource):
    def get(self, id):
        try:
            pipeline = {"$match": {"id_int": int(id)}},
            testing = AssetInventory.objects.aggregate(pipeline)
            temp = list(testing)
            if len(temp) == 0:
                res = {"message": 'no data found'}
                response = json.dumps(res, default=str)
                return Response(response, mimetype="application/json", status=200)
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
                "asset_category": request.form.get('asset_category', None),
                "name": request.form.get('name', None),
                "description": request.form.get('description', None),
                "amount": request.form.get('amount', None),
                "price": request.form.get('price', None),
                "image": request.form.get('image', None),
            }
            inventory = AssetInventory.objects.get(id_int = int(id)).update(**body)
            response = {"message": "success update asset inventory", "data": body}
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
            inventory = AssetInventory.objects.get(id_int = int(id)).delete()
            response = {"message": "success delete asset inventory"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)