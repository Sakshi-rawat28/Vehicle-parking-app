from flask_restful import Resource, Api
from app import app
from models import ParkingLot, db
api = Api(app)

class Lot(Resource):
    def get(self):
        parkinglots= ParkingLot.query.all()
        return {'parkinglots': [
            {
                'id': lot.id,
                'name': lot.name,
                'address': lot.address,
                'pincode': lot.pincode,
                'total_spots': lot.total_spots,
                'price_per_hour': lot.price_per_hour,
                'occupied_spots': sum(1 for spot in lot.spots if spot.is_occupied),
                'available_spots': lot.total_spots - sum(1 for spot in lot.spots if spot.is_occupied)
            } for lot in parkinglots
        ]}

api.add_resource(Lot, '/api/parking_lot')