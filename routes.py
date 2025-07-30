from app import app
from flask import render_template,request, redirect, url_for, flash,session
from models import db,User,ParkingLot,ParkingSpot,Reservation, Vehicle
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend suitable for Flask
import matplotlib.pyplot as plt


#----------------------------------------- Decorators-----------------------------

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


#--------------------------------- Index ----------------------------------------------

@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.is_admin:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('user'))
    return render_template('index.html')


#-------------------------------- Login  ---------------------------------------------------
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

#------------------------------------ Register ---------------------------------------

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


#------------------------------------------------- Profile --------------------------------
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


#-------------------------------------- Logout ----------------------------------

@app.route('/logout')
@auth_required
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


#---------------------------------------- Admin  -----------------------------------
@app.route('/admin')
@admin_required
def admin():
    parkinglots = ParkingLot.query.all()

    parameter= request.args.get('parameter')
    query= request.args.get('query')

    parameters= {
        'default':'Search by ',
        'lotname' : 'Lot name',
        'location' :'Location',
        'pincode' : 'Pincode',
        'lotid': 'Lot ID',
        'totalspot': 'Total Spots'
    }
    
    if parameter and query:
        try:
            if parameter == 'lotname':
                parkinglots = ParkingLot.query.filter(ParkingLot.name.ilike(f'%{query}%')).all()
            elif parameter == 'location':
                parkinglots = ParkingLot.query.filter(ParkingLot.address.ilike(f'%{query}%')).all()
            elif parameter == 'pincode':
                parkinglots = ParkingLot.query.filter(ParkingLot.pincode.ilike(f'{query}%')).all()
            elif parameter == 'lotid' and query.isdigit():
                parkinglots = ParkingLot.query.filter(ParkingLot.id == int(query)).all()
            elif parameter == 'totalspot' and query.isdigit():
                parkinglots = ParkingLot.query.filter(ParkingLot.total_spots == int(query)).all()
        except Exception as e:
            flash("Invalid search input.", "danger")
    return render_template('admin.html',parkinglots=parkinglots,parameters=parameters,param=parameter,query=query)


#------------------------------------- Parking lot -----------------------------------
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

#---------------------------------------------------------------------------------

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

#--------------------------------------------------------------------------------

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


#-------------------------------------------------- Admin (User data) ---------------------------------
# User details
@app.route('/userdata')
@admin_required
def userdata():
    users = User.query.all()
    parameter= request.args.get('parameter')
    query= request.args.get('query')

    parameters= {
        'default':'Search by ',
        'userid' : 'User ID',
        'name' : 'Name',
        'uname' : 'Username',
        'ulocation' : 'Location',
        'upincode' : 'Pincode',
    }
    
    if parameter and query:
        try:
            if parameter == 'userid' and query.isdigit():
                users = User.query.filter(User.id == int(query)).all()
            elif parameter == 'ulocation':
                users = User.query.filter(User.address.ilike(f'%{query}%')).all()
            elif parameter== "name":
                users=User.query.filter(User.name.ilike(f'%{query}%')).all()
            elif parameter == 'uname':
                users = User.query.filter(User.username.ilike(f'{query}%')).all()
            elif parameter == 'upincode':
                users = User.query.filter(User.pincode.like(f'{query}%')).all()
        except Exception as e:
            flash('Invalid search query.')
    return render_template('user/userdata.html', users=users,parameters=parameters,param=parameter,query=query)


#------------------------------------------- View reserved spot --------------------------------------

@app.route('/reserved/<int:id>/view')
@admin_required
def view_reserve(id):
    reservation=Reservation.query.filter_by(spot_id=id).first()
    if not reservation:
        flash('Reservation not found')
        return redirect(url_for('admin'))
    leaving_timestamp = datetime.now()
    ptimestamp= reservation.parking_timestamp
    duration = leaving_timestamp - ptimestamp
    hrs = duration.total_seconds() / 3600
    est_cost = round(hrs * reservation.parkinglot.price_per_hour, 2)
    return render_template('spot/occupiedspot.html',reservation=reservation,est_cost=est_cost)



#-------------------------------------- Parking spot---------------------------------------------------

@app.route('/admin/deletespot/<int:id>')
@admin_required
def delete_spot(id):
    spot=ParkingSpot.query.get(id)
    if not spot.is_occupied: 
        status='Available'   
    else:
        status='Occupied'
    return render_template('spot/deletespot.html',spot=spot,status=status)

