from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, verify_jwt_in_request, get_jwt
from flask import request, render_template, redirect, url_for, Blueprint, jsonify, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from model.db import User, Supplier, TokenBlocklist, db
from functools import wraps
from datetime import datetime, timedelta

login_page = Blueprint("login_page", __name__)
auth_bp = Blueprint("auth_bp", __name__)

@login_page.route('/login')
def login():
    return render_template("login.html")

jwt = JWTManager()

# Separate identity handling for managers and suppliers
@jwt.user_identity_loader
def user_identity_lookup(user):
    # We're now passing string identities directly, but keep this for backward compatibility
    if isinstance(user, User):
        return f"manager_{user.id}"
    elif isinstance(user, Supplier):
        return f"supplier_{user.id}"
    return user  # Already formatted string or other value

@jwt.additional_claims_loader
def add_claims_to_access_token(identity):
    print(f"Adding claims for identity: {identity}")
    
    # Check if it's a manager identity
    if isinstance(identity, str) and identity.startswith("manager_"):
        try:
            user_id = int(identity.split("_")[1])
            user = User.query.get(user_id)
            if user:
                print(f"Adding manager claims for ID {user_id}")
                return {
                    'user_type': 'manager',
                    'email': user.email,
                    'user_id': user_id,
                    'manager_name': user.u_name
                }
        except (IndexError, ValueError) as e:
            print(f"Error parsing manager identity: {e}")
    
    # Check if it's a supplier identity
    elif isinstance(identity, str) and identity.startswith("supplier_"):
        try:
            supplier_id = int(identity.split("_")[1])
            supplier = Supplier.query.get(supplier_id)
            if supplier:
                print(f"Adding supplier claims for ID {supplier_id}")
                return {
                    'user_type': 'supplier',
                    'email': supplier.email,
                    'supplier_id': supplier_id,
                    'supplier_name': supplier.s_name
                }
        except (IndexError, ValueError) as e:
            print(f"Error parsing supplier identity: {e}")
    
    print(f"No valid identity found for: {identity}")
    return {}

def manager_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            identity = get_jwt_identity()
            
            print(f"Manager required - Identity: {identity}")
            print(f"Manager required - Claims: {claims}")
            
            if claims.get('user_type') != 'manager':
                print(f"Access denied: user_type is {claims.get('user_type')}, not manager")
                return jsonify(message="Manager access required"), 403
                
            return fn(*args, **kwargs)
        except Exception as e:
            print(f"JWT verification error in manager_required: {e}")
            if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json':
                return jsonify(message="Authentication required", error=str(e)), 401
            return redirect(url_for('login_page.login'))
    return wrapper

def supplier_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            identity = get_jwt_identity()
            
            print(f"Supplier required - Identity: {identity}")
            print(f"Supplier required - Claims: {claims}")
            
            if claims.get('user_type') != 'supplier':
                print(f"Access denied: user_type is {claims.get('user_type')}, not supplier")
                return jsonify(message="Supplier access required"), 403
                
            return fn(*args, **kwargs)
        except Exception as e:
            print(f"JWT verification error in supplier_required: {e}")
            if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json':
                return jsonify(message="Authentication required", error=str(e)), 401
            return redirect(url_for('login_page.login'))
    return wrapper

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Try manager login first
    user = User.query.filter(User.email == data.get('email')).first()
    if user and (user.verify_password(data.get('password'))):
        print(f"Manager login successful: user_id={user.id}")
        
        # Create a manager identity string instead of passing the User object
        manager_identity = f"manager_{user.id}"
        
        # Create tokens with the manager identity string
        access_token = create_access_token(identity=manager_identity)
        refresh_token = create_refresh_token(identity=manager_identity)
        
        print(f"Created access token for manager: {access_token[:20]}...")
        
        response = jsonify({
            'message': 'Login Successfully',
            'tokens': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user_type': 'manager'
            },
            'redirect_url': url_for("dashBoard.manager_dashboard"),
        })
        
        response.set_cookie('access_token_cookie', access_token, 
                    httponly=True, 
                    secure=False,  # Set to True in production with HTTPS
                    samesite='Lax', 
                    max_age=60*60*24*15,  # 15 days
                    path='/')
        return response

    # Try supplier login
    supplier = Supplier.query.filter(Supplier.email == data.get('email')).first()
    if supplier and (supplier.verify_password(data.get('password'))):
        print(f"Supplier login successful: supplier_id={supplier.id}")
        
        # Create a supplier identity string
        supplier_identity = f"supplier_{supplier.id}"
        
        # Create tokens with the supplier identity string
        access_token = create_access_token(identity=supplier_identity)
        refresh_token = create_refresh_token(identity=supplier_identity)
        
        print(f"Created access token for supplier: {access_token[:20]}...")
        
        response = jsonify({
            'message': 'Login Successfully',
            'tokens': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user_type': 'supplier'
            },
            'redirect_url': url_for("dashBoard.supplier_dashboard"),
        })
        
        response.set_cookie('access_token_cookie', access_token, 
                    httponly=True, 
                    secure=False,  # Set to True in production with HTTPS
                    samesite='Lax', 
                    max_age=60*60*24*15,  # 15 days
                    path='/')
        return response

    return jsonify({'message': 'Invalid Email or Password'}), 401

