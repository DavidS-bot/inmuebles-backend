# app/routers/financial_movements.py
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from pydantic import BaseModel
import pandas as pd
import io
from datetime import datetime
import re

from ..db import get_session
from ..deps import get_current_user
from ..models import User, Property, FinancialMovement, ClassificationRule

router = APIRouter(prefix="/financial-movements", tags=["financial-movements"])

# Helper functions for parsing European formats
def parse_european_date(date_str):
    """Parse date in DD/MM/YYYY format"""
    try:
        if pd.isna(date_str) or date_str == "":
            return None
        
        # If it's already a datetime object
        if hasattr(date_str, 'date'):
            return date_str.date()
        
        date_str = str(date_str).strip()
        if not date_str:
            return None
        
        # Try different date formats
        date_formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y']
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        return None
    except Exception as e:
        print(f"ERROR in parse_european_date: {e} for input: {date_str}")
        return None

def parse_european_amount(amount_str):
    """Parse amount in European format: -70,00 € or 1.234,56 €"""
    try:
        if pd.isna(amount_str):
            return None
        
        # If it's already a number
        if isinstance(amount_str, (int, float)):
            return float(amount_str)
        
        amount_str = str(amount_str).strip()
        if not amount_str:
            return None
        
        # Remove currency symbols and whitespace
        amount_str = re.sub(r'[€$£¥]', '', amount_str).strip()
        
        # Handle European number format (comma as decimal separator)
        # Examples: "1.234,56" -> "1234.56", "-70,00" -> "-70.00"
        
        # If there are both dots and commas, assume dot is thousands separator
        if '.' in amount_str and ',' in amount_str:
            # European format: 1.234,56 -> 1234.56
            amount_str = amount_str.replace('.', '').replace(',', '.')
        elif ',' in amount_str:
            # Only comma present, assume it's decimal separator
            amount_str = amount_str.replace(',', '.')
        
        return float(amount_str)
    except Exception as e:
        print(f"ERROR in parse_european_amount: {e} for input: {amount_str}")
        return None

# Pydantic models para request/response
class FinancialMovementCreate(BaseModel):
    property_id: int
    date: date
    concept: str
    amount: float
    category: str
    subcategory: Optional[str] = None
    tenant_name: Optional[str] = None
    bank_balance: Optional[float] = None

class FinancialMovementUpdate(BaseModel):
    date: Optional[date] = None
    concept: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tenant_name: Optional[str] = None
    bank_balance: Optional[float] = None

class FinancialMovementResponse(BaseModel):
    id: int
    property_id: Optional[int] = None
    date: date
    concept: str
    amount: float
    category: str
    subcategory: Optional[str] = None
    tenant_name: Optional[str] = None
    is_classified: bool
    bank_balance: Optional[float] = None

class BulkMovementUpload(BaseModel):
    movements: List[dict]

