from app import app
from flask import render_template,request, redirect, url_for, flash,session
from models import db,User,ParkingLot,ParkingSpot,Reservation, Vehicle
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
    
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
            return redirect(url_for('user'))
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
    return render_template('lot/addlot.html')

@app.route('/lot/add' ,methods=['POST'])
@admin_required
def add_lot_post():
    # creating lot
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
    totalspots = int(totalspots)  # Convert to integer 
    # creating parking spots
    for i in range(1, totalspots + 1):
        spot_number = i
        new_spot = ParkingSpot(lot_id=new_lot.id, spot_number=spot_number, is_occupied=False)
        db.session.add(new_spot)

    db.session.commit()
    flash("Parking lot and spots created successfully!")
    return redirect(url_for('admin')) 

@app.route('/lot/<int:id>/edit')
@admin_required
def edit_lot(id):
    parkinglot = ParkingLot.query.get(id)
    return render_template('lot/editlot.html', parkinglot=parkinglot)

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

    updated_spots = int(request.form.get('totalspots'))
    current_spots = ParkingSpot.query.filter_by(lot_id=id).count()
    if updated_spots > current_spots:
        # Add new parking spots
        for i in range(current_spots + 1, updated_spots + 1):
            new_spot = ParkingSpot(lot_id=id, spot_number=i, is_occupied=False)
            db.session.add(new_spot)

    elif updated_spots < current_spots:
        spots_to_delete = (ParkingSpot.query.filter_by(lot_id=id).order_by(ParkingSpot.spot_number.desc()).limit(current_spots - updated_spots).all())
        for spot in spots_to_delete:
            db.session.delete(spot)

    db.session.commit()
    flash('Parking lot updated successfully')
    return redirect(url_for('admin'))

@app.route('/lot/<int:id>/delete')
@admin_required
def delete_lot(id):
    parkinglot = ParkingLot.query.get(id)
    return render_template('lot/deletelot.html', parkinglot=parkinglot)


@app.route('/lot/<int:id>/delete', methods=['POST'])
@admin_required
def delete_lot_post(id):
    parkinglot = ParkingLot.query.get(id)
    occupied_spot=next((s.id for s in parkinglot.spots if s.is_occupied), None)
    if occupied_spot:
        flash("You can't delete the lot as spot is occupied in this lot.")
        return redirect(url_for('admin'))

    # Delete parking lot if there is no spot occupied
    db.session.delete(parkinglot)
    db.session.commit()
    return redirect(url_for('admin'))

# User details
@app.route('/userdata')
@admin_required
def userdata():
    users = User.query.all()
    return render_template('user/userdata.html', users=users)


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
    user = User.query.get(session['user_id'])
    return render_template("profile.html", user=user)
    

@app.route('/profile/edit')
@auth_required
def edit_profile():
    user= User.query.get(session['user_id'])
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
    return render_template('user/user.html',parkinglots=parkinglots)
    
@app.route('/lot/<int:id>/book')
@auth_required
def book_lot(id):
    parkinglot = ParkingLot.query.get(id)
    vehicles = Vehicle.query.filter_by(user_id=session['user_id']).all()
    spot = next((s.id for s in parkinglot.spots if not s.is_occupied), None)
    if not spot:
        flash('No vacant spots available in this lot.')
        return redirect(url_for('user'))
    if not vehicles:
        flash('No vehicles found. Please add a vehicle first.')
        return redirect(url_for('vehicle'))
    if not parkinglot:
        flash('Parking lot not found')
        return redirect(url_for('user'))
    return render_template('lot/booklot.html', parkinglot=parkinglot,vehicles=vehicles, spot=spot)


