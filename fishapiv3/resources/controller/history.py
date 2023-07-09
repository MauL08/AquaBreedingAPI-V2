from flask import Flask, Response, request, jsonify, current_app, url_for, send_from_directory, make_response
from fishapiv3.database.models import *
from flask_restful import Resource
from fishapiv3.resources.helper import *
import datetime
import json
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from bson.objectid import ObjectId
from ...database.models import *

class SeedHistoryApi(Resource):
    def get(self):
        try:
            start_date = datetime.datetime.strptime(request.args.get('start_date'), '%Y-%m-%d') if request.args.get('start_date') else datetime.datetime.strptime("2023-01-01", '%Y-%m-%d')
            end_date = datetime.datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') + datetime.timedelta(days=1) if request.args.get('end_date') else datetime.datetime.strptime("2030-01-01", '%Y-%m-%d')

            pipeline = [
                {
                    '$match': {
                        'created_at': {
                            '$gte': start_date,
                            '$lte': end_date,
                        }
                    }
                },
                {"$sort": {"fish_seed_id": 1}},
                {'$lookup': {
                    'from': 'seed_inventory',
                    'let': {"fishseedid": "$fish_seed_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$fishseedid']}}},
                        {"$project": {
                            "_id": 1,
                            "fish_seed_category": 1,
                            "fish_type": 1,
                            "brand_name": 1,
                            "price": 1,
                            "created_at": 1,
                        }}
                    ],
                    'as': 'seed'
                }},
                {"$addFields": {
                    "seed": {"$first": "$seed"},
                }},
            ]

            testing = SeedUsed.objects.aggregate(pipeline)
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

    def post(self):
        try:
            body = {
                "fish_seed_id": request.form.get('fish_seed_id', None),
                "original_amount": request.form.get('original_amount', None),
                "usage": request.form.get('usage', None),
                "pond": request.form.get('pond', None),
            }

            # save body to history table
            seed_history = SeedUsed(**body).save()
            id = seed_history.id
            res = {"message": "success add seed history","id": id, "data": body}
            response = json.dumps(res, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        
class FeedFishHistoryApi(Resource):
    def get(self):
        try:
            start_date = datetime.datetime.strptime(request.args.get('start_date'), '%Y-%m-%d') if request.args.get('start_date') else datetime.datetime.strptime("2023-01-01", '%Y-%m-%d')
            end_date = datetime.datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') + datetime.timedelta(days=1) if request.args.get('end_date') else datetime.datetime.strptime("2030-01-01", '%Y-%m-%d')

            pipeline = [
                {
                    '$match': {
                        'created_at': {
                            '$gte': start_date,
                            '$lte': end_date,
                        }
                    }
                },
                {"$sort": {"fish_feed_id": 1}},
                {'$lookup': {
                    'from': 'feed_inventory',
                    'let': {"fishfeedid": "$fish_feed_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$fishfeedid']}}},
                        {"$project": {
                            "_id": 1,
                            "id_int": 1,
                            "feed_category": 1,
                            "brand_name": 1,
                            "description": 1,
                            "price": 1,
                            "amount": 1,
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

            testing = FeedUsed.objects.aggregate(pipeline)
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

    def post(self):
        try:
            body = {
                "fish_feed_id": request.form.get('fish_feed_id', None),
                "original_amount": request.form.get('original_amount', None),
                "usage": request.form.get('usage', None),
                "pond": request.form.get('pond', None),
            }

            # update feed inventory table
            get_feed_by_id = FeedInventory.objects.get(id=request.form.get('fish_feed_id', None))
            get_feed_by_id.amount -= int(request.form.get('usage', None))
            get_feed_by_id.save()
            
            # save body to history table
            feed_history = FeedUsed(**body).save()
            id = feed_history.id
            res = {"message": "success add feed history","id": id, "data": body}
            response = json.dumps(res, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        
class SuplemenHistoryApi(Resource):
    def get(self):
        try:
            start_date = datetime.datetime.strptime(request.args.get('start_date'), '%Y-%m-%d') if request.args.get('start_date') else datetime.datetime.strptime("2023-01-01", '%Y-%m-%d')
            end_date = datetime.datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') + datetime.timedelta(days=1) if request.args.get('end_date') else datetime.datetime.strptime("2030-01-01", '%Y-%m-%d')

            pipeline = [
                {
                    '$match': {
                        'created_at': {
                            '$gte': start_date,
                            '$lte': end_date,
                        }
                    }
                },
                {"$sort": {"fish_suplemen_id": 1}},
                {'$lookup': {
                    'from': 'suplemen_inventory',
                    'let': {"fishsuplemenid": "$fish_suplemen_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$fishsuplemenid']}}},
                        {"$project": {
                            "_id": 1,
                            "id_int": 1,
                            "function": 1,
                            "name": 1,
                            "description": 1,
                            "price": 1,
                            "amount": 1,
                            "type": 1,
                            "min_expired_period": 1,
                            "max_expired_period": 1,
                            "image": 1,
                            "created_at": 1,
                        }}
                    ],
                    'as': 'suplemen'
                }},
                {"$addFields": {
                    "suplemen": {"$first": "$suplemen"},
                }},
            ]

            testing = SuplemenUsed.objects.aggregate(pipeline)
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

    def post(self):
        try:
            body = {
                "fish_suplemen_id": request.form.get('fish_suplemen_id', None),
                "original_amount": request.form.get('original_amount', None),
                "usage": request.form.get('usage', None),
                "pond": request.form.get('pond', None),
            }

            # update suplemen inventory table
            get_suplemen_by_id = SuplemenInventory.objects.get(id=request.form.get('fish_suplemen_id', None))
            get_suplemen_by_id.amount -= float(request.form.get('usage', None))
            get_suplemen_by_id.save()
            
            # save body to history table
            suplemen_history = SuplemenUsed(**body).save()
            id = suplemen_history.id
            res = {"message": "success add suplemen history","id": id, "data": body}
            response = json.dumps(res, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)