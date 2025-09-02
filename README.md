# 🚗 Vehicle Parking App

This is my **first real-world project**, built as part of my learning journey while pursuing a dual degree from **IIT Madras (BS in Data Science)** . 

I was always passionate about creating useful web applications, and this project gave me the opportunity to apply my knowledge and gain hands-on experience in **Flask, Databases, and Web Development**.  

---

## 🛠️ Technologies Used
1. **HTML/CSS/Bootstrap** – Frontend design and responsiveness  
2. **Flask** – Backend web server  
3. **Flask-Session** – Manage user sessions  
4. **Flask-SQLAlchemy** – ORM to interact with SQLite database  
5. **Jinja2** – Dynamic HTML template rendering  
6. **SQLite** – Database for users, lots, spots, vehicles, and reservations  
7. **Matplotlib** – Visual reports and summaries  
8. **Werkzeug Security** – Secure password hashing  

---

## 🗂️ Project Structure
├── app.py # Main application entry point
├── models.py # Database models
├── routes.py # Handles login, dashboard, reservations, etc.
├── templates/ # HTML templates (rendered via Flask & Jinja2)
├── static/ # Images, CSS, JS
└── parking.db # SQLite database


---

## ✨ Features Implemented
- ✅ User registration & login with session handling  
- ✅ Admin dashboard (add/edit/delete parking lots & spots, view stats)  
- ✅ Searchbar:  
  - Users → Search parking lots  
  - Admins → Search users/parking lots by ID, name, username, location, etc.  
- ✅ Spot reservation with real-time status (occupied/available)  
- ✅ Matplotlib graphs for **Admin Summary** & **User Summary**  

---

## ➕ Additional Features
1. 🚗 Vehicle registration & assignment to users (with edit/delete options)  
2. ✔️ Frontend validation using HTML5 (`required`, `type=email`, etc.)  
3. 👤 Update profile & logout functionality  
4. 🎨 Clean, responsive UI with Bootstrap  
5. 🔐 Secure password storage using **Werkzeug Security**  

---

## 📊 Future Improvements
- QR code–based parking tickets  
- Real-time slot availability updates  
- Deployment on **Heroku/AWS/GCP**  

---

## 👩‍💻 Author
Developed by **Sakshi Rawat**  
- Pursuing **BS in Data Science, IIT Madras**  

---

## Project report
https://drive.google.com/file/d/1ParX9z4CrCwkNqXfzS_hz4-dm1cZDtP_/view?usp=sharing
