from flask import render_template, Blueprint, jsonify, request
import requests
import os
from model.db import *
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint


contact_route = Blueprint("contact", __name__)

contact_api_route = apiBlueprint('contact_api_route', __name__, url_prefix='/api/contact', description='handle everything related to contacts')


@contact_route.route("/contact")
def contact():
    return render_template("contact.html")


@contact_api_route.route('/postReview')
class Review(MethodView):

    def post(self):
        data = request.get_json()
        print(data)

        try:
            title = data.get('title')
            feedback = data.get('feed_back')

            newReview = Feedback(feedback_name=title, feedbac_data=feedback, date_submitted=datetime.now())
            db.session.add(newReview)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'error uploading review'})

        return jsonify({'message': 'Review sent Successfully'}), 201


@contact_api_route.route('/getReview')
class getReview(MethodView):

    def get(self):
        reviews = Feedback.query.all()
        reviews = [{
            'id': review.id,
            'name': review.feedback_name,
            'date': review.date_submitted.strftime("%Y-%m-%d"),
        } for review in reviews]

        return jsonify(reviews), 200
    

