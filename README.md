VEHICLE PARKING APP : It is a multi-user app (one requires an administrator and other users) that manages different parking lots, parking spots and parked vehicles.

Frameworks that are used:
1.HTML/CSS/Bootstrap: For the frontend design and responsiveness.
2.Flask: To build the backend web server.
3.Flask-Session : To manage user sessions.
4.Flask-SQLAlchemy: To interact with the SQLite database using ORM (Object Relational
Mapping).
5.Jinja2: To render HTML templates dynamically.
6.SQLite: As the database for storing users, lots, spots , vehicles, and reservations.
7.Matplotlib: To create visual reports and summary. .
8.Werkzeug Security: For secure password hashing.

Project Structure :-
app.py : This is the main file that connects everything.
templates/ : It has all the HTML files rendered using Flask.
static/ : holds all images.
models.py : It contains all the database models.
routes.py : It handles login, admin/user dashboard, reservation logic etc. 

Admin functionalities:
1.Admin can create a new parking lot
2.Each parking lot can have any number of parking spots for 4-wheeler parking
3.Each parking lot can have a different price
4.Admin can view the status of all available parking spots on his/her dashboard
5.Admin can edit/delete any number of parking lots, i.e., admin can increase or decrease the number of parking spots inside the 

User functionalities:
1.Register/Login
2.Choose an available parking lot
3.Book the spot (automatically allotted by the app after booking)
4.Release or vacate the spot