@auth_bp.route('/test-auth', methods=['GET'])
@jwt_required()
def test_auth():
    print("Request Headers:", {k: v for k, v in request.headers.items()})
    
    identity = get_jwt_identity()
    claims = get_jwt()
    
    print(f"test-auth identity: {identity}")
    print(f"test-auth claims: {claims}")
    
    return jsonify({
        'message': 'Authorization successful',
        'identity': identity,
        'user_type': claims.get('user_type')
    }), 200

@auth_bp.route('/check-token', methods=['GET'])
def check_token():
    auth_header = request.headers.get('Authorization', 'None')
    access_token_cookie = request.cookies.get('access_token_cookie', 'None')
    user_type = None
    identity = None
    
    print(f"check-token - Auth header: {auth_header[:20] if auth_header != 'None' else 'None'}")
    print(f"check-token - Cookie: {access_token_cookie[:20] if access_token_cookie != 'None' else 'None'}")
    
    try:
        verify_jwt_in_request(optional=True)
        claims = get_jwt()
        identity = get_jwt_identity()
        user_type = claims.get('user_type')
        print(f"check-token - JWT verified successfully")
        print(f"check-token - Identity: {identity}")
        print(f"check-token - Claims: {claims}")
    except Exception as e:
        print(f"Exception in check-token: {e}")
    
    return jsonify({
        'has_auth_header': auth_header != 'None',
        'has_auth_cookie': access_token_cookie != 'None',
        'user_type': user_type,
        'identity': identity,
        'headers': {k: v for k, v in request.headers.items() if k.lower() in ['authorization', 'content-type', 'accept']}
    }), 200

@auth_bp.route('/whoami', methods=['GET'])
@jwt_required()
def whoami():
    identity = get_jwt_identity()
    claims = get_jwt()
    
    print(f"whoami - Identity: {identity}")
    print(f"whoami - Claims: {claims}")
    
    user_info = {
        'identity': identity,
        'user_type': claims.get('user_type'),
    }
    
    # Add additional user details based on user type
    if claims.get('user_type') == 'manager':
        user_info['user_id'] = claims.get('user_id')
        user_info['email'] = claims.get('email')
        user_info['user_name'] = (claims.get('manager_name')).title()
    elif claims.get('user_type') == 'supplier':
        user_info['supplier_id'] = claims.get('supplier_id')
        user_info['email'] = claims.get('email')
        user_info['user_name'] = (claims.get('supplier_name')).title()
    
    return jsonify(user_info), 200

@auth_bp.get('/logout')
@jwt_required()
def logout_user():
    jwt = get_jwt()

    jti = jwt['jti']

    token_b = TokenBlocklist(jti=jti)

    token_b.save()

    return redirect(url_for('login_page.login'))

@jwt.token_in_blocklist_loader
def token_in_blocklist(jwt_header, jwt_data):
    jti = jwt_data['jti']

    token  = db.session.query(TokenBlocklist).filter(TokenBlocklist.jti == jti).scalar()

    return token is not None