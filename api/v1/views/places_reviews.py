#!/usr/bin/python3
"""
Flask route that returns json status response
"""
from api.v1.views import app_views
from flask import abort, jsonify, request
from flasgger.utils import swag_from
from models import storage, CNC


@app_views.route('/places/<place_id>/reviews', methods=['GET', 'POST'])
@swag_from('swagger_yaml/reviews_by_place.yml', methods=['GET', 'POST'])
def reviews_per_place(place_id=None):
    """
        reviews route to handle http method for requested reviews by place
    """
    place_obj = storage.get('Place', place_id)

    if request.method == 'GET':
        if place_obj is None:
            abort(404, 'Not found')
        all_reviews = storage.all('Review')
        place_reviews = [obj.to_json() for obj in all_reviews.values()
                         if obj.place_id == place_id]
        return jsonify(place_reviews)

    if request.method == 'POST':
        if place_obj is None:
            abort(404, 'Not found')
        req_json = request.get_json()
        if req_json is None:
            abort(400, 'Not a JSON')
        user_id = req_json.get("user_id")
        if user_id is None:
            abort(400, 'Missing user_id')
        user_obj = storage.get('User', user_id)
        if user_obj is None:
            abort(404, 'Not found')
        if req_json.get('text') is None:
            abort(400, 'Missing text')
        Review = CNC.get("Review")
        req_json['place_id'] = place_id
        new_object = Review(**req_json)
        new_object.save()
        return jsonify(new_object.to_json()), 201


@app_views.route('/reviews/<review_id>', methods=['GET', 'DELETE', 'PUT'])
@swag_from('swagger_yaml/reviews_id.yml', methods=['GET', 'DELETE', 'PUT'])
def reviews_with_id(review_id=None):
    """
        reviews route to handle http methods for given review by ID
    """
    review_obj = storage.get('Review', review_id)

    if request.method == 'GET':
        if review_obj is None:
            abort(404, 'Not found')
        return jsonify(review_obj.to_json())

    if request.method == 'DELETE':
        if review_obj is None:
            abort(404, 'Not found')
        review_obj.delete()
        del review_obj
        return jsonify({}), 200

    if request.method == 'PUT':
        if review_obj is None:
            abort(404, 'Not found')
        req_json = request.get_json()
        if req_json is None:
            abort(400, 'Not a JSON')
        review_obj.bm_update(req_json)
        return jsonify(review_obj.to_json()), 200#!/usr/bin/python3
"""
Review model hold the endpoint (route) and their respective view functions
"""
from api.v1.views import (app_views, Review, storage)
from flask import (abort, jsonify, request)


@app_views.route("/places/<place_id>/reviews", methods=["GET"],
                 strict_slashes=False)
def all_reviews(place_id):
    """Example endpoint returning a list of all reviews
    Retrieves a list of all reviews associated with a place
    ---
    parameters:
      - name: place_id
        in: path
        type: string
        enum: ['279b355e-ff9a-4b85-8114-6db7ad2a4cd2']
        required: true
        default: '279b355e-ff9a-4b85-8114-6db7ad2a4cd2'
    definitions:
      State:
        type: object
        properties:
          __class__:
            type: string
            description: The string of class object
          created_at:
            type: string
            description: The date the object created
          id:
            type: string
            description: the id of the review
          place_id:
            type: string
            description: the id of the place
          text:
            type: string
            description: the text of the review
          updated_at:
            type: string
            description: The date the object was updated
          user_id:
            type: string
            description: The user id
            items:
              $ref: '#/definitions/Color'
      Color:
        type: string
    responses:
      200:
        description: A list of dictionaries of all reviews objects
        schema:
          $ref: '#/definitions/State'
        examples:
            [{"__class__": "Review",
              "created_at": "2017-03-25T02:17:07",
              "id": "3f54d114-582d-4dab-8559-f0682dbf1fa6",
              "place_id": "279b355e-ff9a-4b85-8114-6db7ad2a4cd2",
              "text": "Really nice place and really nice people. Secluded.",
              "updated_at": "2017-03-25T02:17:07",
              "user_id": "887dcd8d-d5ee-48de-9626-73ff4ea732fa"}]
    """
    place = storage.get("Place", place_id)
    if place is None:
        abort(404)
    reviews = [review.to_json() for review in place.reviews]
    return jsonify(reviews)


@app_views.route("/reviews/<review_id>", methods=["GET"],
                 strict_slashes=False)
def one_review(review_id):
    """Example endpoint returning a list of one reivew
    Retrieves a list of one review associated with a place
    ---
    parameters:
      - name: place_id
        in: path
        type: string
        enum: ["3f54d114-582d-4dab-8559-f0682dbf1fa6"]
        required: true
        default: "3f54d114-582d-4dab-8559-f0682dbf1fa6"
    definitions:
      State:
        type: object
        properties:
          __class__:
            type: string
            description: The string of class object
          created_at:
            type: string
            description: The date the object created
          id:
            type: string
            description: the id of the review
          place_id:
            type: string
            description: the id of the place
          text:
            type: string
            description: written review
          updated_at:
            type: string
            description: The date the object was updated
          user_id:
            type: string
            description: The user id
            items:
              $ref: '#/definitions/Color'
      Color:
        type: string
    responses:
      200:
        description: A list of a dictionary of a Review objects
        schema:
          $ref: '#/definitions/State'
        examples:
            [{"__class__": "Review",
              "created_at": "2017-03-25T02:17:07",
              "id": "3f54d114-582d-4dab-8559-f0682dbf1fa6",
              "place_id": "279b355e-ff9a-4b85-8114-6db7ad2a4cd2",
              "text": "Really nice place and really nice people. Secluded.",
              "updated_at": "2017-03-25T02:17:07",
              "user_id": "887dcd8d-d5ee-48de-9626-73ff4ea732fa"}]
    """
    review = storage.get("Review", review_id)
    if review is None:
        abort(404)
    return jsonify(review.to_json())


