from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from database import get_db_connection, get_db_cursor, test_connection
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date, time
from sales import router as sales_router

# Load environment variables (.env.local preferred, fallback to .env)
load_dotenv(".env.local")
load_dotenv()

app = FastAPI(
    title="Zoko Momo Backend",
    description="FastAPI backend for Zoko Momo",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sales_router)


def get_db():
    """Dependency to get database connection"""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


@app.get("/")
async def root():
    return {"message": "Welcome to Zoko Momo Backend API"}


@app.get("/health")
async def health_check():
    """Health check endpoint with database connection test"""
    db_status = test_connection()
    return {
        "status": "healthy",
        "database": db_status
    }


@app.get("/db/test")
async def test_db(db=Depends(get_db)):
    """Test database connection and return sample query"""
    try:
        cursor = db.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        cursor.close()
        return {
            "status": "success",
            "database_version": version["version"]
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# Pydantic models for manufacturing_db
class ManufacturingCreate(BaseModel):
    """Model for creating manufacturing records"""
    veg: Optional[int] = None
    paneer: Optional[int] = None
    chicken: Optional[int] = None
    cheesecorn: Optional[int] = None
    springroll: Optional[int] = None
    attaveg: Optional[int] = None
    attachicken: Optional[int] = None
    chilli_sauce: Optional[str] = None
    special_sause: Optional[str] = None  # Note: keeping the typo as it appears in DB
    total_bill: Optional[int] = None
    date: Optional[datetime] = None  # Optional, defaults to now() in DB


class ManufacturingResponse(BaseModel):
    """Model for manufacturing record response"""
    date: datetime
    veg: Optional[int] = None
    paneer: Optional[int] = None
    chicken: Optional[int] = None
    cheesecorn: Optional[int] = None
    springroll: Optional[int] = None
    attaveg: Optional[int] = None
    attachicken: Optional[int] = None
    chilli_sauce: Optional[str] = None
    special_sause: Optional[str] = None
    total_bill: Optional[int] = None


# GET endpoints for manufacturing_db
@app.get("/manufacturing", response_model=list[dict])
async def get_all_manufacturing(
    db=Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get all manufacturing records with pagination"""
    try:
        cursor = db.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT * FROM manufacturing_db 
            ORDER BY date DESC 
            LIMIT %s OFFSET %s
            """,
            (limit, offset)
        )
        results = cursor.fetchall()
        cursor.close()
        return [dict(row) for row in results]
    except psycopg2.Error as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching manufacturing records: {str(e)}"
        )


@app.get("/manufacturing/{date}", response_model=dict)
async def get_manufacturing_by_date(
    date: str,
    db=Depends(get_db)
):
    """Get manufacturing record by date (YYYY-MM-DD format)"""
    try:
        cursor = db.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT * FROM manufacturing_db 
            WHERE DATE(date) = %s
            ORDER BY date DESC
            """,
            (date,)
        )
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No manufacturing record found for date: {date}"
            )
        
        return dict(result)
    except HTTPException:
        raise
    except psycopg2.Error as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching manufacturing record: {str(e)}"
        )


# POST endpoint for manufacturing_db
@app.post("/manufacturing", response_model=dict)
async def create_manufacturing(
    data: ManufacturingCreate,
    db=Depends(get_db)
):
    """Create a new manufacturing record"""
    cursor = None
    try:
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # Build the INSERT query dynamically based on provided fields
        fields = []
        values = []
        placeholders = []
        
        # Add date if provided, otherwise let DB use default (now())
        if data.date:
            fields.append("date")
            values.append(data.date)
            placeholders.append("%s")
        
        # Add other fields if provided
        field_mapping = {
            "veg": data.veg,
            "paneer": data.paneer,
            "chicken": data.chicken,
            "cheesecorn": data.cheesecorn,
            "springroll": data.springroll,
            "attaveg": data.attaveg,
            "attachicken": data.attachicken,
            "chilli_sauce": data.chilli_sauce,
            "special_sause": data.special_sause,
            "total_bill": data.total_bill,
        }
        
        for field_name, field_value in field_mapping.items():
            if field_value is not None:
                fields.append(field_name)
                values.append(field_value)
                placeholders.append("%s")
        
        if not fields:
            raise HTTPException(
                status_code=400,
                detail="At least one field must be provided"
            )
        
        fields_str = ", ".join(fields)
        placeholders_str = ", ".join(placeholders)
        
        query = f"""
            INSERT INTO manufacturing_db ({fields_str})
            VALUES ({placeholders_str})
            RETURNING *
        """
        
        cursor.execute(query, values)
        db.commit()
        
        result = cursor.fetchone()
        cursor.close()
        
        return {
            "status": "success",
            "message": "Manufacturing record created successfully",
            "data": dict(result)
        }
        
    except HTTPException:
        if cursor:
            cursor.close()
        db.rollback()
        raise
    except psycopg2.IntegrityError as e:
        db.rollback()
        if cursor:
            cursor.close()
        error_message = str(e)
        if "duplicate key value violates unique constraint" in error_message:
            raise HTTPException(
                status_code=409,
                detail=f"Distribution record already exists for cart_id {data.cart_id} on date {check_date}. Use PUT endpoint to update."
            )
        raise HTTPException(
            status_code=400,
            detail=f"Database integrity error: {error_message}"
        )
    except psycopg2.Error as e:
        db.rollback()
        if cursor:
            cursor.close()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        if cursor:
            cursor.close()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating manufacturing record: {str(e)}"
        )


# PUT endpoint for manufacturing_db
@app.put("/manufacturing", response_model=dict)
async def update_or_create_manufacturing(
    data: ManufacturingCreate,
    db=Depends(get_db)
):
    """
    Update existing manufacturing record for the same date by adding values,
    or create a new record if no record exists for that date.
    
    For numeric fields: adds the new value to existing value
    For string fields: replaces the existing value
    """
    cursor = None
    
    # Determine the date to check
    if data.date:
        check_date = data.date.date() if isinstance(data.date, datetime) else data.date
    else:
        # If no date provided, use today's date
        check_date = date.today()
    
    try:
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # Check if a record exists for this date
        cursor.execute(
            """
            SELECT * FROM manufacturing_db 
            WHERE DATE(date) = %s
            ORDER BY date DESC
            LIMIT 1
            """,
            (check_date,)
        )
        existing_record = cursor.fetchone()
        
        if existing_record:
            # Record exists - update by adding values
            existing_dict = dict(existing_record)
            
            # Build UPDATE query with addition for numeric fields
            update_fields = []
            update_values = []
            
            # Numeric fields that should be added
            numeric_fields = [
                "veg", "paneer", "chicken", "cheesecorn", "springroll",
                "attaveg", "attachicken", "total_bill"
            ]
            
            # String fields that should be replaced
            string_fields = ["chilli_sauce", "special_sause"]
            
            # Process numeric fields - add to existing value
            for field in numeric_fields:
                new_value = getattr(data, field, None)
                if new_value is not None:
                    existing_value = existing_dict.get(field) or 0
                    updated_value = existing_value + new_value
                    update_fields.append(f"{field} = %s")
                    update_values.append(updated_value)
            
            # Process string fields - replace existing value
            for field in string_fields:
                new_value = getattr(data, field, None)
                if new_value is not None:
                    update_fields.append(f"{field} = %s")
                    update_values.append(new_value)
            
            if not update_fields:
                raise HTTPException(
                    status_code=400,
                    detail="At least one field must be provided for update"
                )
            
            # Add the date condition to the WHERE clause
            update_values.append(check_date)
            
            update_fields_str = ", ".join(update_fields)
            
            update_query = f"""
                UPDATE manufacturing_db 
                SET {update_fields_str}
                WHERE DATE(date) = %s
                RETURNING *
            """
            
            cursor.execute(update_query, update_values)
            db.commit()
            
            result = cursor.fetchone()
            cursor.close()
            
            return {
                "status": "success",
                "message": "Manufacturing record updated successfully (values added to existing record)",
                "data": dict(result),
                "operation": "update"
            }
        else:
            # No record exists - create a new one
            fields = []
            values = []
            placeholders = []
            
            # Add date (use the check_date, convert to datetime if needed)
            if isinstance(check_date, date):
                date_datetime = datetime.combine(check_date, time.min)
            else:
                date_datetime = check_date
            
            fields.append("date")
            values.append(date_datetime)
            placeholders.append("%s")
            
            # Add other fields if provided
            field_mapping = {
                "veg": data.veg,
                "paneer": data.paneer,
                "chicken": data.chicken,
                "cheesecorn": data.cheesecorn,
                "springroll": data.springroll,
                "attaveg": data.attaveg,
                "attachicken": data.attachicken,
                "chilli_sauce": data.chilli_sauce,
                "special_sause": data.special_sause,
                "total_bill": data.total_bill,
            }
            
            for field_name, field_value in field_mapping.items():
                if field_value is not None:
                    fields.append(field_name)
                    values.append(field_value)
                    placeholders.append("%s")
            
            if len(fields) == 1:  # Only date field
                raise HTTPException(
                    status_code=400,
                    detail="At least one field besides date must be provided"
                )
            
            fields_str = ", ".join(fields)
            placeholders_str = ", ".join(placeholders)
            
            insert_query = f"""
                INSERT INTO manufacturing_db ({fields_str})
                VALUES ({placeholders_str})
                RETURNING *
            """
            
            cursor.execute(insert_query, values)
            db.commit()
            
            result = cursor.fetchone()
            cursor.close()
            
            return {
                "status": "success",
                "message": "Manufacturing record created successfully (no existing record for this date)",
                "data": dict(result),
                "operation": "create"
            }
            
    except HTTPException:
        if cursor:
            cursor.close()
        db.rollback()
        raise
    except psycopg2.IntegrityError as e:
        db.rollback()
        if cursor:
            cursor.close()
        raise HTTPException(
            status_code=400,
            detail=f"Database integrity error: {str(e)}"
        )
    except psycopg2.Error as e:
        db.rollback()
        if cursor:
            cursor.close()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        if cursor:
            cursor.close()
        raise HTTPException(
            status_code=500,
            detail=f"Error updating/creating manufacturing record: {str(e)}"
        )


# Pydantic models for distribution_db
class DistributionCreate(BaseModel):
    """Model for creating distribution records"""
    cart_id: int
    veg: Optional[int] = None
    paneer: Optional[int] = None
    chicken: Optional[int] = None
    cheesecorn: Optional[int] = None
    springroll: Optional[int] = None
    attaveg: Optional[int] = None
    attachicken: Optional[int] = None
    date: Optional[datetime] = None  # Optional, defaults to now() in DB


class DistributionResponse(BaseModel):
    """Model for distribution record response"""
    cart_id: int
    date: datetime
    veg: Optional[int] = None
    paneer: Optional[int] = None
    chicken: Optional[int] = None
    cheesecorn: Optional[int] = None
    springroll: Optional[int] = None
    attaveg: Optional[int] = None
    attachicken: Optional[int] = None


# GET endpoints for distribution_db
@app.get("/distribution", response_model=list[dict])
async def get_all_distribution(
    db=Depends(get_db),
    cart_id: Optional[int] = Query(None, description="Filter by cart_id"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get all distribution records with optional filtering by cart_id and/or date"""
    try:
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # Build query with optional filters
        query = "SELECT * FROM distribution_db WHERE 1=1"
        params = []
        
        if cart_id is not None:
            query += " AND cart_id = %s"
            params.append(cart_id)
        
        if date is not None:
            query += " AND DATE(date) = %s"
            params.append(date)
        
        query += " ORDER BY date DESC, cart_id ASC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        
        return [dict(row) for row in results]
    except psycopg2.Error as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching distribution records: {str(e)}"
        )


