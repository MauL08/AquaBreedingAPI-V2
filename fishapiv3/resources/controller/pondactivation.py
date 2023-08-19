from bson import ObjectId
from flask import Response, request
from fishapiv3.database.models import *
from flask_restful import Resource
from fishapiv3.database.db import db
from fishapiv3.resources.helper import getYearToday
import datetime
import json
from bson.json_util import dumps
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from bson.objectid import ObjectId

class PondsStatusApi(Resource):
    def get(self):
        pipline = [
            {'$lookup': {
                'from': 'pond_activation',
                'let': {"pondid": "$_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', '$$pondid']},
                    ]}}},
                    {'$lookup': {
                        'from': 'water_preparation',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$pond_activation_id', '$$pond_activation_id']}}},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }}
                        ],
                        'as': 'water_preparation'
                    }},
                    {"$addFields": {
                        "water_preparation": {"$first": "$water_preparation"}
                    }},
                    {"$project": {
                        "pond_id": 0,
                        "feed_type_id": 0,
                        "created_at": 0,
                        "updated_at": 0,
                    }}
                ],
                'as': 'pond_activation_list'
            }},
            {"$addFields": {
                "total_activation": {"$size": "$pond_activation_list"},
            }},
            {"$project": {
                "location": 0,
                "shape": 0,
                "material": 0,
                "length": 0,
                "width": 0,
                "diameter": 0,
                "height": 0,
                "image_name": 0,
                "pond_activation_list": 0,
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        ponds = Pond.objects().aggregate(pipline)
        response = list(ponds)
        response = json.dumps(response, default=str)
        return Response(response, mimetype="application/json", status=200)


class PondStatusApi(Resource):
    def get(self, pond_id):
        pond_objects = Pond.objects.get(id=pond_id)
        pipline = [
            {'$match': {'$expr': {'$eq': ['$_id', {'$toObjectId': pond_id}]}}},
            {'$lookup': {
                'from': 'pond_activation',
                'let': {"pondid": "$_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', '$$pondid']},
                    ]}}},
                    {"$sort": {"activated_at": -1}},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                                    {'$eq': ['$type_log', 'activation']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"},
                                "fish_total_weight": {"$sum": "$fish_total_weight"},
                                "fish_seed_id": {"$first": "$fish_seed_id"},
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_stock'
                    }},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                                    {'$ne': ['$type_log', 'deactivation']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                                # "fish_seed_id": 1,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"},
                                "fish_category": {"$first": "$fish_category"},
                                "fish_seed_id": {"$first": "$fish_seed_id"},
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                                # "fish_seed_id": 1,  # Include the fish_seed_id field
                            }},
                        ],
                        'as': 'fish_live'
                    }},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                             '$$pond_activation_id']},
                                    {'$eq': ['$type_log', 'death']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"}
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_death'
                    }},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                                    {'$eq': ['$type_log', 'deactivation']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"},
                                "fish_total_weight": {"$sum": "$fish_total_weight"},
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_harvested'
                    }},
                    {'$lookup': {
                        'from': 'feed_history',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                             '$$pond_activation_id']},
                                ]}
                            }},
                        ],
                        'as': 'feed_history'
                    }},
                    {'$lookup': {
                        'from': 'water_preparation',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$pond_activation_id', '$$pond_activation_id']}}},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }}
                        ],
                        'as': 'water_preparation'
                    }},
                    {"$addFields": {
                        "water_preparation": {"$first": "$water_preparation"},
                        "total_fish": {"$sum": "$fish_live.fish_amount"},
                        "survival_rate": {"$cond": [
                            {"$eq": [{"$sum": "$fish_stock.fish_amount"}, 0]},
                            0,
                            {"$multiply": [{"$divide": [{"$sum": "$fish_live.fish_amount"}, {
                                "$sum": "$fish_stock.fish_amount"}]}, 100]}
                        ]},
                        "weight_growth": {"$subtract": [{"$sum": "$fish_harvested.fish_total_weight"}, {"$sum": "$fish_stock.fish_total_weight"}]},
                        "total_dose": {"$sum": "$feed_history.feed_dose"},
                        # "fcr": {"$sum": {"$divide": [{"$sum": "$fish_live.fish_amount"}, {"$sum": "$fish_stock.fish_amount"}]}},
                    }},
                    {"$addFields": {
                        "fcr": {"$cond": [
                            {"$eq": [{"$sum": "$total_dose"}, 0]},
                            0,
                            {"$sum": {"$divide": [
                                "$weight_growth", "$total_dose"]}}
                        ]},
                    }},
                    {"$project": {
                        "pond_id": 0,
                        "feed_history": 0,
                        "feed_type_id": 0,
                        "created_at": 0,
                        "updated_at": 0,
                    }}
                ],
                'as': 'pond_activation_list'
            }},
            {"$addFields": {
                "total_activation": {"$size": "$pond_activation_list"},
                "pond_activation_list": '$pond_activation_list',

            }},
            {"$project": {
                "location": 0,
                "shape": 0,
                "material": 0,
                "length": 0,
                "width": 0,
                "diameter": 0,
                "height": 0,
                "image_name": 0,
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        ponds = Pond.objects().aggregate(pipline)
        ponds = list(ponds)
        ponds = dict(ponds[0])
        response = json.dumps(ponds, default=str)
        return Response(response, mimetype="application/json", status=200)


class PondActivationDetailApi(Resource):
    def get(self,id, pond):
        # log = FishLog.objects(pond_activation_id=id, type_log="deactivation").first()
        # response = json.dumps(ponds, default=str)
        activation = PondActivation.objects(id=id).first()
        pond_id = ObjectId(pond)
        # pond = Pond.objects(id=pond).first()
        pipline = [
            
            {'$match': {'$expr': {'$eq': ['$_id', pond_id]}}},
            {'$lookup': {
                'from': 'pond_activation',
                'let': {"pondid": "$_id"},
                'pipeline': [
                    {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', '$$pondid']},
                    ]}}},
                    {"$sort": {"activated_at": -1}},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                                    {'$eq': ['$type_log', 'activation']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"},
                                "fish_total_weight": {"$sum": "$fish_total_weight"}
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_stock'
                    }},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                                    {'$ne': ['$type_log', 'deactivation']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"}
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_live'
                    }},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                             '$$pond_activation_id']},
                                    {'$eq': ['$type_log', 'death']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"}
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_death'
                    }},
                    {'$lookup': {
                        'from': 'fish_log',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                     '$$pond_activation_id']},
                                    {'$eq': ['$type_log', 'deactivation']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"},
                                "fish_total_weight": {"$sum": "$fish_total_weight"},
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},
                        ],
                        'as': 'fish_harvested'
                    }},
                    {'$lookup': {
                        'from': 'feed_history',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                             '$$pond_activation_id']},
                                ]}
                            }},
                        ],
                        'as': 'feed_history'
                    }},
                    {'$lookup': {
                        'from': 'water_preparation',
                        'let': {"pond_activation_id": "$_id"},
                        'pipeline': [
                            {'$match': {
                                '$expr': {'$eq': ['$pond_activation_id', '$$pond_activation_id']}}},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }}
                        ],
                        'as': 'water_preparation'
                    }},
                    {"$addFields": {
                        "water_preparation": {"$first": "$water_preparation"},
                        "total_fish": {"$sum": "$fish_live.fish_amount"},
                        "survival_rate": {"$cond": [
                            {"$eq": [{"$sum": "$fish_stock.fish_amount"}, 0]},
                            0,
                            {"$multiply": [{"$divide": [{"$sum": "$fish_live.fish_amount"}, {
                                "$sum": "$fish_stock.fish_amount"}]}, 100]}
                        ]},
                        "weight_growth": {"$subtract": [{"$sum": "$fish_harvested.fish_total_weight"}, {"$sum": "$fish_stock.fish_total_weight"}]},
                        "total_dose": {"$sum": "$feed_history.feed_dose"},
                        # "fcr": {"$sum": {"$divide": [{"$sum": "$fish_live.fish_amount"}, {"$sum": "$fish_stock.fish_amount"}]}},
                    }},
                    {"$addFields": {
                        "fcr": {"$cond": [
                            {"$eq": [{"$sum": "$total_dose"}, 0]},
                            0,
                            {"$sum": {"$divide": [
                                "$weight_growth", "$total_dose"]}}
                        ]},
                    }},
                    {"$project": {
                        "pond_id": 0,
                        "feed_history": 0,
                        "feed_type_id": 0,
                        "created_at": 0,
                        "updated_at": 0,
                    }}
                ],
                'as': 'pond_activation_list'
            }},
            {"$addFields": {
                "total_activation": {"$size": "$pond_activation_list"},
                "pond_activation_list": '$pond_activation_list',

            }},
            {"$project": {
                "location": 0,
                "shape": 0,
                "material": 0,
                "length": 0,
                "width": 0,
                "diameter": 0,
                "height": 0,
                "image_name": 0,
                "updated_at": 0,
                "created_at": 0,
            }}
        ]
        ponds = Pond.objects().aggregate(pipline)
        ponds = list(ponds)
        activ = None
        for acti in ponds[0]["pond_activation_list"]:
            # activ = acti["_id"]
            if str(acti["_id"]) == id:
                activ = acti
        if activ == None:
            activ =0
        response =  {
            "id": activation.id,
            "pond_id": pond,
            # "pond_id": activation.pond_id,
            "is_finish": activation.isFinish,
            "water_level": activation.water_level,
            "total_fish_harvested": activation.total_fish_harvested,
            "total_weight_harvested": activation.total_weight_harvested,
            "activation_at": activation.activated_at,
            "deactivation_at": activation.deactivated_at,
            "deactivation_description": activation.deactivated_description,
            "fish_activated": activ["fish_stock"],
            "fish_alive": activ["fish_live"],
            "fish_harvested": activ["fish_harvested"],
            "fish_death": activ["fish_death"]
        }
        response = json.dumps(response, default=str)
        # response = jsonify(activation.__dict__)
        return Response(response, mimetype="application/json", status=200)

