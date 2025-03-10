from flask import render_template, Blueprint, jsonify, request
import requests
import os
from model.db import *
from flask.views import MethodView
from flask_smorest import Blueprint as apiBlueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from view.login_new import manager_required, supplier_required


feedback_route = Blueprint("feedback", __name__)
feedback_api_route = apiBlueprint('feedback_api_route', __name__, url_prefix='/api/feedback', description='handle everything related to feedback')


@feedback_route.route("/feedback")
@manager_required
def feedback():
    return render_template("feedback.html")


@feedback_api_route.route('/getReview')
class getReview(MethodView):

    @jwt_required()
    @manager_required
    def get(self):
        reviews = Feedback.query.all()
        reviews = [{
            'id': review.id,
            'name': review.feedback_name,
            'date': review.date_submitted.strftime("%Y-%m-%d"),
        } for review in reviews]

        return jsonify(reviews), 200
    
@feedback_api_route.route('/delReview')
class delReview(MethodView):

    def delete(self):
        id  = request.args.get('id')

        review = Feedback.query.filter(Feedback.id == id).first()

        try:
            db.session.delete(review)
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Error deleting review'}), 500
        db.session.commit()
        return jsonify({'message': 'Review deleted successfully'}), 200

@feedback_api_route.route('/specReview')
class specReview(MethodView):

    def get(self):
        id  = request.args.get('id')

        review = Feedback.query.filter(Feedback.id == id).first()
        review = {
            'id': review.id,
            'content': review.feedbac_data,
        }

        return jsonify(review), 200