@app.route('/admin/deletespot/<int:id>', methods=['POST'])
@admin_required
def delete_spot_post(id):
    spot=ParkingSpot.query.get(id)
    parkinglot=ParkingLot.query.filter_by(id=spot.lot_id).first()

    if spot.is_occupied:
        flash("You can't delete the spot as it is reserved")
        return redirect(url_for('admin'))
    db.session.delete(spot)
    parkinglot.total_spots=parkinglot.total_spots-1
    
    db.session.commit()

    flash('Spot deleted successfully')
    return redirect(url_for('admin'))


# ------------------------------------------ Admin summary  ----------------------------------------

@app.route('/admin/summary')
@admin_required
def admin_summary():
    #revenue from each parking lot
    lots = ParkingLot.query.all()
    revenue_data = []
    lot_labels = []

    for lot in lots:
        reservations = Reservation.query.filter_by(lot_id=lot.id).all()
        total_revenue = 0
        for r in reservations:
            if r.leaving_timestamp:
                hours = (r.leaving_timestamp - r.parking_timestamp).total_seconds() / 3600
                total_revenue += hours * lot.price_per_hour
        revenue_data.append(total_revenue)
        lot_labels.append(lot.name)

    #summary on available and occupied parking lots
    bar_labels = []
    occupied_counts = []
    available_counts = []

    for lot in lots:
        spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        occupied = sum(1 for s in spots if s.is_occupied)
        available = len(spots) - occupied
        bar_labels.append(lot.name)
        occupied_counts.append(occupied)
        available_counts.append(available)

    #  Creating charts directory if not exists
    os.makedirs('static/charts', exist_ok=True)

    # Donut chart wedges, texts, autotexts 
    plt.pie(
        revenue_data,
        labels=lot_labels,
        autopct='%1.1f%%',
        startangle=140,
        wedgeprops=dict(width=0.4)
    )
    plt.title("Revenue Distribution by Lot")
    plt.savefig('static/charts/revenue_donut.png')
    plt.close()

    # Bar chart 
    x = range(len(bar_labels))
    plt.figure(figsize=(8, 6))
    plt.bar(x, available_counts, width=0.4, label='Available', align='center')
    plt.bar(x, occupied_counts, width=0.4, bottom=available_counts, label='Occupied', align='center')
    plt.xticks(x, bar_labels, rotation=45)
    plt.ylabel('Number of Spots')
    plt.title('Parking Spot Summary by Lot')
    plt.legend()
    plt.tight_layout()
    plt.savefig('static/charts/occupancy_bar.png')
    plt.close()

    return render_template('adminsummary.html')

    



#------------------------------------------------ User ------------------------------------------

@app.route('/user')
@auth_required
def user():
    parkinglots = ParkingLot.query.all()
    parameter= request.args.get('parameter')
    query= request.args.get('query')

    parameters={
        'default':'Search by',
        'lotname':'Lot name',
        'location' : 'Location',
        'pincode':'Pincode'
    }
    
    if parameter=='lotname':
        parkinglots=ParkingLot.query.filter(ParkingLot.name.ilike(f'%{query}%')).all()
        return render_template('user/user.html',parkinglots=parkinglots,parameters=parameters,param=parameter,query=query)
    elif parameter=='location':
        parkinglots=ParkingLot.query.filter(ParkingLot.address.ilike(f'%{query}%')).all()
        return render_template('user/user.html',parkinglots=parkinglots,parameters=parameters,param=parameter,query=query)
    elif parameter=='pincode':
        parkinglots=ParkingLot.query.filter(ParkingLot.pincode.ilike(f'{query}%')).all()
        return render_template('user/user.html',parkinglots=parkinglots,parameters=parameters,param=parameter,query=query)
    return render_template('user/user.html',parkinglots=parkinglots,parameters=parameters,param=parameter,query=query)
    

#---------------------------------------- Book lot --------------------------------------------

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
    existing_reservation = Reservation.query.filter_by(user_id=session['user_id'], lot_id=id,vehicle_id=vehicle.id,leaving_timestamp=None).first()
    if existing_reservation:
        flash(f'You have already booked a spot for vehicle : {vehicle.vehicle_number} in this parking lot.')
        return redirect(url_for('parking_history'))

    #check if given vehicle have already a reserved spot in any lot
    reservation=Reservation.query.filter_by(vehicle_id=vehicle_id,leaving_timestamp=None).first()
    if reservation:
        flash(f'You already booked a spot for vehicle : {vehicle.vehicle_number}')
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