@router.get("/", response_model=List[FinancialMovementResponse])
def get_financial_movements(
    property_id: Optional[int] = None,
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    unassigned_only: Optional[bool] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get financial movements with optional filters"""
    # Get user's property IDs for filtering
    user_properties = session.exec(
        select(Property).where(Property.owner_id == current_user.id)
    ).all()
    property_ids = [prop.id for prop in user_properties]
    
    # Handle unassigned_only filter first
    if unassigned_only:
        # Only show unassigned movements for the user
        query = select(FinancialMovement).where(
            (FinancialMovement.property_id.is_(None)) & (FinancialMovement.user_id == current_user.id)
        )
    else:
        # Include both movements assigned to user properties AND unassigned movements for the user
        if property_ids:
            query = select(FinancialMovement).where(
                (FinancialMovement.property_id.in_(property_ids)) |
                ((FinancialMovement.property_id.is_(None)) & (FinancialMovement.user_id == current_user.id))
            )
        else:
            # If user has no properties, only show their unassigned movements
            query = select(FinancialMovement).where(
                (FinancialMovement.property_id.is_(None)) & (FinancialMovement.user_id == current_user.id)
            )
        
        if property_id:
            query = query.where(FinancialMovement.property_id == property_id)
    
    if category:
        query = query.where(FinancialMovement.category == category)
    if start_date:
        query = query.where(FinancialMovement.date >= start_date)
    if end_date:
        query = query.where(FinancialMovement.date <= end_date)
    
    movements = session.exec(query).all()
    return movements

@router.post("/bulk-delete")
def delete_all_movements_bulk(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete all financial movements for current user"""
    print(f"DEBUG: delete_all_movements endpoint reached")
    try:
        print(f"DEBUG: delete_all_movements called for user {current_user.id}")
        # Get all user properties first
        user_properties = session.exec(
            select(Property).where(Property.owner_id == current_user.id)
        ).all()
        print(f"DEBUG: Found {len(user_properties)} properties for user")
        
        property_ids = [prop.id for prop in user_properties]
        
        # Delete movements for user properties, or user's unassigned movements
        if property_ids:
            movements = session.exec(
                select(FinancialMovement).where(
                    (FinancialMovement.property_id.in_(property_ids)) | 
                    ((FinancialMovement.property_id.is_(None)) & (FinancialMovement.user_id == current_user.id))
                )
            ).all()
        else:
            # If no properties, only delete user's unassigned movements
            movements = session.exec(
                select(FinancialMovement).where(
                    (FinancialMovement.property_id.is_(None)) & 
                    (FinancialMovement.user_id == current_user.id)
                )
            ).all()
        
        count = len(movements)
        
        for movement in movements:
            session.delete(movement)
        
        session.commit()
        
        return {"message": f"Successfully deleted {count} movements", "count": count}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting movements: {str(e)}")

@router.get("/download-xlsx")
def export_movements_to_excel(
    property_id: Optional[int] = None,
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Export financial movements to Excel file"""
    try:
        # Get user's property IDs for filtering
        user_properties = session.exec(
            select(Property).where(Property.owner_id == current_user.id)
        ).all()
        property_ids = [prop.id for prop in user_properties]
        
        # Build the same query as the GET endpoint
        if property_ids:
            query = select(FinancialMovement).where(
                (FinancialMovement.property_id.in_(property_ids)) |
                ((FinancialMovement.property_id.is_(None)) & (FinancialMovement.user_id == current_user.id))
            )
        else:
            # If user has no properties, only show their unassigned movements
            query = select(FinancialMovement).where(
                (FinancialMovement.property_id.is_(None)) & (FinancialMovement.user_id == current_user.id)
            )
        
        # Apply filters
        if property_id:
            query = query.where(FinancialMovement.property_id == property_id)
        if category:
            query = query.where(FinancialMovement.category == category)
        if start_date:
            query = query.where(FinancialMovement.date >= start_date)
        if end_date:
            query = query.where(FinancialMovement.date <= end_date)
        
        # Get movements
        movements = session.exec(query).all()
        
        # Create property lookup for better display
        property_lookup = {prop.id: prop.address for prop in user_properties}
        
        # Prepare data for Excel
        excel_data = []
        for movement in movements:
            property_address = property_lookup.get(movement.property_id, "Sin propiedad asignada")
            
            excel_data.append({
                "Fecha": movement.date.strftime("%d/%m/%Y"),
                "Propiedad": property_address,
                "Concepto": movement.concept,
                "Categoría": movement.category,
                "Subcategoría": movement.subcategory or "",
                "Inquilino": movement.tenant_name or "",
                "Importe": movement.amount,
                "Clasificado": "Automático" if movement.is_classified else "Manual",
                "Saldo Bancario": movement.bank_balance or ""
            })
        
        if not excel_data:
            raise HTTPException(status_code=404, detail="No movements found with the specified criteria")
        
        # Create DataFrame and Excel file
        df = pd.DataFrame(excel_data)
        
        # Create Excel file in memory
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl', date_format='DD/MM/YYYY') as writer:
            df.to_excel(writer, sheet_name='Movimientos', index=False)
            
            # Get the workbook and worksheet objects
            workbook = writer.book
            worksheet = workbook['Movimientos']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                # Set column width with some padding
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Format the header row
            for cell in worksheet[1]:
                cell.font = workbook.fonts[0].copy(bold=True)
                cell.fill = workbook.fills[0].copy()
        
        excel_buffer.seek(0)
        
        # Generate filename with current date and filters
        filename_parts = ["movimientos"]
        
        if property_id:
            prop_name = property_lookup.get(property_id, f"propiedad_{property_id}")
            filename_parts.append(prop_name.replace(" ", "_").replace(",", "")[:20])
        
        if start_date and end_date:
            filename_parts.append(f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}")
        elif start_date:
            filename_parts.append(f"desde_{start_date.strftime('%Y%m%d')}")
        elif end_date:
            filename_parts.append(f"hasta_{end_date.strftime('%Y%m%d')}")
        
        if category:
            filename_parts.append(category.lower())
        
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_parts.append(current_date)
        
        filename = "_".join(filename_parts) + ".xlsx"
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(excel_buffer.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in export_movements_to_excel: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error exporting movements to Excel: {str(e)}")

@router.post("/", response_model=FinancialMovementResponse)
def create_financial_movement(
    movement_data: FinancialMovementCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new financial movement"""
    # Verify property ownership
    property_obj = session.get(Property, movement_data.property_id)
    if not property_obj or property_obj.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Property not found")
    
    movement = FinancialMovement(**movement_data.dict())
    session.add(movement)
    session.commit()
    session.refresh(movement)
    return movement

@router.get("/{movement_id}", response_model=FinancialMovementResponse)
def get_financial_movement(
    movement_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific financial movement"""
    movement = session.get(FinancialMovement, movement_id)
    if not movement:
        raise HTTPException(status_code=404, detail="Movement not found")
    
    # Verify ownership through property
    property_obj = session.get(Property, movement.property_id)
    if not property_obj or property_obj.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Movement not found")
    
    return movement

@router.put("/{movement_id}", response_model=FinancialMovementResponse)
def update_financial_movement(
    movement_id: int,
    movement_data: FinancialMovementUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update a financial movement"""
    movement = session.get(FinancialMovement, movement_id)
    if not movement:
        raise HTTPException(status_code=404, detail="Movement not found")
    
    # Verify ownership
    property_obj = session.get(Property, movement.property_id)
    if not property_obj or property_obj.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Movement not found")
    
    # Update fields
    for field, value in movement_data.dict(exclude_unset=True).items():
        setattr(movement, field, value)
    
    session.commit()
    session.refresh(movement)
    return movement

@router.delete("/delete-by-date-range")
def delete_movements_by_date_range(
    start_date: str,
    end_date: str,
    property_id: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete financial movements within a specific date range for current user"""
    try:
        print(f"DEBUG: delete_movements_by_date_range called for user {current_user.id}")
        print(f"DEBUG: Date range: {start_date} to {end_date}, property_id: {property_id}")
        
        # Parse dates
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        if start_date_obj > end_date_obj:
            raise HTTPException(status_code=400, detail="Start date must be before end date")
        
        # Get user properties
        user_properties = session.exec(
            select(Property).where(Property.owner_id == current_user.id)
        ).all()
        property_ids = [prop.id for prop in user_properties]
        
        # Build the query
        if property_id and property_id.strip():
            # Convert property_id to int and validate
            try:
                property_id_int = int(property_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="property_id must be a valid integer")
            
            # Specific property - check if user owns it
            if property_id_int not in property_ids:
                raise HTTPException(status_code=403, detail="Property not found or access denied")
            
            movements = session.exec(
                select(FinancialMovement).where(
                    (FinancialMovement.property_id == property_id_int) &
                    (FinancialMovement.date >= start_date_obj) &
                    (FinancialMovement.date <= end_date_obj)
                )
            ).all()
        else:
            # All properties for user + unassigned movements
            movements = session.exec(
                select(FinancialMovement).where(
                    (
                        (FinancialMovement.property_id.in_(property_ids)) |
                        ((FinancialMovement.property_id.is_(None)) & (FinancialMovement.user_id == current_user.id))
                    ) &
                    (FinancialMovement.date >= start_date_obj) &
                    (FinancialMovement.date <= end_date_obj)
                )
            ).all()
        
        count = len(movements)
        print(f"DEBUG: Found {count} movements to delete")
        
        for movement in movements:
            session.delete(movement)
        
        session.commit()
        
        return {
            "message": f"Successfully deleted {count} movements between {start_date} and {end_date}",
            "deleted_count": count,
            "start_date": start_date,
            "end_date": end_date,
            "property_id": property_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in delete_movements_by_date_range: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting movements: {str(e)}")

@router.delete("/{movement_id}")
def delete_financial_movement(
    movement_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a financial movement"""
    movement = session.get(FinancialMovement, movement_id)
    if not movement:
        raise HTTPException(status_code=404, detail="Movement not found")
    
    # Verify ownership
    if movement.property_id:
        # Movement is assigned to a property - check property ownership
        property_obj = session.get(Property, movement.property_id)
        if not property_obj or property_obj.owner_id != current_user.id:
            raise HTTPException(status_code=404, detail="Movement not found")
    else:
        # Movement is unassigned - check if it belongs to current user
        if movement.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Movement not found")
    
    session.delete(movement)
    session.commit()
    return {"message": "Movement deleted successfully"}

@router.post("/bulk-upload")
def bulk_upload_movements(
    property_id: int,
    upload_data: BulkMovementUpload,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Bulk upload financial movements from bank statements"""
    # Verify property ownership
    property_obj = session.get(Property, property_id)
    if not property_obj or property_obj.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Property not found")
    
    created_movements = []
    
    for movement_data in upload_data.movements:
        try:
            movement = FinancialMovement(
                property_id=property_id,
                date=movement_data.get("date"),
                concept=movement_data.get("concept", ""),
                amount=float(movement_data.get("amount", 0)),
                category=movement_data.get("category", "Sin clasificar"),
                subcategory=movement_data.get("subcategory"),
                tenant_name=movement_data.get("tenant_name"),
                is_classified=movement_data.get("is_classified", False),
                bank_balance=movement_data.get("bank_balance")
            )
            session.add(movement)
            created_movements.append(movement)
        except Exception as e:
            # Skip invalid movements but continue processing
            continue
    
    session.commit()
    return {"message": f"Created {len(created_movements)} movements", "count": len(created_movements)}

@router.post("/upload-excel")
def upload_excel_bank_statement(
    property_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Upload and process Excel bank statement"""
    # Verify property ownership
    property_obj = session.get(Property, property_id)
    if not property_obj or property_obj.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Validate file type
    if not file.filename.lower().endswith(('.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="Only Excel files (.xls, .xlsx) are allowed")
    
    try:
        # Read Excel file
        contents = file.file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Expected columns: Fecha, Concepto, Importe
        expected_columns = ['Fecha', 'Concepto', 'Importe']
        
        # Check if required columns exist (case insensitive)
        df_columns = df.columns.str.lower().tolist()
        required_columns = [col.lower() for col in expected_columns]
        
        missing_columns = [col for col in required_columns if col not in df_columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_columns)}. Expected: Fecha, Concepto, Importe"
            )
        
        # Normalize column names
        column_mapping = {}
        for expected_col in expected_columns:
            for df_col in df.columns:
                if df_col.lower() == expected_col.lower():
                    column_mapping[df_col] = expected_col
                    break
        
        df = df.rename(columns=column_mapping)
        
        # Load classification rules for this property
        rules_query = select(ClassificationRule).where(ClassificationRule.property_id == property_id)
        rules = session.exec(rules_query).all()
        
        created_movements = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Parse date using European format parser
                parsed_date = parse_european_date(row['Fecha'])
                if not parsed_date:
                    errors.append(f"Row {index + 1}: Invalid or missing date: {row['Fecha']}")
                    continue
                
                # Parse amount using European format parser
                amount = parse_european_amount(row['Importe'])
                if amount is None:
                    errors.append(f"Row {index + 1}: Invalid or missing amount: {row['Importe']}")
                    continue
                concept = str(row['Concepto']) if not pd.isna(row['Concepto']) else ""
                
                # Auto-classify based on rules
                category = "Sin clasificar"
                subcategory = None
                tenant_name = None
                is_classified = False
                
                for rule in rules:
                    if rule.keyword.lower() in concept.lower():
                        category = rule.category
                        subcategory = rule.subcategory
                        tenant_name = rule.tenant_name
                        is_classified = True
                        break
                
                # Create movement
                movement = FinancialMovement(
                    property_id=property_id,
                    date=parsed_date,
                    concept=concept,
                    amount=amount,
                    category=category,
                    subcategory=subcategory,
                    tenant_name=tenant_name,
                    is_classified=is_classified
                )
                session.add(movement)
                created_movements.append(movement)
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
                continue
        
        # Commit all valid movements
        session.commit()
        
        return {
            "message": f"Successfully processed Excel file",
            "created_movements": len(created_movements),
            "total_rows": len(df),
            "errors": errors[:10]  # Limit to first 10 errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing Excel file: {str(e)}")

@router.post("/upload-excel-global")
def upload_excel_global_movements(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Upload Excel and create movements with automatic rule-based classification"""
    print("=== UPLOAD EXCEL GLOBAL STARTED V2 ===")
    
    # Validate file type
    if not file.filename.lower().endswith(('.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="Only Excel files (.xls, .xlsx) are allowed")
    
    try:
        # Read Excel file
        print("EXCEL PARSING: Reading file contents...")
        contents = file.file.read()
        print(f"EXCEL PARSING: File size: {len(contents)} bytes")
        
        print("EXCEL PARSING: Creating DataFrame...")
        df = pd.read_excel(io.BytesIO(contents))
        print(f"EXCEL PARSING: DataFrame created with {len(df)} rows and {len(df.columns)} columns")
        print(f"EXCEL PARSING: Columns found: {list(df.columns)}")
        
        # Expected columns: Fecha, Concepto, Importe
        expected_columns = ['Fecha', 'Concepto', 'Importe']
        
        # Check if required columns exist (case insensitive)
        df_columns = df.columns.str.lower().tolist()
        required_columns = [col.lower() for col in expected_columns]
        
        missing_columns = [col for col in required_columns if col not in df_columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_columns)}. Expected: Fecha, Concepto, Importe"
            )
        
        # Normalize column names
        column_mapping = {}
        for expected_col in expected_columns:
            for df_col in df.columns:
                if df_col.lower() == expected_col.lower():
                    column_mapping[df_col] = expected_col
                    break
        
        df = df.rename(columns=column_mapping)
        print(f"EXCEL PARSING: Successfully renamed columns")
        
        # Load all classification rules for the user (from all user properties)
        print("CLASSIFICATION: Loading user properties...")
        user_properties = session.exec(
            select(Property).where(Property.owner_id == current_user.id)
        ).all()
        property_ids = [prop.id for prop in user_properties]
        print(f"CLASSIFICATION: Found {len(user_properties)} properties: {property_ids}")
        
        rules = []
        if property_ids:
            rules = session.exec(
                select(ClassificationRule).where(
                    ClassificationRule.property_id.in_(property_ids) & 
                    ClassificationRule.is_active == True
                )
            ).all()
        
        print(f"CLASSIFICATION: Found {len(rules)} classification rules for user")
        for rule in rules:
            print(f"  Rule: '{rule.keyword}' -> Property {rule.property_id}, Category: {rule.category}")
        
        # Check for duplicates based on date, concept, and amount
        existing_movements = session.exec(
            select(FinancialMovement).where(FinancialMovement.user_id == current_user.id)
        ).all()
        
        existing_signatures = set()
        for movement in existing_movements:
            signature = f"{movement.date}|{movement.concept}|{movement.amount}"
            existing_signatures.add(signature)
        
        created_movements = []
        duplicates_skipped = 0
        errors = []
        
        print(f"EXCEL PROCESSING: Starting to process {len(df)} rows from Excel")
        
        for index, row in df.iterrows():
            print(f"EXCEL PROCESSING: Processing row {index + 1}")
            try:
                # Parse date using European format parser
                print(f"EXCEL DATE PARSING: Row {index + 1} - Processing date: {row['Fecha']}")
                parsed_date = parse_european_date(row['Fecha'])
                if not parsed_date:
                    errors.append(f"Row {index + 1}: Invalid or missing date: {row['Fecha']}")
                    continue
                
                print(f"EXCEL DATE PARSING: Successfully parsed to: {parsed_date}")
                
                # Additional validation - check if date is reasonable
                from datetime import date
                if parsed_date < date(2020, 1, 1) or parsed_date > date(2030, 12, 31):
                    print(f"EXCEL DATE WARNING: Row {index + 1} - Date {parsed_date} seems unusual")
                    errors.append(f"Row {index + 1}: Date {parsed_date} seems out of reasonable range")
                
                # Parse amount using European format parser
                print(f"EXCEL AMOUNT PARSING: Row {index + 1} - Processing amount: {row['Importe']}")
                amount = parse_european_amount(row['Importe'])
                if amount is None:
                    errors.append(f"Row {index + 1}: Invalid or missing amount: {row['Importe']}")
                    continue
                
                print(f"EXCEL AMOUNT PARSING: Successfully parsed to: {amount}")
                concept = str(row['Concepto']) if not pd.isna(row['Concepto']) else ""
                
                # Clean concept from Bankinter coletillas
                import re
                concept = re.sub(r'Pulsa para ver detalle.*$', '', concept, flags=re.IGNORECASE | re.MULTILINE)
                concept = re.sub(r'\n.*Pulsa para ver.*$', '', concept, flags=re.IGNORECASE | re.MULTILINE)
                concept = re.sub(r'.*Pulsa para ver.*', '', concept, flags=re.IGNORECASE)
                concept = re.sub(r'\n+', ' ', concept)
                concept = re.sub(r'\s+', ' ', concept)
                concept = concept.strip()
                
                # Check for duplicates
                signature = f"{parsed_date}|{concept}|{amount}"
                if signature in existing_signatures:
                    duplicates_skipped += 1
                    print(f"DUPLICATE FOUND: Skipping '{concept}' - already exists")
                    continue
                
                # Apply classification rules
                matched_property_id = None
                category = "Sin clasificar"
                subcategory = None
                tenant_name = None
                is_classified = False
                
                # Check all rules for matches with improved matching
                print(f"CLASSIFICATION: Testing concept '{concept}' against {len(rules)} rules")
                best_match = None
                best_score = 0
                
                # Normalize concept for better matching
                concept_normalized = concept.upper().strip()
                
                for rule in rules:
                    rule_keyword = rule.keyword.upper().strip()
                    print(f"CLASSIFICATION: Testing rule '{rule_keyword}' vs concept '{concept_normalized}'")
                    
                    # Calculate match score
                    if rule_keyword in concept_normalized:
                        # Score based on how much of the concept the keyword covers
                        score = len(rule_keyword) / len(concept_normalized) if concept_normalized else 0
                        print(f"CLASSIFICATION: Match found with score {score:.2f}")
                        
                        if score > best_score:
                            best_score = score
                            best_match = rule
                            print(f"CLASSIFICATION: New best match: '{rule_keyword}' with score {score:.2f}")
                    else:
                        print(f"CLASSIFICATION: No match for rule '{rule_keyword}'")
                
                # Apply best match if found
                if best_match and best_score > 0.1:  # Minimum threshold
                    matched_property_id = best_match.property_id
                    category = best_match.category
                    subcategory = best_match.subcategory
                    tenant_name = best_match.tenant_name
                    is_classified = True
                    print(f"CLASSIFICATION: *** BEST MATCH APPLIED *** '{best_match.keyword}' -> Property {best_match.property_id} (score: {best_score:.2f})")
                else:
                    print(f"CLASSIFICATION: No suitable match found")
                
                # Create movement with classification applied
                movement = FinancialMovement(
                    user_id=current_user.id,
                    property_id=matched_property_id,  # Assign to property if rule matched
                    date=parsed_date,
                    concept=concept,
                    amount=amount,
                    category=category,
                    subcategory=subcategory,
                    tenant_name=tenant_name,
                    is_classified=is_classified
                )
                session.add(movement)
                created_movements.append(movement)
                existing_signatures.add(signature)  # Prevent duplicates within same upload
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
                continue
        
        # Commit all valid movements
        session.commit()
        
        print(f"EXCEL SUMMARY: Total rows: {len(df)}, Created: {len(created_movements)}, Duplicates: {duplicates_skipped}, Errors: {len(errors)}")
        
        return {
            "message": f"Successfully processed Excel file",
            "created_movements": len(created_movements),
            "total_rows": len(df),
            "duplicates_skipped": duplicates_skipped,
            "errors": errors[:10]  # Limit to first 10 errors
        }
        
    except Exception as e:
        print(f"EXCEL ERROR: Exception occurred: {str(e)}")
        print(f"EXCEL ERROR: Exception type: {type(e).__name__}")
        import traceback
        print(f"EXCEL ERROR: Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Error processing Excel file: {str(e)}")

@router.put("/{movement_id}/assign-property")
def assign_movement_to_property(
    movement_id: int,
    property_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Assign a movement to a specific property"""
    # Get movement
    movement = session.get(FinancialMovement, movement_id)
    if not movement or movement.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Movement not found")
    
    # Verify property ownership
    property_obj = session.get(Property, property_id)
    if not property_obj or property_obj.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Assign property
    movement.property_id = property_id
    session.commit()
    session.refresh(movement)
    
    return movement

@router.post("/extract-concepts")
def extract_concepts_from_excel(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Extract unique concepts from Excel file for rule creation"""
    # Validate file type
    if not file.filename.lower().endswith(('.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="Only Excel files (.xls, .xlsx) are allowed")
    
    try:
        # Read Excel file
        contents = file.file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Expected columns: Fecha, Concepto, Importe
        expected_columns = ['Fecha', 'Concepto', 'Importe']
        
        # Check if required columns exist (case insensitive)
        df_columns = df.columns.str.lower().tolist()
        required_columns = [col.lower() for col in expected_columns]
        
        missing_columns = [col for col in required_columns if col not in df_columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_columns)}. Expected: Fecha, Concepto, Importe"
            )
        
        # Normalize column names
        column_mapping = {}
        for expected_col in expected_columns:
            for df_col in df.columns:
                if df_col.lower() == expected_col.lower():
                    column_mapping[df_col] = expected_col
                    break
        
        df = df.rename(columns=column_mapping)
        
        # Extract unique concepts with their frequency and sample amounts
        concept_analysis = []
        concept_groups = df.groupby('Concepto')
        
        for concept, group in concept_groups:
            if pd.isna(concept) or concept.strip() == "":
                continue
                
            amounts = group['Importe'].dropna()
            if len(amounts) == 0:
                continue
                
            concept_info = {
                "concept": str(concept).strip(),
                "frequency": len(group),
                "avg_amount": float(amounts.mean()),
                "min_amount": float(amounts.min()),
                "max_amount": float(amounts.max()),
                "is_income": bool(amounts.mean() > 0),
                "sample_dates": group['Fecha'].dropna().astype(str).head(3).tolist()
            }
            concept_analysis.append(concept_info)
        
        # Sort by frequency (most common first)
        concept_analysis.sort(key=lambda x: x['frequency'], reverse=True)
        
        return {
            "total_rows": len(df),
            "unique_concepts": len(concept_analysis),
            "concepts": concept_analysis,
            "file_name": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing Excel file: {str(e)}")

@router.get("/property/{property_id}/summary")
def get_property_financial_summary(
    property_id: int,
    year: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get financial summary for a property"""
    # Verify property ownership
    property_obj = session.get(Property, property_id)
    if not property_obj or property_obj.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Property not found")
    
    query = select(FinancialMovement).where(FinancialMovement.property_id == property_id)
    
    if year:
        from datetime import datetime
        start_date = datetime(year, 1, 1).date()
        end_date = datetime(year, 12, 31).date()
        query = query.where(FinancialMovement.date >= start_date, FinancialMovement.date <= end_date)
    
    movements = session.exec(query).all()
    
    # Calculate summary by category
    summary = {}
    total_income = 0
    total_expenses = 0
    
    for movement in movements:
        category = movement.category
        if category not in summary:
            summary[category] = {"total": 0, "count": 0}
        
        summary[category]["total"] += movement.amount
        summary[category]["count"] += 1
        
        if movement.amount > 0:
            total_income += movement.amount
        else:
            total_expenses += abs(movement.amount)
    
    return {
        "property_id": property_id,
        "year": year,
        "summary_by_category": summary,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_cash_flow": total_income - total_expenses,
        "total_movements": len(movements)
    }

@router.get("/property/{property_id}/monthly")
def get_property_monthly_breakdown(
    property_id: int,
    year: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get monthly breakdown for a property"""
    # Verify property ownership
    property_obj = session.get(Property, property_id)
    if not property_obj or property_obj.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Set year to current year if not provided
    if not year:
        from datetime import datetime
        year = datetime.now().year
    
    from datetime import datetime
    start_date = datetime(year, 1, 1).date()
    end_date = datetime(year, 12, 31).date()
    
    # Get all movements for the property in the specified year
    movements = session.exec(
        select(FinancialMovement).where(
            FinancialMovement.property_id == property_id,
            FinancialMovement.date >= start_date,
            FinancialMovement.date <= end_date
        )
    ).all()
    
    # Initialize monthly data structure
    months = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    
    monthly_data = {}
    for i, month_name in enumerate(months, 1):
        monthly_data[i] = {
            "month": month_name,
            "income": 0.0,
            "expenses": 0.0,
            "net": 0.0,
            "movements_count": 0
        }
    
    # Process movements by month
    for movement in movements:
        month_num = movement.date.month
        monthly_data[month_num]["movements_count"] += 1
        
        if movement.amount > 0:
            monthly_data[month_num]["income"] += movement.amount
        else:
            monthly_data[month_num]["expenses"] += abs(movement.amount)
    
    # Calculate net cash flow for each month
    for month_data in monthly_data.values():
        month_data["net"] = month_data["income"] - month_data["expenses"]
    
    return {
        "property_id": property_id,
        "year": year,
        "monthly_data": [monthly_data[i] for i in range(1, 13)]
    }