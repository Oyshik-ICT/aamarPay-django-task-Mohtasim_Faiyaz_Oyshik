# Payment File System Backend API

A Django REST API system that integrates aamarPay payment gateway with file upload and processing capabilities. Users can register, make payments, upload files (TXT/DOCX), and get word counts processed asynchronously using Celery.

## Features

- User registration and JWT authentication
- aamarPay sandbox payment integration
- File upload with word count processing
- Asynchronous task processing using Celery
- Activity logging and admin dashboard
- Permission-based access control

## Tech Stack

- **Backend**: Django 5.2.5, Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **Task Queue**: Celery with Redis
- **Database**: SQLite (development)
- **Payment Gateway**: aamarPay Sandbox
- **File Processing**: python-docx for DOCX files

## Setup Instructions (Local)

### Prerequisites

- Python 3.8+
- Redis server
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Oyshik-ICT/aamarPay-django-task-Mohtasim_Faiyaz_Oyshik.git

cd aamarPay-django-task-Mohtasim_Faiyaz_Oyshik
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Setup

Create a `.env` file in the project root with the following content:

```env
STORE_ID=aamarpaytest
SIGNATURE_KEY=dbb74894e82415a2f7ff0ec3a97e4183
URL=https://sandbox.aamarpay.com/jsonpost.php
```

### 5. Database Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Celery and Redis Setup

#### Install Redis

**On Windows:**
- Download and install Redis from the official website

**On macOS:**
```bash
brew install redis
brew services start redis
```

**On Ubuntu/Linux:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

#### Start Celery Worker

Open a new terminal, activate your virtual environment, and run:

```bash
celery -A PaymentFileSystem worker -l info
```

### 8. Run the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required | Access Level |
|--------|----------|-------------|---------------|--------------|
| POST | `/api/register/` | User registration | No | Public |
| POST | `/api/login/` | Login (get JWT tokens) | No | Public |
| POST | `/api/login/refresh/` | Refresh JWT token | No | Public |

### User Management

| Method | Endpoint | Description | Auth Required | Access Level |
|--------|----------|-------------|---------------|--------------|
| GET | `/api/user/` | List users | Yes | **Regular User:** See only own profile<br>**Staff/Admin:** See all users |
| GET | `/api/user/{id}/` | Get specific user details | Yes | **Regular User:** Only own profile (if ID matches)<br>**Staff/Admin:** Any user profile |
| PUT | `/api/user/{id}/` | Update user profile | Yes | **Regular User:** Only own profile (if ID matches)<br>**Staff/Admin:** Any user profile |
| PATCH | `/api/user/{id}/` | Partial update user profile | Yes | **Regular User:** Only own profile (if ID matches)<br>**Staff/Admin:** Any user profile |
| POST | `/api/user/` | Create new user | Yes | **Anyone:** Can create users (same as register) |
| DELETE | `/api/user/{id}/` | Delete user | Yes | **Staff/Admin only:** Can delete any user<br>**Regular User:** Can delete only own profile |

### Payment Endpoints

| Method | Endpoint | Description | Auth Required | Access Level |
|--------|----------|-------------|---------------|--------------|
| POST | `/api/initiate-payment/` | Start payment process | Yes | **Authenticated Users:** Can initiate payment for themselves |
| POST | `/api/payment/success/` | Payment success callback | No | **aamarPay Gateway:** Handles successful payment callbacks |
| POST | `/api/payment/failure/` | Payment failure callback | No | **aamarPay Gateway:** Handles failed payment callbacks |
| GET | `/api/payment/cancel/` | Payment cancel callback | No | **aamarPay Gateway:** Handles payment cancellation |
| GET | `/api/transactions/` | List payment transactions | Yes | **Admin/Staff only:** View all payment transactions |

### File Processing Endpoints

| Method | Endpoint | Description | Auth Required | Access Level |
|--------|----------|-------------|---------------|--------------|
| POST | `/api/upload/` | Upload file for processing | Yes | **Authenticated Users with Valid Payment:** Must have unused paid transactions |
| GET | `/api/file/` | List uploaded files | Yes | **Regular User:** See only own uploaded files<br>**Staff/Admin:** See all uploaded files |
| GET | `/api/activity/` | View activity logs | Yes | **Regular User:** See only own activity logs<br>**Staff/Admin:** See all users' activity logs |

### Dashboard

| Method | Endpoint | Description | Auth Required | Access Level |
|--------|----------|-------------|---------------|--------------|
| GET | `/api/dashboard/` | Admin dashboard (HTML) | Yes | **Staff/Admin only:** View comprehensive dashboard with all files, payments, and activities |

