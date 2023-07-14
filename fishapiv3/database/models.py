from .db import db
import datetime
from bson import json_util
from mongoengine import connect, disconnect

disconnect()
class Farm(db.Document):
    farm_name = db.StringField(required=True)
    address = db.StringField(required=True)
    breeder = db.StringField(required=True)
    coordinate = db.StringField()

class Pond(db.Document):
    shape_option = ("bundar", "persegi")

    farm_id = db.ReferenceField(Farm, required=True)
    id_int = db.SequenceField(required=True)
    alias = db.StringField(required=True)
    location = db.StringField(required=True)
    shape = db.StringField(required=True, choices=shape_option)
    material = db.StringField(required=True)
    length = db.FloatField(required=True, default=0)
    width = db.FloatField(required=True, default=0)
    status = db.StringField(required=True)
    diameter = db.FloatField(required=True, default=0)
    height = db.FloatField(required=True, default=0)
    image_name = db.StringField(required=True, default='default.jpg')
    isActive = db.BooleanField(required=True, default=False)
    pondPhDesc = db.StringField(default="Belum Diukur")
    pondPh = db.FloatField(default=None)
    pondDoDesc = db.StringField(default="Belum Diukur")
    pondDo = db.FloatField(default=None)
    pondTemp = db.FloatField(default=None)
    build_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class PondActivation(db.Document):
    id_int = db.IntField(required=True)
    pond_id = db.ReferenceField(Pond, required=True)
    isFinish = db.BooleanField(required=True, default=False)
    isWaterPreparation = db.BooleanField(required=True, default=False)
    water_level = db.FloatField(required=True, default=0)
    total_fish_harvested = db.IntField(required=True, default=0)
    total_weight_harvested = db.IntField(required=True, default=0)
    # fish_harvested = db.ArrayField(default=None)
    activated_at = db.DateTimeField(default=datetime.datetime.now)
    deactivated_at = db.DateTimeField(default=None)
    deactivated_description = db.StringField(default=None)
    constanta_oversize = db.FloatField(required=True, default=1.3)
    constanta_undersize = db.FloatField(required=True, default=0.7)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class WaterPreparation(db.Document):
    carbohydrate_type_option = ("gula", "molase", "terigu", "tapioka")

    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    carbohydrate = db.IntField(required=True)
    carbohydrate_type = db.StringField(
        required=True, choices=carbohydrate_type_option)
    salt = db.IntField(required=True)
    calcium = db.IntField(required=True)


