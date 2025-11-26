# 🎬 Movie Ticket Booking System — Backend  
Backend solution Built with **Django, Django REST Framework, JWT Authentication, and Swagger UI**.

---

## 📌 Overview  
This project implements a complete backend for a movie ticket booking system, including:

- User signup & login (JWT authentication)  
- List movies & shows  
- Book a seat (prevents double-booking & overbooking)  
- Cancel a booking (frees the seat)  
- View logged-in user's bookings  
- Swagger docs at `/swagger/`  
- Seed script + Automated test script  

---

## 🚀 Features

### 🔐 Authentication
- **Signup:** `/api/signup/`
- **Login (JWT):** `/api/login/`

### 🎥 Movies & Shows
- List all movies  
- List shows for a movie  

### 🎫 Seat Booking
- Book a seat in a show  
- Prevent double booking  
- Prevent booking out-of-range seats  
- Cancel booking and free seat  
- View user's booking history  

### 📄 Documentation  
- **Swagger UI:** `/swagger/`  

### 🧪 Testing
- `test_api.py` validates the entire workflow:
  - signup → login → movies → shows → booking → double-book prevention → cancellation → rebooking  
- Expected final result:
```
FINAL: Overall result: PASS
```

---

## 🧰 Tech Stack  
- Python  
- Django  
- Django REST Framework  
- SimpleJWT  
- drf-yasg (Swagger)  
- SQLite  

---

## 📁 Project Structure  

```
movie_booking_assignment/
│
├── manage.py
├── requirements.txt
├── seed_script.py
├── test_api.py
│
├── backend/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
└── api/
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    └── migrations/
```

---

## ⚙️ Installation & Setup (Windows PowerShell)

### 1️⃣ Create Virtual Environment
```powershell
python -m venv venv
```

### 2️⃣ Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### 3️⃣ Install Requirements
```powershell
pip install -r requirements.txt
```

### 4️⃣ Run Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Seed Database
```powershell
Get-Content seed_script.py | python manage.py shell
```

---

## ▶️ Running the Server
```powershell
python manage.py runserver
```

Swagger UI →  
```
http://127.0.0.1:8000/swagger/
```

---

## 🔌 API Endpoints

### 🔐 Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/signup/` | Register a new user |
| POST | `/api/login/` | Login and receive JWT tokens |

### 🎬 Movies & Shows
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/movies/` | List all movies |
| GET | `/api/movies/<movie_id>/shows/` | List all shows for a movie |

### 🎫 Bookings
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/shows/<show_id>/book/` | Book a seat |
| POST | `/api/bookings/<booking_id>/cancel/` | Cancel booking |
| GET | `/api/my-bookings/` | List user’s bookings |

---

## 🌱 Seed Script
Adds sample movies & shows.

Run:
```powershell
Get-Content seed_script.py | python manage.py shell
```

---

## 🧪 Running Automated Tests
```powershell
python test_api.py
```
Expected:
```
FINAL: Overall result: PASS
```

---