class PondActivationApi(Resource):
    def post(self, pond_id):
        pond = Pond.objects.get(id=pond_id)
        pipeline_year = {'$match': {'$expr': {'$and': [
                        {'$eq': ['$pond_id', {'$toObjectId': pond_id}]},
                        {'$eq': [{'$dateToString': {
                            'format': "%Y", 'date': "$created_at"}}, getYearToday()]},
        ]
        }}}
        list_pond_year = PondActivation.objects.aggregate(pipeline_year)
        list_pond_year = list(list_pond_year)
        id_int = len(list_pond_year) + 1
        if pond.isActive == True:
            response = {"message": "status pond is already active"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        fishes = request.form.get("fish", "[]")
        fishes = json.loads(fishes)
        if len(fishes) < 1:
            response = {"message": "There is no fish"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        isWaterPreparation = request.form.get("isWaterPreparation", False)
        # fish_harvested = request.form.get("fish_harvested", None)
        if isWaterPreparation == "true":
            isWaterPreparation = True
        else:
            isWaterPreparation = False
        water_level = request.form.get("water_level", None)

        active_at = request.form.get('active_at')

        pond_activation_data = {
            "id_int": id_int,
            "pond_id": pond_id,
            "isFinish": False,
            "isWaterPreparation": isWaterPreparation,
            "water_level": water_level,
        }

        if active_at != '':
            pond_activation_data['created_at'] = datetime.datetime.strptime(active_at, "%Y-%m-%dT%H:%M:%S.%f %z") 
            pond_activation_data['activated_at'] = datetime.datetime.strptime(active_at, "%Y-%m-%dT%H:%M:%S.%f %z") 
        else :
            three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)  # Approximating months as 30 days
            pond_activation_data['created_at'] = three_months_ago
            pond_activation_data['activated_at'] = three_months_ago

        # if active_at != '':
        #     pond_activation_data['activated_at'] = active_at
        # else :
        #     pond_activation_data['activated_at'] = request.form.get(
        #                 "activated_at", datetime.datetime.now())
        
        pondActivation = PondActivation(**pond_activation_data).save()
        pondActivation_id = pondActivation.id
        if isWaterPreparation == True:
            carbohydrate = request.form.get("carbohydrate", None)
            carbohydrate_type = request.form.get("carbohydrate_type", None)
            salt = request.form.get("salt", None)
            calcium = request.form.get("calcium", None)
            water_preparation_data = {
                "pond_activation_id": pondActivation_id,
                "carbohydrate": carbohydrate,
                "carbohydrate_type": carbohydrate_type,
                "salt": salt,
                "calcium": calcium,
            }

            water_preparation = WaterPreparation(
                **water_preparation_data).save()
        pond.update(**{"isActive": True,
        "status": "Aktif",  "pondDoDesc": "Belum Diukur", "pondPhDesc": "Belum Diukur", "pondPh": None, "pondDo": None, "pondTemp": None})
        print(fishes)
        for fish in fishes:
            # save fish log
            data = {
                "pond_id": pond_id,
                "pond_activation_id": pondActivation_id,
                "type_log": "activation",
                "fish_seed_id": fish['seed_id'],
                "fish_type": fish['type'],
                "fish_category": fish['category'],
                "fish_amount": fish['amount'],
                "fish_total_weight": fish['weight'],
                "fish_size": fish['size'],
            }
            fishlog = FishLog(**data).save()

            get_seed_by_id = SeedInventory.objects.get(id=fish['seed_id'])
            get_seed_by_id.amount -= int(fish['amount'])
            get_seed_by_id.save()        

        response = {"message": "success to activation pond"}
        response = json.dumps(response, default=str)
        return Response(response, mimetype="application/json", status=200)


class PondDeactivationApi(Resource):
    def post(self, pond_id):
        pond = Pond.objects.get(id=pond_id)
        if pond.isActive == False:
            response = {"message": "status pond is already not active"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
        # get last pond_activation
        pond_activation = PondActivation.objects(
            pond_id=pond_id, isFinish=False).order_by('-activated_at').first()
        fishes = request.form.get("fish", "[]")
        fishes = json.loads(fishes)
        total_fish_harvested = request.form.get("total_fish_harvested", None)
        amount_undersize = request.form.get("amount_undersize", None)
        amount_oversize = request.form.get("amount_oversize", None)
        amount_normal = request.form.get("amount_normal", None)
        sample_weight = request.form.get("sample_weight", None)
        sample_amount = request.form.get("sample_amount", None)
        sample_long = request.form.get("sample_long", None)
        total_weight_harvested = request.form.get("total_weight_harvested", None)
        # fish_harvested = request.form.get("fish_harvested", None)
        for fish in fishes:
            # save fish log
            data = {
                "pond_id": pond_id,
                "pond_activation_id": pond_activation.id,
                "type_log": "deactivation",
                "fish_type": fish['type'],
                "fish_amount": fish['amount'],
                "fish_total_weight": fish['weight'],
                "fish_seed_id": fish['fish_seed_id'],
                "fish_category": fish['fish_category'],
            }
            # total_fish_harvested += fish['amount']
            # total_weight_harvested += fish['weight']
            fishlog = FishLog(**data).save()
            print(data)
        print(total_fish_harvested)
        print(total_weight_harvested)
        # get args form data
        # update pond_activation
        pond_deactivation_data = {
            "isFinish": True,
            "total_fish_harvested": total_fish_harvested,
            "total_weight_harvested": total_weight_harvested,
            "deactivated_at": request.form.get("deactivated_at", datetime.datetime.now()),
            "deactivated_description": "Normal",
            "amount_undersize_fish":amount_undersize,
            "amount_oversize_fish":amount_oversize,
            "amount_normal_fish":amount_normal,
            "sample_amount":sample_amount,
            "sample_long":sample_long,
            "sample_weight": sample_weight
        }
        pond_activation.update(**pond_deactivation_data)
        # update pond isActive
        pond.update(**{"isActive": False,"status": "Panen"})
        response = {"message": "success to deactivation pond"}
        response = json.dumps(response, default=str)
        return Response(response, mimetype="application/json", status=200)

class DeactivationRecapApi(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            farm_id = ObjectId(farm)
    
            start_date = datetime.datetime.strptime(request.args.get('start_date'), '%Y-%m-%d') if request.args.get('start_date') else datetime.datetime.strptime("2023-01-01", '%Y-%m-%d')
            end_date = datetime.datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') + datetime.timedelta(days=1) if request.args.get('end_date') else datetime.datetime.strptime("2030-01-01", '%Y-%m-%d')
    
            pipeline = [
                {
                    '$match': {
                        'created_at': {
                            '$gte': start_date,
                            '$lte': end_date,
                        },
                        "farm_id": farm_id,
                    }
                },
                {"$sort": {"created_at": 1}},
                {'$lookup': {
                    'from': 'pond',
                    'let': {"pondid": "$pond_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$pondid']}}, },
                        {"$project": {
                            "_id": 1,
                            "alias": 1,
                            "location": 1,
                            "created_at": 1,
                        }}
                    ],
                    'as': 'pond_detail'
                }},
                {"$addFields": {
                    "pond_detail": {"$first": "$pond_detail"},
                }},
            ]

            testing = DeactivationRecap.objects.aggregate(pipeline)
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
                "pond_id": request.form.get('pond_id'),
                "farm_id": farm,
                "fish_seed_id": request.form.get('fish_seed_id'),
                "fish_weight": request.form.get('fish_weight'),
                "fish_amount": request.form.get('fish_amount'),
                "fish_type": request.form.get('fish_type'),
                "fish_category": request.form.get('fish_category'),
                "fish_price": request.form.get('fish_price'),
            }

            three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)  # Approximating months as 30 days
            body['created_at'] = three_months_ago

            DeactivationRecap(**body).save()
            res = {"message": "success add deactivation recap"}
            response = json.dumps(res, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": e}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)