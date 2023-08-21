from flask import Response, request
from fishapiv3.database.models import *
from flask_restful import Resource
import datetime
import json
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from bson.objectid import ObjectId
from dateutil.relativedelta import relativedelta



class PondTreatmentsApi(Resource):
    @jwt_required()

    def get(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            farm_id = ObjectId(farm)
            
            pipeline = [
                {"$sort": {"created_at": -1}},
                {
                    '$match': {
                        "farm_id": farm_id,
                    }
                },
                {'$lookup': {
                    'from': 'pond',
                    'let': {"pondid": "$pond_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$pondid']}}},
                        {"$project": {
                            "_id": 1,
                            "alias": 1,
                            "location": 1,
                            "build_at": 1,
                            "isActive": 1,
                        }}
                    ],
                    'as': 'pond'
                }},
                {'$lookup': {
                    'from': 'pond_activation',
                    'let': {"activationid": "$pond_activation_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$eq': ['$_id', '$$activationid']}}},
                        {"$project": {
                            "_id": 1,
                            "isFinish": 1,
                            "isWaterPreparation": 1,
                            "water_level": 1,
                            "activated_at": 1
                        }}
                    ],
                    'as': 'pond_activation'
                }},
                {"$addFields": {
                    "pond": {"$first": "$pond"},
                    "pond_activation": {"$first": "$pond_activation"},
                }},
                {"$project": {
                    "updated_at": 0,
                    "created_at": 0,
                }}
            ]
            pondtreatment = PondTreatment.objects.aggregate(pipeline)
            list_pondtreatments = list(pondtreatment)
            response = json.dumps(list_pondtreatments, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity()
            farm = str(current_user['farm_id'])
            
            pond_id = request.form.get("pond_id", None)
            theDate = request.form.get('created_at', None)

            pond = Pond.objects.get(id=pond_id)
            if pond['isActive'] == False:
                response = {"message": "pond is not active"}
                response = json.dumps(response, default=str)
                return Response(response, mimetype="application/json", status=400)
            pond_activation = PondActivation.objects(
                pond_id=pond_id, isFinish=False).order_by('-activated_at').first()
            treatment_type = request.form.get("treatment_type", None)
            if treatment_type == "berat":
                fishes = request.form.get("fish", "[]")
                fishes = json.loads(fishes)
                body = {
                    "pond_id": pond_id,
                    "farm_id": farm,
                    "pond_activation_id": pond_activation.id,
                    "treatment_type": treatment_type,
                    "water_change": 100,
                    "description": request.form.get("description", None),
                }
                pondtreatment = PondTreatment(**body).save()
                id = pondtreatment.id
                # update activation and pond
                pond_deactivation_data = {
                    "isFinish": True,
                    "total_fish_harvested": request.form.get("total_fish_harvested", None),
                    "total_weight_harvested": request.form.get("total_weight_harvested", None),
                    "deactivated_description": "karantina total"
                }

                if theDate != '':
                    body['created_at'] = datetime.datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z") 
                    body['treatment_at'] = datetime.datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z") 
                    pond_deactivation_data['deactivation_at'] = datetime.datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z") 
                else :
                    three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)
                    body['created_at'] = three_months_ago
                    body['treatment_at'] = three_months_ago
                    pond_deactivation_data['deactivation_at'] = three_months_ago

                pond_activation = PondActivation.objects(
                    pond_id=pond_id, isFinish=False).order_by('-activated_at').first()
                pond_activation.update(**pond_deactivation_data)
                pond.update(**{"isActive": False, "status": "Panen"})
                for fish in fishes:
            # save fish log
                    data = {
                        "pond_id": pond_id,
                        "pond_activation_id": pond_activation.id,
                        "type_log": "deactivation",
                        "fish_type": fish['type'],
                        "fish_amount": fish['amount'],
                        "fish_total_weight": fish['weight']
                    }
                    # total_fish_harvested += fish['amount']
                    # total_weight_harvested += fish['weight']
                    fishlog = FishLog(**data).save()
                    print(data)
            elif treatment_type == "ringan":

                prob_id =request.form.get("probiotic_culture_id", None)
                carb_id = request.form.get("carbon_id", None)
                salt_id = request.form.get("salt_id", None)

                theDate = request.form.get('created_at', None)

                body = {
                    "pond_id": pond_id,
                    "farm_id": farm,
                    "pond_activation_id": pond_activation.id,
                    "treatment_type": treatment_type,
                    "description": request.form.get("description", None),
                    "water_change": request.form.get("water_change", 0),
                    "salt": request.form.get("salt", None),
                    "probiotic_culture_name": request.form.get("probiotic_culture_name", None),
                    "probiotic_culture": request.form.get("probiotic_culture", None),
                    "carbohydrate": request.form.get("carbohydrate", None),
                    "carbohydrate_type": request.form.get("carbohydrate_type", None),
                }

                if prob_id != '':
                    body['probiotic_culture_id'] = prob_id
                    get_suplemen_by_prob = SuplemenInventory.objects.get(id=prob_id)
                    get_suplemen_by_prob.amount -= float(request.form.get("probiotic_culture", None))
                    get_suplemen_by_prob.save()

                if carb_id != '':
                    body['carbon_id'] = carb_id
                    get_suplemen_by_carb = SuplemenInventory.objects.get(id=carb_id)
                    get_suplemen_by_carb.amount -= float(request.form.get("carbohydrate", None))
                    get_suplemen_by_carb.save()

                if salt_id != '':
                    body['salt_id'] = salt_id
                    get_suplemen_by_salt = SuplemenInventory.objects.get(id=salt_id)
                    get_suplemen_by_salt.amount -= float(request.form.get("salt", None))
                    get_suplemen_by_salt.save()

                if theDate != '':
                    body['created_at'] = datetime.datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z") 
                    body['treatment_at'] = datetime.datetime.strptime(theDate, "%Y-%m-%dT%H:%M:%S.%f %z") 
                else :
                    three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)
                    body['created_at'] = three_months_ago
                    body['treatment_at'] = three_months_ago

                pondtreatment = PondTreatment(**body).save()
                id = pondtreatment.id
            elif treatment_type == "pergantian air":
                body = {
                    "pond_id": pond_id,
                    "pond_activation_id": pond_activation.id,
                    "treatment_type": treatment_type,
                    "water_change": request.form.get("water_change", 0)
                }
                pondtreatment = PondTreatment(**body).save()
                id = pondtreatment.id
            else:
                response = {
                    "message": "treatment type just allow ['ringan','berat']"}
                response = json.dumps(response, default=str)
                return Response(response, mimetype="application/json", status=400)
            response = {
                "message": "success add data pond treatment", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class PondTreatmentApi(Resource):
    def put(self, id):
        try:
            body = request.form.to_dict(flat=True)
            PondTreatment.objects.get(id=id).update(**body)
            response = {
                "message": "success change data pond treatment", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def delete(self, id):
        try:
            pondtreatment = PondTreatment.objects.get(id=id).delete()
            response = {"message": "success delete pond treatment"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def get(self, id):
        try:
            pipeline = [
                {'$match': {'$expr': {'$eq': ['$_id', {'$toObjectId': id}]}}},
                {'$lookup': {
                    'from': 'pond',
                    'let': {"pondid": "$pond_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$pondid']}}},
                        {"$project": {
                            "_id": 1,
                            "alias": 1,
                            "location": 1,
                            "build_at": 1,
                            "isActive": 1,
                        }}
                    ],
                    'as': 'pond'
                }},
                {'$lookup': {
                    'from': 'pond_activation',
                    'let': {"activationid": "$pond_activation_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$eq': ['$_id', '$$activationid']}}},
                        {"$project": {
                            "_id": 1,
                            "isFinish": 1,
                            "isWaterPreparation": 1,
                            "water_level": 1,
                            "activated_at": 1
                        }}
                    ],
                    'as': 'pond_activation'
                }},
                {"$addFields": {
                    "pond": {"$first": "$pond"},
                    "pond_activation": {"$first": "$pond_activation"},
                }},
                {"$project": {
                    "updated_at": 0,
                    "created_at": 0,
                }}
            ]
            pondtreatment = PondTreatment.objects.aggregate(pipeline)
            list_pondtreatments = list(pondtreatment)
            response = json.dumps(list_pondtreatments[0], default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