## API Usage Examples (Postman)

### Public Postman Collection

Access the complete API collection here: https://www.postman.com/joint-operations-candidate-78622090/workspace/payment-file-system-backend-api/collection/37564257-2060142b-cc98-4021-9bf9-adb1b1a26f0f?action=share&creator=37564257

### 1. User Registration

**POST** `http://127.0.0.1:8000/api/register/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "username": "testuser",
    "email": "test@example.com",
    "mobile_number": "01712345678",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "mobile_number": "01712345678"
}
```

### 2. User Login

**POST** `http://127.0.0.1:8000/api/login/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "username": "testuser",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 3. Initiate Payment

**POST** `http://127.0.0.1:8000/api/initiate-payment/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Body:** Empty (payment amount is fixed at 100 BDT)

**Response:**
```json
{
    "result": "true",
    "payment_url": "https://sandbox.aamarpay.com/paynow.php?track=AAM1690275828103929"
}
```

### 4. Upload File

**POST** `http://127.0.0.1:8000/api/upload/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Body (form-data):**
```
file: [Select a .txt or .docx file]
```

**Response:**
```json
{
    "file_id": "123e4567-e89b-12d3-a456-426614174000",
    "user": 1,
    "file": "http://127.0.0.1:8000/media/uploads/sample.txt",
    "filename": "sample.txt",
    "upload_time": "2023-12-07T10:30:00Z",
    "status": "Processing",
    "word_count": null
}
```

### 5. List Files

**GET** `http://127.0.0.1:8000/api/file/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response (Regular User - sees only own files):**
```json
[
    {
        "file_id": "123e4567-e89b-12d3-a456-426614174000",
        "user": 1,
        "file": "http://127.0.0.1:8000/media/uploads/sample.txt",
        "filename": "sample.txt",
        "upload_time": "2023-12-07T10:30:00Z",
        "status": "Completed",
        "word_count": 150
    }
]
```

