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
    @jwt_required()
    def get(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            farm_id = ObjectId(farm)
            
            type = request.args.get('type') if request.args.get('type') else ""

            pipeline = [
                {"$sort": {"id_int": 1}},
                {
                    '$match': {
                        "farm_id": farm_id,
                        'fish_seed_category': {
                            '$regex': type,
                            '$options': 'i'
                        }
                    }
                },
            ]
           
            testing = SeedInventory.objects.aggregate(pipeline)
            temp = list(testing)
            response = json.dumps({
                'status': 'success',
                'data': temp,
            }, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": e}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        
    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            body = {
                "farm_id": farm,
                "fish_seed_category": request.form.get('fish_seed_category', None),
                "fish_type": request.form.get('fish_type', None),
                "brand_name": request.form.get('brand_name', None),
                "amount": request.form.get('amount', None),
                "weight": request.form.get('weight', None),
                "width": request.form.get('width', None),
                "price": request.form.get('price', None),
                "total_price": request.form.get('total_price', None),
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
            response = json.dumps({
                'status': 'success',
                'data': temp[0],
            }, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": e}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
    
    def put(self, id):
        try:
            body = {
                "id_int": int(id),
                "fish_seed_category": request.form.get('fish_seed_category', None),
                "fish_type": request.form.get('fish_type', None),
                "brand_name": request.form.get('brand_name', None),
                "amount": request.form.get('amount', None),
                "weight": request.form.get('weight', None),
                "width": request.form.get('width', None),
                "price": request.form.get('price', None),
                "total_price": request.form.get('total_price', None),
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
            inventory = SeedInventory.objects.get(id_int = int(id)).delete()
            response = {"message": "success delete seed inventory"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

class FeedInventoriesApi(Resource):
    @jwt_required()

    def get(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            farm_id = ObjectId(farm)

            type = request.args.get('type') if request.args.get('type') else ""

            pipeline = [
                {"$sort": {"id_int": 1}},
                {
                    '$match': {
                        "farm_id": farm_id,
                        'feed_category': {
                            '$regex': type,
                            '$options': 'i'
                        }
                    }
                },
                {'$lookup': {
                    'from': 'feed_name',
                    'let': {"feednameid": "$feed_name_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$feednameid']}}},
                        {"$project": {
                            "_id": 1,
                            "id_int": 1,
                            "type": 1,
                            "name": 1,
                            "description": 1,
                            "producer": 1,
                            "protein": 1,
                            "carbohydrate": 1,
                            "min_expired_period": 1,
                            "max_expired_period": 1,
                            "image": 1,
                            "created_at": 1,
                        }}
                    ],
                    'as': 'feed'
                }},
                {"$addFields": {
                    "feed": {"$first": "$feed"},
                }},
            ]
           
            testing = FeedInventory.objects.aggregate(pipeline)
            temp = list(testing)
            response = json.dumps({
                'status': 'success',
                'data': temp,
            }, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": e}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            body = {
                "farm_id": farm,
                # "type": request.form.get('type', None),
                # "name": request.form.get('name', None),
                # "description": request.form.get('description', None),
                # "producer": request.form.get('producer', None),
                # "protein": request.form.get('protein', None),
                # "carbohydrate": request.form.get('carbohydrate', None),
                # "min_expired_period": request.form.get('min_expired_period', None),
                # "max_expired_period": request.form.get('max_expired_period', None),
                # "image": request.form.get('image', None),
                "feed_name_id": request.form.get('feed_name_id', None),
                "feed_category": request.form.get('feed_category', None),
                "brand_name": request.form.get('brand_name', None),
                "price": request.form.get('price', None),
                "amount": request.form.get('amount', None),
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
            pipeline = [
                {"$match": {"id_int": int(id)}},
                # {'$lookup': {
                #     'from': 'feed_name',
                #     'let': {"feednameid": "$feed_name_id"},
                #     'pipeline': [
                #         {'$match': {'$expr': {'$eq': ['$_id', '$$feednameid']}}},
                #         {"$project": {
                #             "_id": 1,
                #             "id_int": 1,
                #             "name": 1,
                           
                #         }}
                #     ],
                #     'as': 'feed_detail',
                # }},
                # {"$addFields": {
                #     "feed_detail": {"$first": "$feed_detail"},
                # }},
                {'$lookup': {
                    'from': 'feed_name',
                    'let': {"feednameid": "$feed_name_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$feednameid']}}},
                        {"$project": {
                            "_id": 1,
                            "id_int": 1,
                            "type": 1,
                            "name": 1,
                            "description": 1,
                            "producer": 1,
                            "protein": 1,
                            "carbohydrate": 1,
                            "min_expired_period": 1,
                            "max_expired_period": 1,
                            "image": 1,
                            "created_at": 1,
                        }}
                    ],
                    'as': 'feed'
                }},
                {"$addFields": {
                    "feed": {"$first": "$feed"},
                }},
            ]
     
            testing = FeedInventory.objects.aggregate(pipeline)
            temp = list(testing)
            if len(temp) == 0:
                res = {"message": 'no data found'}
                response = json.dumps(res, default=str)
                return Response(response, mimetype="application/json", status=200)
            response = json.dumps({
                'status': 'success',
                'data': temp[0],
            }, default=str)
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
                # "type": request.form.get('type', None),
                # "name": request.form.get('name', None),
                # "description": request.form.get('description', None),
                # "producer": request.form.get('producer', None),
                # "protein": request.form.get('protein', None),
                # "carbohydrate": request.form.get('carbohydrate', None),
                # "min_expired_period": request.form.get('min_expired_period', None),
                # "max_expired_period": request.form.get('max_expired_period', None),
                # "image": request.form.get('image', None),
                "feed_category": request.form.get('feed_category', None),
                "brand_name": request.form.get('brand_name', None),
                "price": request.form.get('price', None),
                "amount": request.form.get('amount', None),
            }

            feed_name_id = request.form.get('feed_name_id', None)
            feed_name = FeedName.objects.get(id=feed_name_id)
            body["feed_name_id"] = feed_name.id

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
        
class FeedNamesApi(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            farm_id = ObjectId(farm)

            type = request.args.get('type') if request.args.get('type') else ""

            pipeline = [
                {"$sort": {"id_int": 1}},
                {
                    '$match': {
                        "farm_id": farm_id,
                        'type': {
                            '$regex': type,
                            '$options': 'i'
                        }
                    }
                }
            ]

            testing = FeedName.objects.aggregate(pipeline)
            temp = list(testing)
            response = json.dumps({
                'status': 'success',
                'data': temp,
            }, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": e}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            body = {
                "farm_id": farm,
                "type": request.form.get('type', None),
                "name": request.form.get('name', None),
                "description": request.form.get('description', None),
                "producer": request.form.get('producer', None),
                "protein": request.form.get('protein', None),
                "carbohydrate": request.form.get('carbohydrate', None),
                "min_expired_period": request.form.get('min_expired_period', None),
                "max_expired_period": request.form.get('max_expired_period', None),
                "image": request.form.get('image', None),
            }
            feed_name = FeedName(**body).save()
            id = feed_name.id
            res = {"message": "success add feed name to db", "id": id, "data": body}
            response = json.dumps(res, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        
class FeedNameApi(Resource):
    def get(self, id):
        try:
            pipeline = [
                {"$match": {"id_int": int(id)}},
                # {'$lookup': {
                #     'from': 'feed_name',
                #     'let': {"feednameid": "$feed_name_id"},
                #     'pipeline': [
                #         {'$match': {'$expr': {'$eq': ['$_id', '$$feednameid']}}},
                #         {"$project": {
                #             "_id": 1,
                #             "id_int": 1,
                #             "name": 1,
                           
                #         }}
                #     ],
                #     'as': 'feed_detail',
                # }},
                # {"$addFields": {
                #     "feed_detail": {"$first": "$feed_detail"},
                # }},
            ]
     
            testing = FeedName.objects.aggregate(pipeline)
            temp = list(testing)
            if len(temp) == 0:
                res = {"message": 'no data found'}
                response = json.dumps(res, default=str)
                return Response(response, mimetype="application/json", status=200)
            response = json.dumps({
                'status': 'success',
                'data': temp[0],
            }, default=str)
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
                # "type": request.form.get('type', None),
                # "name": request.form.get('name', None),
                # "description": request.form.get('description', None),
                # "producer": request.form.get('producer', None),
                # "protein": request.form.get('protein', None),
                # "carbohydrate": request.form.get('carbohydrate', None),
                # "min_expired_period": request.form.get('min_expired_period', None),
                # "max_expired_period": request.form.get('max_expired_period', None),
                # "image": request.form.get('image', None),
                "type": request.form.get('type', None),
                "name": request.form.get('name', None),
                "description": request.form.get('description', None),
                "producer": request.form.get('producer', None),
                "protein": request.form.get('protein', None),
                "carbohydrate": request.form.get('carbohydrate', None),
                "min_expired_period": request.form.get('min_expired_period', None),
                "max_expired_period": request.form.get('max_expired_period', None),
                "image": request.form.get('image', None),
            }
            inventory = FeedName.objects.get(id_int = int(id)).update(**body)
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
            inventory = FeedName.objects.get(id_int = int(id)).delete()
            response = {"message": "success delete feed name on inventory"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

class SuplemenInventoriesApi(Resource):
    @jwt_required()

    def get(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            farm_id = ObjectId(farm)

            type = request.args.get('type') if request.args.get('type') else ""
            name = request.args.get('name') if request.args.get('name') else ""

            pipeline = [
                {"$sort": {"id_int": 1}},
                {
                    '$match': {
                        "farm_id": farm_id,
                        'function': {
                            '$regex': type,
                            '$options': 'i'
                        }
                    }
                },
                {
                    '$match': {
                        'name': {
                            '$regex': name,
                            '$options': 'i'
                        }
                    }
                }
            ]
           
            testing = SuplemenInventory.objects.aggregate(pipeline)
            temp = list(testing)
            response = json.dumps({
                'status': 'success',
                'data': temp,
            }, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": e}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            body = {
                "farm_id": farm,
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
            response = json.dumps({
                'status': 'success',
                'data': temp[0],
            }, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": e}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        
    def put(self, id):
        try:
            body = {
                "id_int": int(id),
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
            inventory = SuplemenInventory.objects.get(id_int = int(id)).delete()
            response = {"message": "success delete suplemen inventory"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

class ElectricInventoriesApi(Resource):
    @jwt_required()

    def get(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            farm_id = ObjectId(farm)

            start_date = datetime.datetime.strptime(request.args.get('start_date'), '%Y-%m-%d') if request.args.get('start_date') else datetime.datetime.strptime("2023-01-01", '%Y-%m-%d')
            end_date = datetime.datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') + datetime.timedelta(days=1) if request.args.get('end_date') else datetime.datetime.strptime("2030-01-01", '%Y-%m-%d')
            type = request.args.get('type') if request.args.get('type') else ""

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
                {
                    '$match': {
                        "farm_id": farm_id,
                        'type': {
                            '$regex': type,
                            '$options': 'i'
                        }
                    }
                }
            ]
           
            testing = ElectricInventory.objects.aggregate(pipeline)
            temp = list(testing)
            response = json.dumps({
                'status': 'success',
                'data': temp,
            }, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": e}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            body = {
                "farm_id": farm,
                "name": request.form.get('name', None),
                "price": request.form.get('price', None),
                "type": request.form.get('type', None),
                "daya": request.form.get('daya', None),
                "image": request.form.get('image', None),
                "id_token": request.form.get('id_token', None),
                "month": request.form.get('month', None)
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
            response = json.dumps({
                'status': 'success',
                'data': temp[0],
            }, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": e}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        
    def put(self, id):
        try:

            body = {
                "id_int": int(id),
                "name": request.form.get('name', None),
                "price": request.form.get('price', None),
                "type": request.form.get('type', None),
                "daya": request.form.get('daya', None),
                "image": request.form.get('image', None),
                "id_token": request.form.get('id_token', None),
                "month": request.form.get('month', None)
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
            inventory = ElectricInventory.objects.get(id_int = int(id)).delete()
            response = {"message": "success delete electric inventory"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

class AssetInventoriesApi(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            farm_id = ObjectId(farm)

            type = request.args.get('type') if request.args.get('type') else ""
            start_date = datetime.datetime.strptime(request.args.get('start_date'), '%Y-%m-%d') if request.args.get('start_date') else datetime.datetime.strptime("2023-01-01", '%Y-%m-%d')
            end_date = datetime.datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') + datetime.timedelta(days=1) if request.args.get('end_date') else datetime.datetime.strptime("2030-01-01", '%Y-%m-%d')

            pipeline = [
                {"$sort": {"id_int": 1}},
                {
                    '$match': {
                        "farm_id": farm_id,
                        'asset_category': {
                            '$regex': type,
                            '$options': 'i'
                        },
                         'created_at': {
                            '$gte': start_date,
                            '$lte': end_date,
                        }
                    }
                },
            ]
           
            testing = AssetInventory.objects.aggregate(pipeline)
            temp = list(testing)
            response = json.dumps({
                'status': 'success',
                'data': temp,
            }, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": e}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            body = {
                "farm_id": farm,
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
            response = json.dumps({
                'status': 'success',
                'data': temp[0],
            }, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": e}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        
    def put(self, id):
        try:
            body = {       
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
            inventory = AssetInventory.objects.get(id_int = int(id)).delete()
            response = {"message": "success delete asset inventory"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)