@app.route('/lot/<int:id>/book', methods=['POST'])
@auth_required
def book_lot_post(id):
    lot_id = request.form.get('lot_id')
    vehicle_id = request.form.get('vehicleid')
    spot_id= int(request.form.get('spotid'))

    # Validate vehicle 
    vehicle = Vehicle.query.filter_by(id=vehicle_id, user_id=session['user_id']).first()
    if not vehicle:
        flash(f'Vehicle {vehicle_id} not found or not owned by the user.')
        return redirect(url_for('vehicle')) 
    
    # timestamp
    # timestamp=now.strftime("%H:%M:%S")
    
    # Check if the user has already booked for given vehicle
    existing_reservation = Reservation.query.filter_by(user_id=session['user_id'], lot_id=id,vehicle_id=vehicle.id).first()
    if existing_reservation:
        flash(f'You have already booked a spot for vehicle : {vehicle.vehicle_number} in this parking lot.')
        return redirect(url_for('parking_history'))

    # Create reservation
    reservation = Reservation(
        user_id=session['user_id'],
        lot_id=lot_id,
        spot_id=spot_id,
        vehicle_id=vehicle.id,
        parking_timestamp=datetime.now(),
        leaving_timestamp=None,
        total_cost=None
    )
    spot=ParkingSpot.query.filter_by(id=spot_id).first()
    # Mark the spot as occupied
    spot.is_occupied = True
    db.session.add(reservation)
    db.session.commit()

    flash(f'Spot successfully reserved ')
    return redirect(url_for('user'))

@app.route('/reserved/<int:id>/view')
@admin_required
def view_reserve(id):
    reservation=Reservation.query.get(id)
    leaving_timestamp = datetime.now()
    parking_timestamp= reservation.parking_timestamp

    duration = leaving_timestamp - parking_timestamp
    hrs = duration.total_seconds() / 3600
    est_cost = round(hrs * reservation.parkinglot.price_per_hour, 2)
    return render_template('spot/occupiedspot.html',reservation=reservation,est_cost=est_cost)


@app.route('/parking/history')
@auth_required
def parking_history():
    reservations=Reservation.query.filter_by(user_id=session['user_id'],leaving_timestamp=None).all()
    return render_template('user/parkinghistory.html',reservations=reservations)

@app.route('/spot/<int:id>/release')
@auth_required
def release(id):
    reservation=Reservation.query.get(id)
    leaving_timestamp = datetime.now()
    parking_timestamp= reservation.parking_timestamp

    duration = leaving_timestamp - parking_timestamp
    hrs = duration.total_seconds() / 3600
    cost = round(hrs * reservation.parkinglot.price_per_hour, 2)

    return render_template('spot/release.html',reservation=reservation,l_timestamp=leaving_timestamp,cost=cost)

@app.route('/spot/<int:id>/release', methods=['POST'])
@auth_required
def release_post(id):
    reservation = Reservation.query.get(id)
    l_str=request.form.get('l_timestamp') 
    # converting str to datetime
    reservation.leaving_timestamp = datetime.fromisoformat(l_str)
    reservation.total_cost=request.form.get('cost')
    spot=ParkingSpot.query.filter_by(id=reservation.spot_id).first()
    # Delete parking lot
    spot.is_occupied=False
    db.session.commit()
    flash('Spot released successfully')
    return redirect(url_for('parking_history'))


@app.route('/vehicle')
@auth_required
def vehicle():
    vehicles=Vehicle.query.filter_by(user_id=session['user_id']).all()
    return render_template('user/vehicle.html',vehicles=vehicles)


@app.route('/vehicle/add' )
@auth_required
def add_vehicle():
    return render_template('user/addvehicle.html') 

@app.route('/vehicle/add', methods=['POST'])
@auth_required  
def add_vehicle_post():
    user_id = session['user_id']
    vehicle_number = request.form.get('vehicleno')
    db.session.add(Vehicle(user_id=user_id, vehicle_number=vehicle_number))
    db.session.commit()
    flash('Vehicle added successfully')
    return redirect(url_for('vehicle'))

# searching lot
@app.route('/search')
@admin_required
def search_lot():
    return render_template('lot/searchlot.html')


#-----------------------------  spot--------------------------------------


@app.route('/admin/deletespot/<int:id>')
@admin_required
def delete_spot(id):
    spot=ParkingSpot.query.get(id)
    return render_template('spot/deletespot.html',spot=spot)