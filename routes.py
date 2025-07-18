from app import app
from flask import render_template,request, redirect, url_for, flash,session
from models import db,User,ParkingLot,ParkingSpot,Reservation, Vehicle
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
    
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login' ,methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    # check if user exists
    user= User.query.filter_by(username=username).first()
    if not user:
        flash('Username does not exist')
        return redirect(url_for('login'))

    # check if password is correct
    if not check_password_hash(user.passhash, password):
        flash('Incorrect password')
        return redirect(url_for('login'))

    session['user_id'] = user.id
    session['is_admin'] = user.is_admin
    session['name'] = user.name
    session['username'] = user.username
    session['address'] = user.address
    session['pincode'] = user.pincode
    flash('Login successful')
    if user.is_admin:
        return redirect(url_for('admin'))
    return redirect(url_for('user'))


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    name = request.form.get('name')
    address = request.form.get('address')
    pincode = request.form.get('pincode')
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    # confirm password
    if password != confirm_password:
        flash('Passwords do not match')
        return redirect(url_for('register')) 
    
    # check if username already exists
    user = User.query.filter_by(username=username).first() 
    if user:
        flash('Username already exists')
        return redirect(url_for('register'))
    
    # check if pincode is a valid number
    if not pincode.isdigit() or len(pincode) != 6:
        flash('Invalid pincode. It should be a 6-digit number.')
        return redirect(url_for('register'))
    
    # hash the password
    password_hash = generate_password_hash(password)    
    # create new user
    new_user = User(name=name, address=address, pincode=pincode, username=username, passhash=password_hash)
    db.session.add(new_user)
    db.session.commit()
    flash('Registration successful! Please login.')
    return redirect(url_for('login'))

# decorator for user authentication
def auth_required(f):
    @wraps(f) #create different function object
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # flash('Please login to continue')
            return redirect(url_for('login'))
        else:
            return f(*args, **kwargs)
    return decorated_function

#decorator for admin authentication
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue')
            return redirect(url_for('login'))
        user= User.query.get(session['user_id'])
        if not user.is_admin:
            flash('You do not have permission to access this page')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/logout')
@auth_required
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/admin')
@admin_required
def admin():
    parkinglots = ParkingLot.query.all()
    return render_template('admin.html', parkinglots=parkinglots) 

@app.route('/lot/add')
@admin_required
def add_lot():
    return render_template('addlot.html')

@app.route('/lot/add' ,methods=['POST'])
@admin_required
def add_lot_post():
    
    name= request.form.get('name')
    address = request.form.get('address')
    pincode = request.form.get('pincode')
    price = request.form.get('price')
    totalspots = request.form.get('totalspots')
    if not pincode.isdigit() or len(pincode) != 6:
        flash('Invalid pincode. It should be a 6-digit number.')
        return redirect(url_for('add_lot'))
    
    new_lot=ParkingLot(name=name,address=address,pincode=pincode,price_per_hour=price,total_spots=totalspots)
    db.session.add(new_lot)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/lot/<int:id>/')
@admin_required
def view_lot(id):
    return "view lot"    

@app.route('/lot/<int:id>/edit')
@admin_required
def edit_lot(id):
    parkinglot = ParkingLot.query.get(id)
    return render_template('editlot.html', parkinglot=parkinglot)

@app.route('/lot/<int:id>/edit', methods=['POST'])
@admin_required
def edit_lot_post(id):
    parkinglot = ParkingLot.query.get(id)
    parkinglot.name = request.form.get('name')
    parkinglot.address = request.form.get('address')
    parkinglot.pincode = request.form.get('pincode')
    parkinglot.price_per_hour = request.form.get('price')
    parkinglot.total_spots = request.form.get('totalspots')

    if not parkinglot.pincode.isdigit() or len(parkinglot.pincode) != 6:
        flash('Invalid pincode. It should be a 6-digit number.')
        return redirect(url_for('edit_lot', id=id))
    
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/lot/<int:id>/delete')
@admin_required
def delete_lot(id):
    parkinglot = ParkingLot.query.get(id)
    return render_template('deletelot.html', parkinglot=parkinglot)

@app.route('/lot/<int:id>/delete', methods=['POST'])
@admin_required
def delete_lot_post(id):
    parkinglot = ParkingLot.query.get(id)
    db.session.delete(parkinglot)
    db.session.commit()
    return redirect(url_for('admin'))

# User details
@app.route('/userdata')
@admin_required
def userdata():
    users = User.query.all()
    return render_template('userdata.html', users=users)


@app.route('/')
@auth_required
def index():
    user= User.query.get(session['user_id'])
    if user.is_admin:
        return redirect(url_for('admin'))
    return render_template('index.html',user=user)


@app.route('/profile')
@auth_required
def profile():
    user = {
        'Name': session['name']
    }
    return render_template("profile.html", user=user)
    

@app.route('/profile/edit')
@auth_required
def edit_profile():
    user= User.query.get(session['user_id'])
    admin= User.query.filter_by(is_admin=True).first()
    return render_template('editprofile.html',user=user)

@app.route('/profile/edit', methods=['POST'])
@auth_required
def edit_profile_post():
    user= User.query.get(session['user_id'])
    name= request.form.get('name')
    address = request.form.get('address')
    pincode = request.form.get('pincode')
    username = request.form.get('username')
    cpassword = request.form.get('cpassword')
    npassword = request.form.get('npassword')
    
    # check if current password is correct
    if not check_password_hash(user.passhash, cpassword):
        flash('Current password is incorrect')
        return redirect(url_for('profile'))
    
    if username!= user.username:
        # check if new username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists')
            return redirect(url_for('profile'))
    
    # update password if new password is provided
    if npassword:
        user.passhash = generate_password_hash(npassword)
    
    user.name = name
    user.address = address
    user.pincode = pincode
    user.username = username
    # commit changes to the database
    db.session.commit()
    flash('Profile updated successfully')
    return redirect(url_for('profile'))

@app.route('/user')
@auth_required
def user():
    parkinglots = ParkingLot.query.all()
    return render_template('user.html',parkinglots=parkinglots)
    
@app.route('/lot/<int:id>/book')
@auth_required
def book_lot(id):
    parkinglot = ParkingLot.query.get(id)
    if not parkinglot:
        flash('Parking lot not found')
        return redirect(url_for('user'))
    
    # Check if the user has already booked a spot in this lot
    # existing_reservation = Reservation.query.filter_by(user_id=session['user_id'], parkinglot_id=id).first()
    # if existing_reservation:
    #     flash('You have already booked a spot in this parking lot.')
    #     return redirect(url_for('user'))
    
    return render_template('booklot.html', parkinglot=parkinglot)
    
@app.route('/parking/history')
@auth_required
def parking_history():
    parkinglots= ParkingLot.query.all()
    return render_template('parkinghistory.html',parkinglots=parkinglots)

@app.route('/release')
@auth_required
def release():
    return render_template('release.html')