#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants')
def restaurants():
    restaurants = []

    for restaurant in Restaurant.query.all():
        restaurant_dict = {
            "address": restaurant.address,
            "id": restaurant.id,
            "name" : restaurant.name,
        }
        restaurants.append(restaurant_dict)

    response = make_response(
         jsonify(restaurants),
         200
     )   
    return response

@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)

    if restaurant is None:
        response_body = {
            "error": "Restaurant not found"
        }
        return make_response(jsonify(response_body), 404)
    
    if request.method == 'GET':
        restaurant_dict = restaurant.to_dict()

        response = make_response(
            restaurant_dict,
            200
        )

        return response
    
    elif request.method == 'DELETE':
         db.session.delete(restaurant)
         db.session.commit()

    response_body = {
        "delete_successful": True,
        "message": "Restaurant deleted."
    }

    response = make_response(
            response_body,
            204
        )

    return response

#pizza METHODS
@app.route('/pizzas')
def pizzas():
    pizzas = []

    for pizza in Pizza.query.all():
        pizza_dict = {
            "id": pizza.id,
            "ingredients":pizza.ingredients,
            "name" : pizza.name,
            
        }
        pizzas.append(pizza_dict)

    response = make_response(
         jsonify(pizzas),
         200
     )   
    return response


@app.route('/restaurant_pizzas', methods=['POST'])
def add_restaurant_pizza():
    data = request.get_json()
    if not data:
        return jsonify({"errors": ["No data provided"]}), 400
    
    
    try:
        price = data['price']
        pizza_id = data['pizza_id']
        restaurant_id = data['restaurant_id']
    
        if price not in range(1,31):
            raise ValueError("validation errors")

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not pizza or not restaurant:
            raise ValueError("validation errors")

    #CREATING A NEW RESTAURANT PIZZA OBJECT
        new_restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )

        db.session.add(new_restaurant_pizza)
        db.session.commit()

    

        response = {
            "id": new_restaurant_pizza.id,
            "price": new_restaurant_pizza.price,
            "pizza_id": new_restaurant_pizza.pizza_id,
            "restaurant_id": new_restaurant_pizza.restaurant_id,
            "pizza": new_restaurant_pizza.pizza.to_dict(), 
            "restaurant": new_restaurant_pizza.restaurant.to_dict()
        }
    
        return jsonify(response), 201

    except ValueError as ve:
        return jsonify({"errors": [str(ve)]}), 400
    
    except Exception as e:
        return jsonify({"errors": ["An unexpected error occurred"]}), 500



if __name__ == "__main__":
    app.run(port=5555, debug=True)