**Response (Admin/Staff - sees all users' files):**
```json
[
    {
        "file_id": "123e4567-e89b-12d3-a456-426614174000",
        "user": 1,
        "file": "http://127.0.0.1:8000/media/uploads/sample.txt",
        "filename": "sample.txt",
        "upload_time": "2023-12-07T10:30:00Z",
        "status": "Completed",
        "word_count": 150
    },
    {
        "file_id": "456e7890-e89b-12d3-a456-426614174001",
        "user": 2,
        "file": "http://127.0.0.1:8000/media/uploads/document.docx",
        "filename": "document.docx",
        "upload_time": "2023-12-07T11:00:00Z",
        "status": "Processing",
        "word_count": null
    }
]
```

### 6. Get User Profile

**GET** `http://127.0.0.1:8000/api/user/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response (Regular User - sees only own profile):**
```json
[
    {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "mobile_number": "01712345678"
    }
]
```

**Response (Admin/Staff - sees all users):**
```json
[
    {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "mobile_number": "01712345678"
    },
    {
        "id": 2,
        "username": "anotheruser",
        "email": "another@example.com",
        "mobile_number": "01987654321"
    }
]
```

### 7. View Activity Logs

**GET** `http://127.0.0.1:8000/api/activity/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response (Regular User - sees only own activities):**
```json
[
    {
        "activity_id": "456e7890-e89b-12d3-a456-426614174000",
        "user": 1,
        "action": "file_uploaded",
        "metadata": {
            "filename": "sample.txt"
        },
        "timestamp": "2023-12-07T10:30:00Z"
    },
    {
        "activity_id": "789e1234-e89b-12d3-a456-426614174001",
        "user": 1,
        "action": "payment",
        "metadata": {
            "tranasction_id": "PAY_abc123def456",
            "payment_status": "Successful",
            "amount": 100.00
        },
        "timestamp": "2023-12-07T10:25:00Z"
    }
]
```

**Response (Admin/Staff - sees all users' activities):**
```json
[
    {
        "activity_id": "456e7890-e89b-12d3-a456-426614174000",
        "user": 1,
        "action": "file_uploaded",
        "metadata": {
            "filename": "sample.txt"
        },
        "timestamp": "2023-12-07T10:30:00Z"
    },
    {
        "activity_id": "123e4567-e89b-12d3-a456-426614174002",
        "user": 2,
        "action": "word_count",
        "metadata": {
            "filename": "document.docx",
            "word_count": 250,
            "status": "COMPLETED"
        },
        "timestamp": "2023-12-07T11:15:00Z"
    }
]
```

### 8. List Payment Transactions (Admin Only)

**GET** `http://127.0.0.1:8000/api/transactions/`

**Headers:**
```
Authorization: Bearer ADMIN_ACCESS_TOKEN
```

**Response (Admin/Staff only):**
```json
[
    {
        "payment_id": "789e1234-e89b-12d3-a456-426614174000",
        "user": 1,
        "amount": "100.00",
        "status": "Paid",
        "transaction_id": "PAY_abc123def456",
        "gateway_response": {
            "pg_txnid": "AAM1694948761103545",
            "pay_status": "Successful",
            "amount": "100.00",
            "cus_name": "testuser"
        },
        "timestamp": "2023-12-07T10:25:00Z"
    }
]
```

### 9. Update User Profile

**PUT** `http://127.0.0.1:8000/api/user/1/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "username": "updateduser",
    "email": "updated@example.com",
    "mobile_number": "01798765432"
}
```

**Response (Success):**
```json
{
    "id": 1,
    "username": "updateduser",
    "email": "updated@example.com",
    "mobile_number": "01798765432"
}
```

**Response (Error - trying to access another user's profile as regular user):**
```json
{
    "detail": "Not found."
}
```

## Permission System Details

### User Roles and Access Control

The system implements a role-based permission system:

1. **Regular Users (Authenticated)**
   - Can view and update only their own data
   - Can make payments and upload files (if payment is made)
   - Cannot access other users' information
   - Cannot access admin-only endpoints

2. **Staff/Admin Users**
   - Have full access to all endpoints
   - Can view all users' data, files, payments, and activities
   - Can access admin dashboard
   - Can manage transactions and user accounts

3. **Unauthenticated Users (Public)**
   - Can only access registration and login endpoints
   - Cannot access any protected resources

### File Upload Restrictions

File upload is restricted based on payment status:
- Users can only upload files if they have more **successful payments** than **uploaded files**
- For example: If a user has made 2 successful payments and uploaded 1 file, they can upload 1 more file
- This ensures users pay before uploading each file

## Payment Flow


### Step 1: Complete User Registration and Login
1. Register a new user using the registration endpoint
2. Login to get JWT tokens
3. Save the access token for authenticated requests

### Step 2: Initiate Payment
1. Make a POST request to `/api/initiate-payment/` with your access token
2. You'll receive a response with `payment_url`
3. Copy and open the `payment_url` in your browser

### Step 3: Complete Payment in Sandbox
1. The aamarPay sandbox page will open
2. Select how you pay
3. Click "Success"

### Step 4: Verify Payment Status
1. After payment completion, you'll be redirected to your success/failure URL
2.If the payment is successful then you will see the transaction id and file upload api endpoint url.
3. Check the transaction status using `/api/transactions/` (Admin only)
4. Check activity logs using `/api/activity/` to see payment logging

### Step 5: Test File Upload
1. After successful payment, try uploading a file using `/api/upload/`
2. Only users with successful payments can upload files
3. Monitor the file processing status - it should change from "Processing" to "Completed"
4. Check the word count in the file list endpoint

## Payment Gateway Callback URLs

The system automatically handles these callback URLs from aamarPay:

- **Success URL:** `http://your-domain/api/payment/success/`
- **Failure URL:** `http://your-domain/api/payment/failure/`
- **Cancel URL:** `http://your-domain/api/payment/cancel/`

## File Processing

### Supported File Types
- `.txt` - Plain text files
- `.docx` - Microsoft Word documents

### Processing Flow
1. User uploads a file (requires prior payment)
2. File is saved and a Celery task is queued
3. Celery worker processes the file and counts words
4. File status updates from "Processing" to "Completed" or "Failed"
5. Word count is stored and available via API

## Admin Dashboard

Access the admin dashboard at: `http://127.0.0.1:8000/api/dashboard/`

**Requirements:** Staff user account

**Features:**
- View all uploaded files
- Monitor payment transactions
- Check activity logs
- Read-only interface for data protection

## Troubleshooting

### Common Issues

1. **Celery worker not starting:**
   - Ensure Redis is running
   - Check Redis connection: `redis-cli ping`
   - Verify Celery configuration in settings.py

2. **File upload fails:**
   - Verify user has completed payment
   - Check file type is supported (.txt or .docx)
   - Ensure media directory has write permissions

3. **JWT token expires:**
   - Use the refresh token to get a new access token or hit the login url again to get new token
   - Implement token refresh in your client application