class FishDeath(db.Document):
    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    image_name = db.StringField(required=True)
    diagnosis = db.StringField(default=datetime.datetime.now)
    death_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class FishTransfer(db.Document):
    transfer_method_option = ("basah", "kering")
    transfer_type_option = ("", "oversized_transfer", "undersized_transfer")

    origin_pond_id = db.ReferenceField(Pond, required=True)
    destination_pond_id = db.ReferenceField(Pond, required=True)
    origin_activation_id = db.ReferenceField(PondActivation, required=True)
    destination_activation_id = db.ReferenceField(
        PondActivation, required=True)
    # fish_grading_id = db.ObjectIdField(required=True, default=None)
    transfer_type = db.StringField(choices=transfer_type_option, default="")
    transfer_method = db.StringField(
        required=True, choices=transfer_method_option)
    sample_weight = db.FloatField(required=True)
    sample_long = db.FloatField(default=None)
    transfer_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class SeedInventory(db.Document):
    id_int = db.SequenceField(required=True)
    # farm_id = db.ReferenceField(Farm, required=True)
    fish_seed_category = db.StringField(required=True)
    fish_type = db.StringField(required=True)
    brand_name = db.StringField(required=True)
    amount = db.IntField(required=True)
    weight = db.IntField()
    # length = db.IntField()
    width = db.StringField()
    price = db.IntField(required=True)
    image = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class FishLog(db.Document):
    fish_type_option = ("nila hitam", "nila merah", "lele", "patin", "mas")

    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ObjectIdField(required=False, default=None)
    fish_seed_id = db.ReferenceField(SeedInventory, required=True)
    fish_death_id = db.ObjectIdField(required=False, default=None)
    fish_transfer_id = db.ObjectIdField(required=False, default=None)
    type_log = db.StringField(required=True)
    fish_type = db.StringField(required=True, choices=fish_type_option)
    fish_category = db.StringField(required=True)
    fish_amount = db.IntField(required=True)
    fish_total_weight = db.IntField(default=None)
    fish_size = db.StringField(default=None)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class FishGrading(db.Document):
    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    isOversizeTransferred = db.BooleanField(required=True, default=False)
    isUndersizeTransferred = db.BooleanField(required=True, default=False)
    fish_type = db.StringField(required=True)
    sampling_amount = db.IntField(required=True)
    avg_fish_weight = db.FloatField(required=True)
    avg_fish_long = db.FloatField(required=True)
    amount_normal_fish = db.IntField(required=True)
    amount_oversize_fish = db.IntField(required=True)
    amount_undersize_fish = db.IntField(required=True)
    grading_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class DailyWaterQuality(db.Document):
    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    ph = db.FloatField(required=True)
    do = db.FloatField(required=True)
    temperature = db.FloatField(required=True)
    week = db.IntField(defauit=None)
    dailywater_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class WeeklyWaterQuality(db.Document):

    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    floc = db.FloatField(required=True)
    nitrite = db.FloatField(Default=None)
    nitrate = db.FloatField(Default=None)
    ammonia = db.FloatField(Default=None)
    hardness = db.FloatField(Default=None)
    week = db.IntField(Default=None)
    weeklywater_at= db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class PondTreatment(db.Document):
    treatment_type_option = ("ringan", "berat", "pergantian air")
    carbohydrate_type_option = ("", "gula", "molase", "terigu", "tapioka")

    pond_id = db.ReferenceField(Pond, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    treatment_type = db.StringField(
        required=True, choices=treatment_type_option)
    water_change = db.IntField()
    salt = db.FloatField()
    probiotic_culture = db.FloatField()
    carbohydrate = db.FloatField()
    carbohydrate_type = db.StringField(
        required=True, choices=carbohydrate_type_option, default="")
    description = db.StringField(default="")
    treatment_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class OptionTable(db.Document):
    type = db.StringField(required=True)
    option = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class Breeder(db.Document):
    farm_id = db.ReferenceField(Farm, required=True)
    username = db.StringField(required=True)
    password = db.StringField(required=True)
    name = db.StringField(required=True)
    nik = db.StringField(required=True)
    phone = db.StringField(required=True)

class SeedUsed(db.Document):
    fish_seed_id = db.ReferenceField(SeedInventory, required=True)
    original_amount = db.IntField(required=True)
    usage = db.IntField(required=True)
    pond = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class FeedInventory(db.Document):
    id_int = db.SequenceField(required=True)
    feed_category = db.StringField(required=True)
    brand_name = db.StringField(required=True)
    description = db.StringField(required=True)
    price = db.IntField(required=True)
    amount = db.FloatField(required=True)
    producer = db.StringField(required=True)
    protein = db.IntField(required=True)
    carbohydrate = db.IntField(required=True)
    min_expired_period = db.IntField(required=True)
    max_expired_period = db.IntField(required=True)
    image = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class FeedUsed(db.Document):
    fish_feed_id = db.ReferenceField(FeedInventory, required=True)
    original_amount = db.FloatField(required=True)
    usage = db.FloatField(required=True)
    pond = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class FeedHistory(db.Document):
    pond_id = db.ReferenceField(Pond, required=True)
    fish_feed_id = db.ReferenceField(FeedInventory, required=True)
    pond_activation_id = db.ReferenceField(PondActivation, required=True)
    feed_dose = db.FloatField(required=True)
    feed_history_time = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class SuplemenInventory(db.Document):
    id_int = db.SequenceField(required=True)
    function = db.StringField(required=True)
    name = db.StringField(required=True)
    description = db.StringField(required=True)
    price = db.IntField(required=True)
    amount = db.FloatField(required=True)
    type = db.StringField(required=True)
    min_expired_period = db.IntField(required=True)
    max_expired_period = db.IntField(required=True)
    image = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class SuplemenUsed(db.Document):
    fish_suplemen_id = db.ReferenceField(SuplemenInventory, required=True)
    original_amount = db.FloatField(required=True)
    usage = db.FloatField(required=True)
    pond = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class ElectricInventory(db.Document):
    id_int = db.SequenceField(required=True)
    type = db.StringField(required=True)
    name = db.StringField(required=True)
    daya = db.StringField()
    price = db.IntField(required=True)
    image = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

class AssetInventory(db.Document):
    id_int = db.SequenceField(required=True)
    asset_category = db.StringField(required=True)
    name = db.StringField(required=True)
    description = db.StringField(required=True)
    amount = db.IntField(required=True)
    price = db.IntField(required=True)
    image = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

# class FeedType(db.Document):
#     fish_feed_id = db.ReferenceField(FeedInventory, required=True)
#     feed_type = db.StringField(required=True)
#     name = db.StringField(required=True)
#     protein = db.IntField(required=True)
#     carbohydrate = db.IntField(required=True)
#     created_at = db.DateTimeField(default=datetime.datetime.now)
#     updated_at = db.DateTimeField(default=datetime.datetime.now)