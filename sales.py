from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from database import get_db_connection
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date, time

router = APIRouter(prefix="/sales", tags=["sales"])


def get_db():
    """Dependency to get database connection"""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


# Pydantic models for cart_sales_db
class CartSalesCreate(BaseModel):
    """Model for creating cart sales records"""
    cart_id: int
    half_vegsteam: Optional[int] = None
    full_vegsteam: Optional[int] = None
    half_vegfried: Optional[int] = None
    full_vegfried: Optional[int] = None
    half_vegkurkure: Optional[int] = None
    full_vegkurkure: Optional[int] = None
    half_paneersteam: Optional[int] = None
    full_paneersteam: Optional[int] = None
    half_paneerfried: Optional[int] = None
    full_paneerfried: Optional[int] = None
    half_paneerkurkure: Optional[int] = None
    full_paneerkurkure: Optional[int] = None
    half_chickensteam: Optional[int] = None
    full_chickensteam: Optional[int] = None
    half_chickenfried: Optional[int] = None
    full_chickenfried: Optional[int] = None
    half_chickenkurkure: Optional[int] = None
    full_chickenkurkure: Optional[int] = None
    half_cheesecornsteam: Optional[int] = None
    full_cheesecorsteamn: Optional[int] = None  # Note: keeping typo as in DB
    half_cheesecornfried: Optional[int] = None
    full_cheesecornfried: Optional[int] = None
    half_cheesecornkurkure: Optional[int] = None
    full_cheesecornkurkure: Optional[int] = None
    half_springroll: Optional[int] = None
    full_springroll: Optional[int] = None
    half_springrollkurkure: Optional[int] = None
    full_springrollkurkure: Optional[int] = None
    half_attavegsteam: Optional[int] = None
    full_attavegsteam: Optional[int] = None
    half_attachickensteam: Optional[int] = None
    full_attachickensteam: Optional[int] = None
    cash_total: Optional[int] = None
    upi_total: Optional[int] = None
    Shift_timing: Optional[float] = None  # Shift timing as float (float8)
    created_at: Optional[date] = None  # Optional, defaults to now() in DB


class CartSalesResponse(BaseModel):
    """Model for cart sales record response"""
    created_at: date
    cart_id: int
    half_vegsteam: Optional[int] = None
    full_vegsteam: Optional[int] = None
    half_vegfried: Optional[int] = None
    full_vegfried: Optional[int] = None
    half_vegkurkure: Optional[int] = None
    full_vegkurkure: Optional[int] = None
    half_paneersteam: Optional[int] = None
    full_paneersteam: Optional[int] = None
    half_paneerfried: Optional[int] = None
    full_paneerfried: Optional[int] = None
    half_paneerkurkure: Optional[int] = None
    full_paneerkurkure: Optional[int] = None
    half_chickensteam: Optional[int] = None
    full_chickensteam: Optional[int] = None
    half_chickenfried: Optional[int] = None
    full_chickenfried: Optional[int] = None
    half_chickenkurkure: Optional[int] = None
    full_chickenkurkure: Optional[int] = None
    half_cheesecornsteam: Optional[int] = None
    full_cheesecorsteamn: Optional[int] = None
    half_cheesecornfried: Optional[int] = None
    full_cheesecornfried: Optional[int] = None
    half_cheesecornkurkure: Optional[int] = None
    full_cheesecornkurkure: Optional[int] = None
    half_springroll: Optional[int] = None
    full_springroll: Optional[int] = None
    half_springrollkurkure: Optional[int] = None
    full_springrollkurkure: Optional[int] = None
    half_attavegsteam: Optional[int] = None
    full_attavegsteam: Optional[int] = None
    half_attachickensteam: Optional[int] = None
    full_attachickensteam: Optional[int] = None
    cash_total: Optional[int] = None
    upi_total: Optional[int] = None
    Shift_timing: Optional[float] = None


