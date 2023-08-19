from flask import Flask, Response, request, jsonify, current_app, url_for, send_from_directory, make_response
from fishapiv3.database.models import *
from flask_restful import Resource
from fishapiv3.resources.helper import *
from mongoengine import DoesNotExist
import datetime
import json
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from bson.objectid import ObjectId
from ...database.models import *

class SeedHistoryApi(Resource):
    @jwt_required()

    def get(self):
        try:

            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            farm_id = ObjectId(farm)

            start_date = datetime.datetime.strptime(request.args.get('start_date'), '%Y-%m-%d') if request.args.get('start_date') else datetime.datetime.strptime("2023-01-01", '%Y-%m-%d')
            end_date = datetime.datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') + datetime.timedelta(days=1) if request.args.get('end_date') else datetime.datetime.strptime("2030-01-01", '%Y-%m-%d')
            name = request.args.get('name') if request.args.get('name') else ""
            pond_name = request.args.get('pond_name') if request.args.get('pond_name') else ""

            pipeline = [
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
                        'pond': {
                            '$regex': pond_name,
                            '$options': 'i'
                        }
                    }
                },
                {"$sort": {"fish_seed_id": 1}},
                {'$lookup': {
                    'from': 'seed_inventory',
                    'let': {"fishseedid": "$fish_seed_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$fishseedid']}}, },
                        {
                            '$match': {
                                'brand_name': {
                                    '$regex': name,
                                    '$options': 'i'
                                }
                            }
                        },
                        {"$project": {
                            "_id": 1,
                            "fish_seed_category": 1,
                            "fish_type": 1,
                            "brand_name": 1,
                            "price": 1,
                            "total_price": 1,
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
            result = []

            for i in temp:
                if 'seed' in i:
                    result.append(i)
               

            response = json.dumps({
                'status': 'success',
                'data': result,
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
        
            req_pond = request.form.get('pond', None)
            req_seed_id = request.form.get('fish_seed_id', None)
            req_usage = request.form.get('usage', None) 
            
            history_by_pond =  SeedUsed.objects(pond=req_pond, fish_seed_id=req_seed_id).first()

            print(history_by_pond)

            theDate = request.form.get('created_at', None)

            body = {
                "farm_id": farm,
                "fish_seed_id": request.form.get('fish_seed_id', None),
                "original_amount": request.form.get('original_amount', None),
                "usage": request.form.get('usage', None),
                "pond": request.form.get('pond', None),
            }

            if theDate != '':
                body['created_at'] = datetime.datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z") 
            else :
                three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)  # Approximating months as 30 days
                body['created_at'] = three_months_ago

            # save body to history table
            seed_history = SeedUsed(**body).save()
            id = seed_history.id
            res = {"message": "success add seed history","id": id, "data": body}
            response = json.dumps(res, default=str)
            return Response(response, mimetype="application/json", status=200)

            # if history_by_pond == None:
            #     body = {
            #         "farm_id": farm,
            #         "fish_seed_id": request.form.get('fish_seed_id', None),
            #         "original_amount": request.form.get('original_amount', None),
            #         "usage": request.form.get('usage', None),
            #         "pond": request.form.get('pond', None),
            #     }

            #     # save body to history table
            #     seed_history = SeedUsed(**body).save()
            #     id = seed_history.id
            #     res = {"message": "success add seed history","id": id, "data": body}
            #     response = json.dumps(res, default=str)
            #     return Response(response, mimetype="application/json", status=200)
            # if req_pond == history_by_pond.pond :
            #     history_by_pond.usage += int(req_usage)
            #     history_by_pond.save()

            #     res = {"message": "success update seed history"}
            #     response = json.dumps(res, default=str)
            #     return Response(response, mimetype="application/json", status=200) 
                
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        
class FeedFishHistoryApi(Resource):
    @jwt_required()

    def get(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            farm_id = ObjectId(farm)

            start_date = datetime.datetime.strptime(request.args.get('start_date'), '%Y-%m-%d') if request.args.get('start_date') else datetime.datetime.strptime("2023-01-01", '%Y-%m-%d')
            end_date = datetime.datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') + datetime.timedelta(days=1) if request.args.get('end_date') else datetime.datetime.strptime("2030-01-01", '%Y-%m-%d')
            name = request.args.get('name') if request.args.get('name') else ""
            pond_name = request.args.get('pond_name') if request.args.get('pond_name') else ""

            pipeline = [
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
                        'pond': {
                            '$regex': pond_name,
                            '$options': 'i'
                        }
                    }
                },
                {"$sort": {"fish_feed_id": 1}},
                {'$lookup': {
                    'from': 'feed_inventory',
                    'let': {"fishfeedid": "$fish_feed_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$fishfeedid']}}},
                        {
                            '$match': {
                                'brand_name': {
                                    '$regex': name,
                                    '$options': 'i'
                                }
                            }
                        },
                        {"$project": {
                            "_id": 1,
                            "id_int": 1,
                            "feed_category": 1,
                            "brand_name": 1,
                            "price": 1,
                            "amount": 1,
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

    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])

            req_pond = request.form.get('pond', None)
            req_feed_id = request.form.get('fish_feed_id', None)
            req_usage = request.form.get('usage', None) 
            
            history_by_pond =  FeedUsed.objects(pond=req_pond, fish_feed_id=req_feed_id).first()

            theDate = request.form.get('created_at', None)

            body = {
                "farm_id": farm,
                "fish_feed_id": request.form.get('fish_feed_id', None),
                "original_amount": request.form.get('original_amount', None),
                "usage": request.form.get('usage', None),
                "pond": request.form.get('pond', None),
            }

            if theDate != '':
                body['created_at'] = datetime.datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z") 
            else :
                three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)  # Approximating months as 30 days
                body['created_at'] = three_months_ago

            # save body to history table
            feed_history = FeedUsed(**body).save()
            id = feed_history.id
            res = {"message": "success add feed history","id": id, "data": body}
            response = json.dumps(res, default=str)
            return Response(response, mimetype="application/json", status=200)
            # if history_by_pond == None:
            #     body = {
            #         "farm_id": farm,
            #         "fish_feed_id": request.form.get('fish_feed_id', None),
            #         "original_amount": request.form.get('original_amount', None),
            #         "usage": request.form.get('usage', None),
            #         "pond": request.form.get('pond', None),
            #         "created_at": datetime.datetime.strptime(request.form.get('created_at', None), "%Y-%m-%dT%H:%M:%S.%f %z") if request.form.get('created_at') else None,
            #     }

            #     # save body to history table
            #     feed_history = FeedUsed(**body).save()
            #     id = feed_history.id
            #     res = {"message": "success add feed history","id": id, "data": body}
            #     response = json.dumps(res, default=str)
            #     return Response(response, mimetype="application/json", status=200)
            # if req_pond == history_by_pond.pond :
            #     history_by_pond.usage += float(req_usage)
            #     history_by_pond.created_at = datetime.datetime.strptime(request.form.get('created_at', None), "%Y-%m-%dT%H:%M:%S.%f %z")

            #     history_by_pond.save()                

            #     res = {"message": "success update feed history"}
            #     response = json.dumps(res, default=str)
            #     return Response(response, mimetype="application/json", status=200) 
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        
class SuplemenHistoryApi(Resource):
    @jwt_required()

    def get(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            farm_id = ObjectId(farm)

            start_date = datetime.datetime.strptime(request.args.get('start_date'), '%Y-%m-%d') if request.args.get('start_date') else datetime.datetime.strptime("2023-01-01", '%Y-%m-%d')
            end_date = datetime.datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') + datetime.timedelta(days=1) if request.args.get('end_date') else datetime.datetime.strptime("2030-01-01", '%Y-%m-%d')
            name = request.args.get('name') if request.args.get('name') else ""
            pond_name = request.args.get('pond_name') if request.args.get('pond_name') else ""

            pipeline = [
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
                        'pond': {
                            '$regex': pond_name,
                            '$options': 'i'
                        }
                    }
                },
                {"$sort": {"fish_suplemen_id": 1}},
                {'$lookup': {
                    'from': 'suplemen_inventory',
                    'let': {"fishsuplemenid": "$fish_suplemen_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$fishsuplemenid']}}},
                        {
                            '$match': {
                                'name': {
                                    '$regex': name,
                                    '$options': 'i'
                                }
                            }
                        },
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

    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])

            req_pond = request.form.get('pond', None)
            req_suplemen_id = request.form.get('fish_suplemen_id', None)
            req_usage = request.form.get('usage', None) 
            
            history_by_pond =  SuplemenUsed.objects(pond=req_pond, fish_suplemen_id=req_suplemen_id).first()

            theDate = request.form.get('created_at', None)

            body = {
                "farm_id": farm,
                "fish_suplemen_id": request.form.get('fish_suplemen_id', None),
                "original_amount": request.form.get('original_amount', None),
                "usage": request.form.get('usage', None),
                "pond": request.form.get('pond', None),
            }

            if theDate != '':
                body['created_at'] = datetime.datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z") 
            else :
                three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)  # Approximating months as 30 days
                body['created_at'] = three_months_ago

            # save body to history table
            suplemen_history = SuplemenUsed(**body).save()
            id = suplemen_history.id
            res = {"message": "success add suplemen history","id": id, "data": body}
            response = json.dumps(res, default=str)
            return Response(response, mimetype="application/json", status=200)

            # if history_by_pond == None:
            #     body = {
            #         "farm_id": farm,
            #         "fish_suplemen_id": request.form.get('fish_suplemen_id', None),
            #         "original_amount": request.form.get('original_amount', None),
            #         "usage": request.form.get('usage', None),
            #         "pond": request.form.get('pond', None),
            #     }

            #     # save body to history table
            #     suplemen_history = SuplemenUsed(**body).save()
            #     id = suplemen_history.id
            #     res = {"message": "success add suplemen history","id": id, "data": body}
            #     response = json.dumps(res, default=str)
            #     return Response(response, mimetype="application/json", status=200)
            # if req_pond == history_by_pond.pond :
            #     history_by_pond.usage += float(req_usage)
            #     history_by_pond.save()

            #     res = {"message": "success update suplemen history"}
            #     response = json.dumps(res, default=str)
            #     return Response(response, mimetype="application/json", status=200) 
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)