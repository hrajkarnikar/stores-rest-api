from typing import Dict, List
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required, 
    fresh_jwt_required
)
from models.item import ItemModel

BLANK_ERROR = "'{}' cannot be blank."

class Item(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help=BLANK_ERROR.format('price')
    )

    parser.add_argument('store_id',
        type=int,
        required=True,
        help=BLANK_ERROR.format('store id')
    )
    
    @classmethod
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)

        if(item):
            return item.json()
        
        return {'message': 'Item not found'}, 404

    
    @classmethod
    @fresh_jwt_required
    def post(cls, name: str):
        
        if ItemModel.find_by_name(name):
            return {'message': "An item with '{}' already exists.".format(name)}, 400

        data = Item.parser.parse_args()

        #data = request.get_json()
        item = ItemModel(name, **data)
        
        try:
            item.save_to_db()
        except:
            return {"message": "An error occurred inserting the item"}, 500

        return item.json(), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        
        item = ItemModel.find_by_name(name)

        if item:
            item.delete_from_db()

        return {'message': 'Item deleted'}

    @classmethod
    def put(cls, name: str):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data['price']
            item.store_id = data['store_id']
        
        item.save_to_db()

        return item.json()

   


class ItemList(Resource):

    @classmethod
    def get(cls) -> Dict:
        
        return {
            'items':[item.json() for item in ItemModel.find_all()],
            'message': 'More data available if you log in.'
        }
        #return {'items': list(map(lambda x:x.json(), ItemModel.query.all()))}