# GET endpoints for cart_sales_db
@router.get("", response_model=list[dict])
async def get_all_cart_sales(
    db=Depends(get_db),
    cart_id: Optional[int] = Query(None, description="Filter by cart_id"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get all cart sales records with optional filtering by cart_id and/or date"""
    try:
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # Build query with optional filters
        query = "SELECT * FROM cart_sales_db WHERE 1=1"
        params = []
        
        if cart_id is not None:
            query += " AND cart_id = %s"
            params.append(cart_id)
        
        if date is not None:
            query += " AND created_at = %s"
            params.append(date)
        
        query += " ORDER BY created_at DESC, cart_id ASC LIMIT %s OFFSET %s"
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
            detail=f"Error fetching cart sales records: {str(e)}"
        )


@router.get("/{cart_id}", response_model=list[dict])
async def get_cart_sales_by_cart_id(
    cart_id: int,
    db=Depends(get_db),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)")
):
    """Get cart sales records for a specific cart_id, optionally filtered by date"""
    try:
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        query = "SELECT * FROM cart_sales_db WHERE cart_id = %s"
        params = [cart_id]
        
        if date is not None:
            query += " AND created_at = %s"
            params.append(date)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        
        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No cart sales records found for cart_id: {cart_id}"
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
            detail=f"Error fetching cart sales records: {str(e)}"
        )


@router.get("/date/{date}", response_model=list[dict])
async def get_cart_sales_by_date(
    date: str,
    db=Depends(get_db),
    cart_id: Optional[int] = Query(None, description="Filter by cart_id")
):
    """Get cart sales records for a specific date, optionally filtered by cart_id"""
    try:
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        query = "SELECT * FROM cart_sales_db WHERE created_at = %s"
        params = [date]
        
        if cart_id is not None:
            query += " AND cart_id = %s"
            params.append(cart_id)
        
        query += " ORDER BY cart_id ASC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        
        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No cart sales records found for date: {date}"
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
            detail=f"Error fetching cart sales records: {str(e)}"
        )


# POST endpoint for cart_sales_db
@router.post("", response_model=dict)
async def create_cart_sales(
    data: CartSalesCreate,
    db=Depends(get_db)
):
    """Create a new cart sales record. If record exists for same date and cart_id, returns error."""
    cursor = None
    try:
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # Determine the date to check
        if data.created_at:
            check_date = data.created_at
        else:
            check_date = date.today()
        
        # Check if a record already exists for this cart_id and date
        cursor.execute(
            """
            SELECT * FROM cart_sales_db 
            WHERE cart_id = %s AND created_at = %s
            LIMIT 1
            """,
            (data.cart_id, check_date)
        )
        existing_record = cursor.fetchone()
        
        if existing_record:
            raise HTTPException(
                status_code=409,
                detail=f"Cart sales record already exists for cart_id {data.cart_id} on date {check_date}. Use PUT endpoint to update."
            )
        
        # Build the INSERT query
        fields = ["cart_id"]
        values = [data.cart_id]
        placeholders = ["%s"]
        
        # Add created_at if provided, otherwise let DB use default (now())
        if data.created_at:
            fields.append("created_at")
            values.append(data.created_at)
            placeholders.append("%s")
        
        # Add other fields if provided
        field_mapping = {
            "half_vegsteam": data.half_vegsteam,
            "full_vegsteam": data.full_vegsteam,
            "half_vegfried": data.half_vegfried,
            "full_vegfried": data.full_vegfried,
            "half_vegkurkure": data.half_vegkurkure,
            "full_vegkurkure": data.full_vegkurkure,
            "half_paneersteam": data.half_paneersteam,
            "full_paneersteam": data.full_paneersteam,
            "half_paneerfried": data.half_paneerfried,
            "full_paneerfried": data.full_paneerfried,
            "half_paneerkurkure": data.half_paneerkurkure,
            "full_paneerkurkure": data.full_paneerkurkure,
            "half_chickensteam": data.half_chickensteam,
            "full_chickensteam": data.full_chickensteam,
            "half_chickenfried": data.half_chickenfried,
            "full_chickenfried": data.full_chickenfried,
            "half_chickenkurkure": data.half_chickenkurkure,
            "full_chickenkurkure": data.full_chickenkurkure,
            "half_cheesecornsteam": data.half_cheesecornsteam,
            "full_cheesecorsteamn": data.full_cheesecorsteamn,
            "half_cheesecornfried": data.half_cheesecornfried,
            "full_cheesecornfried": data.full_cheesecornfried,
            "half_cheesecornkurkure": data.half_cheesecornkurkure,
            "full_cheesecornkurkure": data.full_cheesecornkurkure,
            "half_springroll": data.half_springroll,
            "full_springroll": data.full_springroll,
            "half_springrollkurkure": data.half_springrollkurkure,
            "full_springrollkurkure": data.full_springrollkurkure,
            "half_attavegsteam": data.half_attavegsteam,
            "full_attavegsteam": data.full_attavegsteam,
            "half_attachickensteam": data.half_attachickensteam,
            "full_attachickensteam": data.full_attachickensteam,
            "cash_total": data.cash_total,
            "upi_total": data.upi_total,
            "Shift_timing": data.Shift_timing,
        }
        
        for field_name, field_value in field_mapping.items():
            if field_value is not None:
                fields.append(field_name)
                values.append(field_value)
                placeholders.append("%s")
        
        # Quote column names that might be case-sensitive (Shift_timing)
        quoted_fields = []
        for field in fields:
            if field == "Shift_timing":
                quoted_fields.append('"Shift_timing"')  # Quote for case sensitivity
            else:
                quoted_fields.append(field)
        fields_str = ", ".join(quoted_fields)
        placeholders_str = ", ".join(placeholders)
        
        query = f"""
            INSERT INTO cart_sales_db ({fields_str})
            VALUES ({placeholders_str})
            RETURNING *
        """
        
        cursor.execute(query, values)
        db.commit()
        
        result = cursor.fetchone()
        cursor.close()
        
        return {
            "status": "success",
            "message": "Cart sales record created successfully",
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
        raise HTTPException(
            status_code=400,
            detail=f"Database integrity error: {str(e)}"
        )
    except psycopg2.Error as e:
        db.rollback()
        if cursor:
            cursor.close()
        import traceback
        error_detail = f"Database error: {str(e)}"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )
    except Exception as e:
        db.rollback()
        if cursor:
            cursor.close()
        import traceback
        error_detail = f"Error creating cart sales record: {str(e)}"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )


# PUT endpoint for cart_sales_db
@router.put("", response_model=dict)
async def update_or_create_cart_sales(
    data: CartSalesCreate,
    db=Depends(get_db)
):
    """
    Update existing cart sales record for the same date and cart_id by adding values,
    or create a new record if no record exists for that date and cart_id.
    
    For numeric fields: adds the new value to existing value
    For Shift_timing: replaces the existing value
    """
    cursor = None
    
    # Determine the date to check
    if data.created_at:
        check_date = data.created_at
    else:
        check_date = date.today()
    
    try:
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # Check if a record exists for this cart_id and date
        cursor.execute(
            """
            SELECT * FROM cart_sales_db 
            WHERE cart_id = %s AND created_at = %s
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
            
            # Numeric fields that should be added
            numeric_fields = [
                "half_vegsteam", "full_vegsteam", "half_vegfried", "full_vegfried",
                "half_vegkurkure", "full_vegkurkure", "half_paneersteam", "full_paneersteam",
                "half_paneerfried", "full_paneerfried", "half_paneerkurkure", "full_paneerkurkure",
                "half_chickensteam", "full_chickensteam", "half_chickenfried", "full_chickenfried",
                "half_chickenkurkure", "full_chickenkurkure", "half_cheesecornsteam", "full_cheesecorsteamn",
                "half_cheesecornfried", "full_cheesecornfried", "half_cheesecornkurkure", "full_cheesecornkurkure",
                "half_springroll", "full_springroll", "half_springrollkurkure", "full_springrollkurkure",
                "half_attavegsteam", "full_attavegsteam", "half_attachickensteam", "full_attachickensteam",
                "cash_total", "upi_total"
            ]
            
            # Process numeric fields - add to existing value
            for field in numeric_fields:
                new_value = getattr(data, field, None)
                if new_value is not None:
                    existing_value = existing_dict.get(field) or 0
                    updated_value = existing_value + new_value
                    update_fields.append(f"{field} = %s")
                    update_values.append(updated_value)
            
            # Process Shift_timing - replace existing value (quote it for case sensitivity)
            if data.Shift_timing is not None:
                update_fields.append('"Shift_timing" = %s')
                update_values.append(data.Shift_timing)
            
            if not update_fields:
                raise HTTPException(
                    status_code=400,
                    detail="At least one field must be provided for update"
                )
            
            # Add the cart_id and date conditions to the WHERE clause
            update_values.extend([data.cart_id, check_date])
            
            update_fields_str = ", ".join(update_fields)
            
            update_query = f"""
                UPDATE cart_sales_db 
                SET {update_fields_str}
                WHERE cart_id = %s AND created_at = %s
                RETURNING *
            """
            
            cursor.execute(update_query, update_values)
            db.commit()
            
            result = cursor.fetchone()
            cursor.close()
            
            return {
                "status": "success",
                "message": f"Cart sales record updated successfully (values added to existing record for cart_id {data.cart_id})",
                "data": dict(result),
                "operation": "update"
            }
        else:
            # No record exists - create a new one
            fields = ["cart_id"]
            values = [data.cart_id]
            placeholders = ["%s"]
            
            # Add created_at
            fields.append("created_at")
            values.append(check_date)
            placeholders.append("%s")
            
            # Add other fields if provided
            field_mapping = {
                "half_vegsteam": data.half_vegsteam,
                "full_vegsteam": data.full_vegsteam,
                "half_vegfried": data.half_vegfried,
                "full_vegfried": data.full_vegfried,
                "half_vegkurkure": data.half_vegkurkure,
                "full_vegkurkure": data.full_vegkurkure,
                "half_paneersteam": data.half_paneersteam,
                "full_paneersteam": data.full_paneersteam,
                "half_paneerfried": data.half_paneerfried,
                "full_paneerfried": data.full_paneerfried,
                "half_paneerkurkure": data.half_paneerkurkure,
                "full_paneerkurkure": data.full_paneerkurkure,
                "half_chickensteam": data.half_chickensteam,
                "full_chickensteam": data.full_chickensteam,
                "half_chickenfried": data.half_chickenfried,
                "full_chickenfried": data.full_chickenfried,
                "half_chickenkurkure": data.half_chickenkurkure,
                "full_chickenkurkure": data.full_chickenkurkure,
                "half_cheesecornsteam": data.half_cheesecornsteam,
                "full_cheesecorsteamn": data.full_cheesecorsteamn,
                "half_cheesecornfried": data.half_cheesecornfried,
                "full_cheesecornfried": data.full_cheesecornfried,
                "half_cheesecornkurkure": data.half_cheesecornkurkure,
                "full_cheesecornkurkure": data.full_cheesecornkurkure,
                "half_springroll": data.half_springroll,
                "full_springroll": data.full_springroll,
                "half_springrollkurkure": data.half_springrollkurkure,
                "full_springrollkurkure": data.full_springrollkurkure,
                "half_attavegsteam": data.half_attavegsteam,
                "full_attavegsteam": data.full_attavegsteam,
                "half_attachickensteam": data.half_attachickensteam,
                "full_attachickensteam": data.full_attachickensteam,
                "cash_total": data.cash_total,
                "upi_total": data.upi_total,
                "Shift_timing": data.Shift_timing,
            }
            
            for field_name, field_value in field_mapping.items():
                if field_value is not None:
                    fields.append(field_name)
                    values.append(field_value)
                    placeholders.append("%s")
            
            # Quote column names that might be case-sensitive (Shift_timing)
            quoted_fields = []
            for field in fields:
                if field == "Shift_timing":
                    quoted_fields.append('"Shift_timing"')
                else:
                    quoted_fields.append(field)
            fields_str = ", ".join(quoted_fields)
            placeholders_str = ", ".join(placeholders)
            
            insert_query = f"""
                INSERT INTO cart_sales_db ({fields_str})
                VALUES ({placeholders_str})
                RETURNING *
            """
            
            cursor.execute(insert_query, values)
            db.commit()
            
            result = cursor.fetchone()
            cursor.close()
            
            return {
                "status": "success",
                "message": f"Cart sales record created successfully (no existing record for cart_id {data.cart_id} on this date)",
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
        error_detail = f"Database error: {str(e)}"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )
    except Exception as e:
        db.rollback()
        if cursor:
            cursor.close()
        error_detail = f"Error updating/creating cart sales record: {str(e)}"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )
