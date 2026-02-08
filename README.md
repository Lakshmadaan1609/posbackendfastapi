# Zoko Momo Backend API Documentation

FastAPI backend application for Zoko Momo management system.

  - [Manufacturing](#manufacturing)
  - [Distribution](#distribution)
  - [Cart Sales](#cart-sales)

---

## Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Update the database credentials in `.env` file with your actual database details

4. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

---

## Base URL

```
http://localhost:8000
```

---

## API Endpoints

### Health & System

#### 1. Root Endpoint
- **Method:** `GET`
- **Endpoint:** `/`
- **Description:** Welcome message
- **Response:**
  ```json
  {
    "message": "Welcome to Zoko Momo Backend API"
  }
  ```

#### 2. Health Check
- **Method:** `GET`
- **Endpoint:** `/health`
- **Description:** Check API and database connection status
- **Response:**
  ```json
  {
    "status": "healthy",
    "database": {
      "status": "connected",
      "database_version": "PostgreSQL 14.x"
    }
  }
  ```

#### 3. Database Test
- **Method:** `GET`
- **Endpoint:** `/db/test`
- **Description:** Test database connection and return database version
- **Response:**
  ```json
  {
    "status": "success",
    "database_version": "PostgreSQL 14.x on x86_64..."
  }
  ```

---

### Manufacturing

#### 1. Get All Manufacturing Records
- **Method:** `GET`
- **Endpoint:** `/manufacturing`
- **Description:** Retrieve all manufacturing records with pagination
- **Query Parameters:**
  - `limit` (optional, default: 100, max: 1000): Number of records to return
  - `offset` (optional, default: 0): Number of records to skip
- **Response:**
  ```json
  [
    {
      "date": "2024-01-15T00:00:00",
      "veg": 10,
      "paneer": 5,
      "chicken": 8,
      "cheesecorn": 3,
      "springroll": 2,
      "attaveg": 4,
      "attachicken": 6,
      "chilli_sauce": "500ml",
      "special_sause": "300ml",
      "total_bill": 5000
    }
  ]
  ```

#### 2. Get Manufacturing Record by Date
- **Method:** `GET`
- **Endpoint:** `/manufacturing/{date}`
- **Description:** Get manufacturing record for a specific date
- **Path Parameters:**
  - `date` (required): Date in `YYYY-MM-DD` format
- **Response:**
  ```json
  {
    "date": "2024-01-15T00:00:00",
    "veg": 10,
    "paneer": 5,
    "chicken": 8,
    "cheesecorn": 3,
    "springroll": 2,
    "attaveg": 4,
    "attachicken": 6,
    "chilli_sauce": "500ml",
    "special_sause": "300ml",
    "total_bill": 5000
  }
  ```
- **Error Response (404):**
  ```json
  {
    "detail": "No manufacturing record found for date: 2024-01-15"
  }
  ```

#### 3. Create Manufacturing Record
- **Method:** `POST`
- **Endpoint:** `/manufacturing`
- **Description:** Create a new manufacturing record
- **Request Body:**
  ```json
  {
    "veg": 10,
    "paneer": 5,
    "chicken": 8,
    "cheesecorn": 3,
    "springroll": 2,
    "attaveg": 4,
    "attachicken": 6,
    "chilli_sauce": "500ml",
    "special_sause": "300ml",
    "total_bill": 5000,
    "date": "2024-01-15T00:00:00"
  }
  ```
  **Note:** All fields are optional except at least one field must be provided. `date` defaults to current timestamp if not provided.
- **Response:**
  ```json
  {
    "status": "success",
    "message": "Manufacturing record created successfully",
    "data": {
      "date": "2024-01-15T00:00:00",
      "veg": 10,
      "paneer": 5,
      "chicken": 8,
      "cheesecorn": 3,
      "springroll": 2,
      "attaveg": 4,
      "attachicken": 6,
      "chilli_sauce": "500ml",
      "special_sause": "300ml",
      "total_bill": 5000
    }
  }
  ```

#### 4. Update or Create Manufacturing Record
- **Method:** `PUT`
- **Endpoint:** `/manufacturing`
- **Description:** 
  - If a record exists for the same date: **Adds** numeric values to existing values and **replaces** string values
  - If no record exists: Creates a new record
- **Request Body:**
  ```json
  {
    "veg": 5,
    "paneer": 3,
    "chicken": 2,
    "chilli_sauce": "200ml",
    "date": "2024-01-15T00:00:00"
  }
  ```
  **Note:** `date` defaults to today if not provided.
- **Response (Update):**
  ```json
  {
    "status": "success",
    "message": "Manufacturing record updated successfully (values added to existing record)",
    "data": {
      "date": "2024-01-15T00:00:00",
      "veg": 15,
      "paneer": 8,
      "chicken": 10,
      "chilli_sauce": "200ml"
    },
    "operation": "update"
  }
  ```
- **Response (Create):**
  ```json
  {
    "status": "success",
    "message": "Manufacturing record created successfully (no existing record for this date)",
    "data": {
      "date": "2024-01-15T00:00:00",
      "veg": 5,
      "paneer": 3,
      "chicken": 2
    },
    "operation": "create"
  }
  ```
- **Logic:** 
  - Numeric fields (veg, paneer, chicken, etc., total_bill): **Addition** (existing + new)
  - String fields (chilli_sauce, special_sause): **Replacement**

---

### Distribution

#### 1. Get All Distribution Records
- **Method:** `GET`
- **Endpoint:** `/distribution`
- **Description:** Retrieve all distribution records with optional filtering
- **Query Parameters:**
  - `cart_id` (optional): Filter by cart ID
  - `date` (optional): Filter by date in `YYYY-MM-DD` format
  - `limit` (optional, default: 100, max: 1000): Number of records to return
  - `offset` (optional, default: 0): Number of records to skip
- **Response:**
  ```json
  [
    {
      "cart_id": 1,
      "date": "2024-01-15T00:00:00",
      "veg": 10,
      "paneer": 5,
      "chicken": 8,
      "cheesecorn": 3,
      "springroll": 2,
      "attaveg": 4,
      "attachicken": 6
    }
  ]
  ```

#### 2. Get Distribution Records by Cart ID
- **Method:** `GET`
- **Endpoint:** `/distribution/{cart_id}`
- **Description:** Get all distribution records for a specific cart
- **Path Parameters:**
  - `cart_id` (required): Cart ID (integer)
- **Query Parameters:**
  - `date` (optional): Filter by date in `YYYY-MM-DD` format
- **Response:**
  ```json
  [
    {
      "cart_id": 1,
      "date": "2024-01-15T00:00:00",
      "veg": 10,
      "paneer": 5,
      "chicken": 8,
      "cheesecorn": 3,
      "springroll": 2,
      "attaveg": 4,
      "attachicken": 6
    }
  ]
  ```
- **Error Response (404):**
  ```json
  {
    "detail": "No distribution records found for cart_id: 1"
  }
  ```

#### 3. Create Distribution Record
- **Method:** `POST`
- **Endpoint:** `/distribution`
- **Description:** Create a new distribution record. Returns error if record exists for same cart_id and date.
- **Request Body:**
  ```json
  {
    "cart_id": 1,
    "veg": 10,
    "paneer": 5,
    "chicken": 8,
    "cheesecorn": 3,
    "springroll": 2,
    "attaveg": 4,
    "attachicken": 6,
    "date": "2024-01-15T00:00:00"
  }
  ```
  **Note:** `cart_id` is required. `date` defaults to current timestamp if not provided.
- **Response:**
  ```json
  {
    "status": "success",
    "message": "Distribution record created successfully",
    "data": {
      "cart_id": 1,
      "date": "2024-01-15T00:00:00",
      "veg": 10,
      "paneer": 5,
      "chicken": 8
    }
  }
  ```
- **Error Response (409):**
  ```json
  {
    "detail": "Distribution record already exists for cart_id 1 on date 2024-01-15. Use PUT endpoint to update."
  }
  ```

#### 4. Update or Create Distribution Record
- **Method:** `PUT`
- **Endpoint:** `/distribution`
- **Description:** 
  - If a record exists for the same cart_id and date: **Adds** numeric values to existing values
  - If no record exists: Creates a new record
- **Request Body:**
  ```json
  {
    "cart_id": 1,
    "veg": 5,
    "paneer": 3,
    "chicken": 2,
    "date": "2024-01-15T00:00:00"
  }
  ```
  **Note:** `cart_id` is required. `date` defaults to today if not provided.
- **Response (Update):**
  ```json
  {
    "status": "success",
    "message": "Distribution record updated successfully (values added to existing record for cart_id 1)",
    "data": {
      "cart_id": 1,
      "date": "2024-01-15T00:00:00",
      "veg": 15,
      "paneer": 8,
      "chicken": 10
    },
    "operation": "update"
  }
  ```
- **Response (Create):**
  ```json
  {
    "status": "success",
    "message": "Distribution record created successfully (no existing record for cart_id 1 on this date)",
    "data": {
      "cart_id": 1,
      "date": "2024-01-15T00:00:00",
      "veg": 5,
      "paneer": 3,
      "chicken": 2
    },
    "operation": "create"
  }
  ```
- **Logic:** All numeric fields are **added** to existing values (existing + new)

---

### Cart Sales

#### 1. Get All Cart Sales Records
- **Method:** `GET`
- **Endpoint:** `/sales`
- **Description:** Retrieve all cart sales records with optional filtering
- **Query Parameters:**
  - `cart_id` (optional): Filter by cart ID
  - `date` (optional): Filter by date in `YYYY-MM-DD` format
  - `limit` (optional, default: 100, max: 1000): Number of records to return
  - `offset` (optional, default: 0): Number of records to skip
- **Response:**
  ```json
  [
    {
      "created_at": "2024-01-15",
      "cart_id": 1,
      "half_vegsteam": 10,
      "full_vegsteam": 5,
      "half_vegfried": 8,
      "full_vegfried": 3,
      "half_vegkurkure": 2,
      "full_vegkurkure": 1,
      "half_paneersteam": 6,
      "full_paneersteam": 4,
      "half_paneerfried": 3,
      "full_paneerfried": 2,
      "half_paneerkurkure": 1,
      "full_paneerkurkure": 1,
      "half_chickensteam": 8,
      "full_chickensteam": 5,
      "half_chickenfried": 4,
      "full_chickenfried": 3,
      "half_chickenkurkure": 2,
      "full_chickenkurkure": 1,
      "half_cheesecornsteam": 3,
      "full_cheesecorsteamn": 2,
      "half_cheesecornfried": 2,
      "full_cheesecornfried": 1,
      "half_cheesecornkurkure": 1,
      "full_cheesecornkurkure": 1,
      "half_springroll": 5,
      "full_springroll": 3,
      "half_springrollkurkure": 2,
      "full_springrollkurkure": 1,
      "half_attavegsteam": 4,
      "full_attavegsteam": 2,
      "half_attachickensteam": 3,
      "full_attachickensteam": 2,
      "cash_total": 5000,
      "upi_total": 3000,
      "Shift_timing": "09:00:00"
    }
  ]
  ```

#### 2. Get Cart Sales Records by Cart ID
- **Method:** `GET`
- **Endpoint:** `/sales/{cart_id}`
- **Description:** Get all cart sales records for a specific cart
- **Path Parameters:**
  - `cart_id` (required): Cart ID (integer)
- **Query Parameters:**
  - `date` (optional): Filter by date in `YYYY-MM-DD` format
- **Response:**
  ```json
  [
    {
      "created_at": "2024-01-15",
      "cart_id": 1,
      "half_vegsteam": 10,
      "full_vegsteam": 5,
      "cash_total": 5000,
      "upi_total": 3000
    }
  ]
  ```
- **Error Response (404):**
  ```json
  {
    "detail": "No cart sales records found for cart_id: 1"
  }
  ```

#### 3. Get Cart Sales Records by Date
- **Method:** `GET`
- **Endpoint:** `/sales/date/{date}`
- **Description:** Get all cart sales records for a specific date
- **Path Parameters:**
  - `date` (required): Date in `YYYY-MM-DD` format
- **Query Parameters:**
  - `cart_id` (optional): Filter by cart ID
- **Response:**
  ```json
  [
    {
      "created_at": "2024-01-15",
      "cart_id": 1,
      "half_vegsteam": 10,
      "full_vegsteam": 5
    },
    {
      "created_at": "2024-01-15",
      "cart_id": 2,
      "half_vegsteam": 8,
      "full_vegsteam": 4
    }
  ]
  ```
- **Error Response (404):**
  ```json
  {
    "detail": "No cart sales records found for date: 2024-01-15"
  }
  ```

#### 4. Create Cart Sales Record
- **Method:** `POST`
- **Endpoint:** `/sales`
- **Description:** Create a new cart sales record. Returns error if record exists for same cart_id and date.
- **Request Body:**
  ```json
  {
    "cart_id": 1,
    "half_vegsteam": 10,
    "full_vegsteam": 5,
    "half_vegfried": 8,
    "full_vegfried": 3,
    "half_vegkurkure": 2,
    "full_vegkurkure": 1,
    "half_paneersteam": 6,
    "full_paneersteam": 4,
    "half_paneerfried": 3,
    "full_paneerfried": 2,
    "half_paneerkurkure": 1,
    "full_paneerkurkure": 1,
    "half_chickensteam": 8,
    "full_chickensteam": 5,
    "half_chickenfried": 4,
    "full_chickenfried": 3,
    "half_chickenkurkure": 2,
    "full_chickenkurkure": 1,
    "half_cheesecornsteam": 3,
    "full_cheesecorsteamn": 2,
    "half_cheesecornfried": 2,
    "full_cheesecornfried": 1,
    "half_cheesecornkurkure": 1,
    "full_cheesecornkurkure": 1,
    "half_springroll": 5,
    "full_springroll": 3,
    "half_springrollkurkure": 2,
    "full_springrollkurkure": 1,
    "half_attavegsteam": 4,
    "full_attavegsteam": 2,
    "half_attachickensteam": 3,
    "full_attachickensteam": 2,
    "cash_total": 5000,
    "upi_total": 3000,
    "Shift_timing": "09:00:00",
    "created_at": "2024-01-15"
  }
  ```
  **Note:** `cart_id` is required. All other fields are optional. `created_at` defaults to current date if not provided. `Shift_timing` format: `HH:MM:SS`
- **Response:**
  ```json
  {
    "status": "success",
    "message": "Cart sales record created successfully",
    "data": {
      "created_at": "2024-01-15",
      "cart_id": 1,
      "half_vegsteam": 10,
      "full_vegsteam": 5,
      "cash_total": 5000,
      "upi_total": 3000
    }
  }
  ```
- **Error Response (409):**
  ```json
  {
    "detail": "Cart sales record already exists for cart_id 1 on date 2024-01-15. Use PUT endpoint to update."
  }
  ```

#### 5. Update or Create Cart Sales Record
- **Method:** `PUT`
- **Endpoint:** `/sales`
- **Description:** 
  - If a record exists for the same cart_id and date: **Adds** numeric values to existing values, **replaces** Shift_timing
  - If no record exists: Creates a new record
- **Request Body:**
  ```json
  {
    "cart_id": 1,
    "half_vegsteam": 5,
    "full_vegsteam": 3,
    "cash_total": 1000,
    "upi_total": 500,
    "Shift_timing": "10:00:00",
    "created_at": "2024-01-15"
  }
  ```
  **Note:** `cart_id` is required. `created_at` defaults to today if not provided.
- **Response (Update):**
  ```json
  {
    "status": "success",
    "message": "Cart sales record updated successfully (values added to existing record for cart_id 1)",
    "data": {
      "created_at": "2024-01-15",
      "cart_id": 1,
      "half_vegsteam": 15,
      "full_vegsteam": 8,
      "cash_total": 6000,
      "upi_total": 3500,
      "Shift_timing": "10:00:00"
    },
    "operation": "update"
  }
  ```
- **Response (Create):**
  ```json
  {
    "status": "success",
    "message": "Cart sales record created successfully (no existing record for cart_id 1 on this date)",
    "data": {
      "created_at": "2024-01-15",
      "cart_id": 1,
      "half_vegsteam": 5,
      "full_vegsteam": 3,
      "cash_total": 1000,
      "upi_total": 500
    },
    "operation": "create"
  }
  ```
- **Logic:** 
  - All numeric fields (product counts, cash_total, upi_total): **Addition** (existing + new)
  - `Shift_timing`: **Replacement** (replaces existing value)

---

## Field Reference

### Manufacturing Fields
- `veg` (int, optional): Vegetable momo quantity
- `paneer` (int, optional): Paneer momo quantity
- `chicken` (int, optional): Chicken momo quantity
- `cheesecorn` (int, optional): Cheese corn momo quantity
- `springroll` (int, optional): Spring roll quantity
- `attaveg` (int, optional): Atta veg momo quantity
- `attachicken` (int, optional): Atta chicken momo quantity
- `chilli_sauce` (string, optional): Chilli sauce quantity/description
- `special_sause` (string, optional): Special sauce quantity/description
- `total_bill` (int, optional): Total bill amount
- `date` (datetime, optional): Date timestamp (defaults to now())

### Distribution Fields
- `cart_id` (int, required): Cart identifier
- `veg` (int, optional): Vegetable momo quantity
- `paneer` (int, optional): Paneer momo quantity
- `chicken` (int, optional): Chicken momo quantity
- `cheesecorn` (int, optional): Cheese corn momo quantity
- `springroll` (int, optional): Spring roll quantity
- `attaveg` (int, optional): Atta veg momo quantity
- `attachicken` (int, optional): Atta chicken momo quantity
- `date` (datetime, optional): Date timestamp (defaults to now())

### Cart Sales Fields
- `cart_id` (int, required): Cart identifier
- `created_at` (date, optional): Date (defaults to today)
- `half_vegsteam`, `full_vegsteam` (int, optional): Half/Full veg steam momo
- `half_vegfried`, `full_vegfried` (int, optional): Half/Full veg fried momo
- `half_vegkurkure`, `full_vegkurkure` (int, optional): Half/Full veg kurkure momo
- `half_paneersteam`, `full_paneersteam` (int, optional): Half/Full paneer steam momo
- `half_paneerfried`, `full_paneerfried` (int, optional): Half/Full paneer fried momo
- `half_paneerkurkure`, `full_paneerkurkure` (int, optional): Half/Full paneer kurkure momo
- `half_chickensteam`, `full_chickensteam` (int, optional): Half/Full chicken steam momo
- `half_chickenfried`, `full_chickenfried` (int, optional): Half/Full chicken fried momo
- `half_chickenkurkure`, `full_chickenkurkure` (int, optional): Half/Full chicken kurkure momo
- `half_cheesecornsteam`, `full_cheesecorsteamn` (int, optional): Half/Full cheesecorn steam momo
- `half_cheesecornfried`, `full_cheesecornfried` (int, optional): Half/Full cheesecorn fried momo
- `half_cheesecornkurkure`, `full_cheesecornkurkure` (int, optional): Half/Full cheesecorn kurkure momo
- `half_springroll`, `full_springroll` (int, optional): Half/Full spring roll
- `half_springrollkurkure`, `full_springrollkurkure` (int, optional): Half/Full spring roll kurkure
- `half_attavegsteam`, `full_attavegsteam` (int, optional): Half/Full atta veg steam momo
- `half_attachickensteam`, `full_attachickensteam` (int, optional): Half/Full atta chicken steam momo
- `cash_total` (int, optional): Total cash sales
- `upi_total` (int, optional): Total UPI sales
- `Shift_timing` (string, optional): Shift timing in `HH:MM:SS` format

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Error message describing what went wrong"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 409 Conflict
```json
{
  "detail": "Resource already exists. Use PUT endpoint to update."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Database error or server error message"
}
```

---

## Important Notes

1. **PUT Endpoint Logic:**
   - **Manufacturing**: Numeric fields are added, string fields are replaced
   - **Distribution**: All numeric fields are added
   - **Cart Sales**: All numeric fields are added, `Shift_timing` is replaced

2. **Date Handling:**
   - If `date` or `created_at` is not provided, it defaults to current date/time
   - Date format for query parameters: `YYYY-MM-DD`
   - Date format in request body: ISO 8601 datetime string or date string

3. **POST vs PUT:**
   - Use **POST** when you want to create a new record and get an error if it already exists
   - Use **PUT** when you want to update existing record (by adding values) or create if it doesn't exist

4. **Pagination:**
   - Default limit: 100 records
   - Maximum limit: 1000 records
   - Use `offset` for pagination (e.g., page 2: `offset=100`, page 3: `offset=200`)

---

## Environment Variables

The following environment variables are required in the `.env` file:

- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DATABASE_URL`: Full database connection URL (optional, can be used instead of individual DB_* variables)
- `ENVIRONMENT`: Application environment (development/production)
- `DEBUG`: Debug mode (True/False)
- `SECRET_KEY`: Secret key for application security

---

## Project Structure

```
zokoMomoBackend/
├── main.py              # FastAPI application entry point
├── sales.py             # Cart sales endpoints
├── database.py          # Database connection utilities
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

---

## Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These provide interactive documentation where you can test all endpoints directly from your browser.