@app_views.route("/reviews/<review_id>", methods=["DELETE"],
                 strict_slashes=False)
def delete_one_review(review_id):
    """Example endpoint deleting one review
    Deletes a review based on the place_id
    ---
    definitions:
      Review:
        type: object
      Color:
        type: string
      items:
        $ref: '#/definitions/Color'

    responses:
      200:
        description: An empty dictionary
        schema:
          $ref: '#/definitions/City'
        examples:
            {}
    """
    review = storage.get("Review", review_id)
    if review is None:
        abort(404)
    storage.delete(review)
    return jsonify({}), 200


@app_views.route("/places/<place_id>/reviews", methods=["POST"],
                 strict_slashes=False)
def create_review(place_id):
    """Example endpoint creates one review
    Creates one review associated with a place_id based on the JSON body
    ---
    parameters:
      - name: place_id
        in: path
        type: string
        enum: ["3f54d114-582d-4dab-8559-f0682dbf1fa6"]
        required: true
        default: "3f54d114-582d-4dab-8559-f0682dbf1fa6"
    definitions:
      State:
        type: object
        properties:
          __class__:
            type: string
            description: The string of class object
          created_at:
            type: string
            description: The date the object created
          id:
            type: string
            description: the id of the review
          place_id:
            type: string
            description: the id of the place
          text:
            type: string
            description: written review
          updated_at:
            type: string
            description: The date the object was updated
          user_id:
            type: string
            description: The user id
            items:
              $ref: '#/definitions/Color'
      Color:
        type: string
    responses:
      201:
        description: A list of a dictionary of a Review objects
        schema:
          $ref: '#/definitions/State'
        examples:
            [{"__class__": "Review",
              "created_at": "2017-03-25T02:17:07",
              "id": "3f54d114-582d-4dab-8559-f0682dbf1fa6",
              "place_id": "279b355e-ff9a-4b85-8114-6db7ad2a4cd2",
              "text": "Really nice place and really nice people. Secluded.",
              "updated_at": "2017-03-25T02:17:07",
              "user_id": "887dcd8d-d5ee-48de-9626-73ff4ea732fa"}]
    """
    try:
        r = request.get_json()
    except:
        r = None
    if r is None:
        return "Not a JSON", 400
    if "user_id" not in r.keys():
        return "Missing user_id", 400
    if "text" not in r.keys():
        return "Missing text", 400
    place = storage.get("Place", place_id)
    if place is None:
        abort(404)
    user = storage.get("User", r["user_id"])
    if user is None:
        abort(404)
    review = Review(**r)
    review.place_id = place_id
    review.save()
    return jsonify(review.to_json()), 201


@app_views.route("/reviews/<review_id>", methods=["PUT"],
                 strict_slashes=False)
def update_review(review_id):
    """Example endpoint creates one review
    Creates one review associated with a place_id based on the JSON body
    ---
    parameters:
      - name: place_id
        in: path
        type: string
        enum: ["3f54d114-582d-4dab-8559-f0682dbf1fa6"]
        required: true
        default: "3f54d114-582d-4dab-8559-f0682dbf1fa6"
    definitions:
      State:
        type: object
        properties:
          __class__:
            type: string
            description: The string of class object
          created_at:
            type: string
            description: The date the object created
          id:
            type: string
            description: the id of the review
          place_id:
            type: string
            description: the id of the place
          text:
            type: string
            description: written review
          updated_at:
            type: string
            description: The date the object was updated
          user_id:
            type: string
            description: The user id
            items:
              $ref: '#/definitions/Color'
      Color:
        type: string
    responses:
      200:
        description: A list of a dictionary of a Review objects
        schema:
          $ref: '#/definitions/State'
        examples:
            [{"__class__": "Review",
              "created_at": "2017-03-25T02:17:07",
              "id": "3f54d114-582d-4dab-8559-f0682dbf1fa6",
              "place_id": "279b355e-ff9a-4b85-8114-6db7ad2a4cd2",
              "text": "Really nice place and really nice people. Secluded.",
              "updated_at": "2017-03-25T02:17:07",
              "user_id": "887dcd8d-d5ee-48de-9626-73ff4ea732fa"}]
    """
    review = storage.get("Review", review_id)
    if review is None:
        abort(404)
    try:
        r = request.get_json()
    except:
        r = None
    if r is None:
        return "Not a JSON", 400
    for k in ("id", "user_id", "place_id", "created_at", "updated_at"):
        r.pop(k, None)
    for key, value in r.items():
        setattr(review, key, value)
    review.save()
    return jsonify(review.to_json()), 200