@app.get("/distribution/{cart_id}", response_model=list[dict])
async def get_distribution_by_cart_id(
    cart_id: int,
    db=Depends(get_db),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)")
):
    """Get distribution records for a specific cart_id, optionally filtered by date"""
    try:
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        query = "SELECT * FROM distribution_db WHERE cart_id = %s"
        params = [cart_id]
        
        if date is not None:
            query += " AND DATE(date) = %s"
            params.append(date)
        
        query += " ORDER BY date DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        
        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No distribution records found for cart_id: {cart_id}"
            )
        
        return [dict(row) for row in results]
    except HTTPException:
        raise
    except psycopg2.Error as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching distribution records: {str(e)}"
        )


# POST endpoint for distribution_db
@app.post("/distribution", response_model=dict)
async def create_distribution(
    data: DistributionCreate,
    db=Depends(get_db)
):
    """Create a new distribution record. If record exists for same date and cart_id, returns error."""
    cursor = None
    try:
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # Determine the date to check (defaults to today's date)
        if data.date:
            check_date = data.date.date() if isinstance(data.date, datetime) else data.date
        else:
            check_date = date.today()
        
        # Check if a record already exists for this cart_id and date
        cursor.execute(
            """
            SELECT * FROM distribution_db 
            WHERE cart_id = %s AND DATE(date) = %s
            LIMIT 1
            """,
            (data.cart_id, check_date)
        )
        existing_record = cursor.fetchone()
        
        if existing_record:
            raise HTTPException(
                status_code=409,
                detail=f"Distribution record already exists for cart_id {data.cart_id} on date {check_date}. Use PUT endpoint to update."
            )
        
        # Build the INSERT query
        fields = ["cart_id"]
        values = [data.cart_id]
        placeholders = ["%s"]

        # Always store explicit date value to match sales endpoint behavior
        if data.date and isinstance(data.date, datetime):
            date_datetime = data.date
        else:
            date_datetime = datetime.combine(check_date, time.min)
        fields.append("date")
        values.append(date_datetime)
        placeholders.append("%s")
        
        # Add other fields if provided
        field_mapping = {
            "veg": data.veg,
            "paneer": data.paneer,
            "chicken": data.chicken,
            "cheesecorn": data.cheesecorn,
            "springroll": data.springroll,
            "attaveg": data.attaveg,
            "attachicken": data.attachicken,
        }
        
        for field_name, field_value in field_mapping.items():
            if field_value is not None:
                fields.append(field_name)
                values.append(field_value)
                placeholders.append("%s")
        
        fields_str = ", ".join(fields)
        placeholders_str = ", ".join(placeholders)
        
        query = f"""
            INSERT INTO distribution_db ({fields_str})
            VALUES ({placeholders_str})
            RETURNING *
        """
        
        cursor.execute(query, values)
        db.commit()
        
        result = cursor.fetchone()
        cursor.close()
        
        return {
            "status": "success",
            "message": "Distribution record created successfully",
            "data": dict(result)
        }
        
    except HTTPException:
        if cursor:
            cursor.close()
        db.rollback()
        raise
    except psycopg2.IntegrityError as e:
        db.rollback()
        if cursor:
            cursor.close()
        error_message = str(e)
        if "duplicate key value violates unique constraint" in error_message:
            raise HTTPException(
                status_code=409,
                detail=f"Distribution record already exists for cart_id {data.cart_id} on date {check_date}. Use PUT endpoint to update."
            )
        raise HTTPException(
            status_code=400,
            detail=f"Database integrity error: {error_message}"
        )
    except psycopg2.Error as e:
        db.rollback()
        if cursor:
            cursor.close()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        if cursor:
            cursor.close()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating distribution record: {str(e)}"
        )