#-------------------------------------- Release lot ---------------------------------------------

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


#------------------------------------------- parking history -------------------------------------

@app.route('/parking/history')
@auth_required
def parking_history():
    reservations=Reservation.query.filter_by(user_id=session['user_id']).all()
    return render_template('user/parkinghistory.html',reservations=reservations)



#----------------------------------------- Vehicle ------------------------------------------------

@app.route('/vehicle')
@auth_required
def vehicle():
    vehicles=Vehicle.query.filter_by(user_id=session['user_id']).all()
    return render_template('user/vehicle.html',vehicles=vehicles)

# -----------------------------------------------------------------------------
@app.route('/vehicle/add' )
@auth_required
def add_vehicle():
    return render_template('user/addvehicle.html') 

@app.route('/vehicle/add', methods=['POST'])
@auth_required  
def add_vehicle_post():
    user_id = session['user_id']
    vehicle_number = request.form.get('vehicleno')
    vehicle_type = request.form.get('vehicle_type')
    #check if vehicle_number is unique or not
    vehicle=Vehicle.query.filter_by(vehicle_number=vehicle_number).first()
    if vehicle:
        flash("Vehicle_number already exist.Kindly check again")
        return redirect(url_for('vehicle'))
    
    db.session.add(Vehicle(user_id=user_id, vehicle_number=vehicle_number,vehicle_type=vehicle_type))
    db.session.commit()
    flash('Vehicle added successfully')
    return redirect(url_for('vehicle'))

#--------------------------------------------------------------------------
@app.route('/vehicle/<int:id>/edit' )
@auth_required
def edit_vehicle(id):
    vehicle=Vehicle.query.filter_by(id=id).first()
    return render_template('user/editvehicle.html',vehicle=vehicle) 

@app.route('/vehicle/<int:id>/edit' , methods=['POST'] )
@auth_required
def edit_vehicle_post(id):
    vehicle=Vehicle.query.filter_by(id=id).first()
    vehicle.vehicle_type=request.form.get('vehicle_type')
    db.session.commit()
    flash('Vehicle updated successfully')
    return redirect(url_for('vehicle'))
    
# -----------------------------------------------------------------------------
@app.route('/vehicle/<int:id>/delete' )
@auth_required
def delete_vehicle(id):
    vehicle=Vehicle.query.filter_by(id=id).first()
    return render_template('user/deletevehicle.html',vehicle=vehicle) 

@app.route('/vehicle/<int:id>/delete' ,methods=['POST'])
@auth_required
def delete_vehicle_post(id):
    vehicle=Vehicle.query.filter_by(id=id).first()
    reservation=Reservation.query.filter_by(vehicle_id=id,leaving_timestamp=None).first()
    if reservation:
        flash(f"You can't delete vehicle : {vehicle.vehicle_number} as it reserved a spot")
        return redirect(url_for('parking_history'))
    db.session.delete(vehicle)
    db.session.commit()
    flash('Deleted successfully')
    return redirect(url_for('vehicle'))
    

#--------------------------------------------------- User summary ------------------------------------

@app.route('/user/<int:id>/summary')
@auth_required
def user_summary(id):
    lots = ParkingLot.query.all()
    # count = defaultdict(int)
    count={}
    for lot in lots:
        count[lot.name] = 0
    reservations = Reservation.query.filter_by(user_id=id).all()
    for r in reservations:
        lot = ParkingLot.query.get(r.lot_id)
        if lot:
            count[lot.name] += 1
    lot_names = list(count.keys())
    counts = list(count.values())

    plt.figure(figsize=(8, 5))
    plt.bar(lot_names, counts, color='green')
    plt.xlabel('Parking Lots')
    plt.ylabel('No. of Used Spots')
    plt.title('Summary of Used Parking Spots')
    plt.xticks(rotation=45)
    plt.tight_layout()
    image_path = os.path.join('static', 'summary_plot.png')
    plt.savefig(image_path)
    plt.close()

    return render_template('user/usersummary.html', image_file='summary_plot.png')

   

