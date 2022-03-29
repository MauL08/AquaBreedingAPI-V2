from flask import Response, request
from database.models import LogFeeding
from flask_restful import Resource
import datetime


class LogFeedingsApi(Resource):
    def get(self):
        logfeedings = LogFeeding.objects().to_json()
        return Response(logfeedings, mimetype="application/json", status=200)

    def post(self):
        body = request.get_json()
        # body["time_feeding"] = datetime.strptime(
        #     body["time_feeding"], '%Y-%m-%dT%H:%M:%SZ')
        # print(body)
        logfeeding = LogFeeding(**body).save()
        id = logfeeding.id
        return {'id': str(id)}, 200


class LogFeedingApi(Resource):
    def put(self, id):
        body = request.get_json()
        LogFeeding.objects.get(id=id).update(**body)
        return '', 200

    def delete(self, id):
        logfeeding = LogFeeding.objects.get(id=id).delete()
        return '', 200

    def get(self, id):
        logFeeding = LogFeeding.objects.get(id=id).to_json()
        return Response(logFeeding, mimetype="application/json", status=200)