# PUT endpoint for distribution_db
@app.put("/distribution", response_model=dict)
async def update_or_create_distribution(
    data: DistributionCreate,
    db=Depends(get_db)
):
    """
    Update existing distribution record for the same date and cart_id by adding values,
    or create a new record if no record exists for that date and cart_id.
    
    For numeric fields: adds the new value to existing value
    """
    cursor = None
    
    # Determine the date to check (defaults to today's date)
    if data.date:
        check_date = data.date.date() if isinstance(data.date, datetime) else data.date
    else:
        check_date = date.today()
    
    try:
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # Check if a record exists for this cart_id and date
        cursor.execute(
            """
            SELECT * FROM distribution_db 
            WHERE cart_id = %s AND DATE(date) = %s
            ORDER BY date DESC
            LIMIT 1
            """,
            (data.cart_id, check_date)
        )
        existing_record = cursor.fetchone()
        
        if existing_record:
            # Record exists - update by adding values
            existing_dict = dict(existing_record)
            
            # Build UPDATE query with addition for numeric fields
            update_fields = []
            update_values = []
            
            # All fields are numeric (int8) in distribution_db
            numeric_fields = [
                "veg", "paneer", "chicken", "cheesecorn", "springroll",
                "attaveg", "attachicken"
            ]
            
            # Process numeric fields - add to existing value
            for field in numeric_fields:
                new_value = getattr(data, field, None)
                if new_value is not None:
                    existing_value = existing_dict.get(field) or 0
                    updated_value = existing_value + new_value
                    update_fields.append(f"{field} = %s")
                    update_values.append(updated_value)
            
            if not update_fields:
                raise HTTPException(
                    status_code=400,
                    detail="At least one field must be provided for update"
                )
            
            # Add the cart_id and date conditions to the WHERE clause
            update_values.extend([data.cart_id, check_date])
            
            update_fields_str = ", ".join(update_fields)
            
            update_query = f"""
                UPDATE distribution_db 
                SET {update_fields_str}
                WHERE cart_id = %s AND DATE(date) = %s
                RETURNING *
            """
            
            cursor.execute(update_query, update_values)
            db.commit()
            
            result = cursor.fetchone()
            cursor.close()
            
            return {
                "status": "success",
                "message": f"Distribution record updated successfully (values added to existing record for cart_id {data.cart_id})",
                "data": dict(result),
                "operation": "update"
            }
        else:
            # No record exists - create a new one
            fields = ["cart_id"]
            values = [data.cart_id]
            placeholders = ["%s"]
            
            # Add date to inserted row
            if data.date and isinstance(data.date, datetime):
                date_datetime = data.date
            else:
                date_datetime = datetime.combine(check_date, time.min)
            
            fields.append("date")
            values.append(date_datetime)
            placeholders.append("%s")
            
            # Add other fields if provided
            field_mapping = {
                "veg": data.veg,
                "paneer": data.paneer,
                "chicken": data.chicken,
                "cheesecorn": data.cheesecorn,
                "springroll": data.springroll,
                "attaveg": data.attaveg,
                "attachicken": data.attachicken,
            }
            
            for field_name, field_value in field_mapping.items():
                if field_value is not None:
                    fields.append(field_name)
                    values.append(field_value)
                    placeholders.append("%s")
            
            fields_str = ", ".join(fields)
            placeholders_str = ", ".join(placeholders)
            
            insert_query = f"""
                INSERT INTO distribution_db ({fields_str})
                VALUES ({placeholders_str})
                RETURNING *
            """
            
            cursor.execute(insert_query, values)
            db.commit()
            
            result = cursor.fetchone()
            cursor.close()
            
            return {
                "status": "success",
                "message": f"Distribution record created successfully (no existing record for cart_id {data.cart_id} on this date)",
                "data": dict(result),
                "operation": "create"
            }
            
    except HTTPException:
        if cursor:
            cursor.close()
        db.rollback()
        raise
    except psycopg2.IntegrityError as e:
        db.rollback()
        if cursor:
            cursor.close()
        raise HTTPException(
            status_code=400,
            detail=f"Database integrity error: {str(e)}"
        )
    except psycopg2.Error as e:
        db.rollback()
        if cursor:
            cursor.close()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        if cursor:
            cursor.close()
        raise HTTPException(
            status_code=500,
            detail=f"Error updating/creating distribution record: {str(e)}"
        )