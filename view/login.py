from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import request, render_template, redirect, url_for, Blueprint, jsonify, flash
from werkzeug.security import check_password_hash, generate_password_hash
from model.db import User, Supplier
from functools import wraps


login_page = Blueprint("login_page", __name__)

@login_page.route('/')
def login():
    return render_template("login.html")

login_manager = LoginManager()
login_manager.login_view = "login_page.login"

auth_bp = Blueprint("auth_bp", __name__)


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if user:
        return user
    
    return Supplier.query.get(int(user_id))  # Check in Supplier model


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.l_password, password):
            login_user(user)
            return jsonify({"redirect_url": url_for("dashBoard.manager_dashboard")})

        supplier = Supplier.query.filter_by(email=email).first()
        if supplier and check_password_hash(supplier.l_password, password):
            login_user(supplier)
            return jsonify({"redirect_url": url_for("dashBoard.supplier_dashboard")})

        return jsonify({"error": "Invalid email or password"}), 401

    return render_template("login.html")





@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()  # Logs out the current user
    return redirect(url_for("login_page.login"))


def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # Return JSON error for all requests
            return jsonify({"error": "Authentication required", "code": 401}), 401
            
        if not isinstance(current_user, User):
            # Return JSON error when manager access is required
            return jsonify({"error": "Access forbidden. Manager privileges required.", "code": 403}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def supplier_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # Return JSON error for all requests
            return jsonify({"error": "Authentication required", "code": 401}), 401
            
        if not isinstance(current_user, Supplier):
            # Return JSON error when supplier access is required
            return jsonify({"error": "Access forbidden. Supplier privileges required.", "code": 403}), 403
            
        return f(*args, **kwargs)
    return decorated_function

# Function to get current user info as dictionary
def get_current_user_info():
    if not current_user.is_authenticated:
        return None
    
    # Check user type and return appropriate info
    if hasattr(current_user, 'u_name'):  # Manager user
        return {
            'id': current_user.id,
            'name': current_user.u_name,
            'user_type': 'manager'
        }
    else:  # Supplier user
        return {
            'id': current_user.id,
            'name': current_user.s_name,
            'user_type': 'supplier'
        }

# Example API endpoint to get current user info
@auth_bp.route("/user-info")
@login_required
def user_info():
    user_data = get_current_user_info()
    if user_data:
        return jsonify(user_data)
    return jsonify({"error": "User not authenticated"}), 401