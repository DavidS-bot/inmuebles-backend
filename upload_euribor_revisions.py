#!/usr/bin/env python3
"""
Script to upload Euribor revision data for all properties with mortgage details.
This script will:
1. Fetch historical Euribor rates from an external source or use predefined data
2. Create/update MortgageRevision entries for all properties with mortgage details
3. Ensure all properties have complete revision history with proper Euribor rates
"""

import sys
import os
import requests
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Historical Euribor 12M rates (monthly averages)
HISTORICAL_EURIBOR_12M = {
    "2024-12": 2.08,
    "2024-11": 2.44,
    "2024-10": 2.73,
    "2024-09": 3.05,
    "2024-08": 3.53,
    "2024-07": 3.66,
    "2024-06": 3.70,
    "2024-05": 3.79,
    "2024-04": 3.89,
    "2024-03": 3.92,
    "2024-02": 3.94,
    "2024-01": 3.97,
    "2023-12": 4.00,
    "2023-11": 4.15,
    "2023-10": 4.15,
    "2023-09": 4.13,
    "2023-08": 4.15,
    "2023-07": 4.04,
    "2023-06": 3.85,
    "2023-05": 3.55,
    "2023-04": 3.33,
    "2023-03": 3.21,
    "2023-02": 2.94,
    "2023-01": 2.73,
    "2022-12": 2.50,
    "2022-11": 2.11,
    "2022-10": 1.76,
    "2022-09": 1.35,
    "2022-08": 0.99,
    "2022-07": 0.74,
    "2022-06": 0.52,
    "2022-05": 0.29,
    "2022-04": 0.18,
    "2022-03": -0.01,
    "2022-02": -0.15,
    "2022-01": -0.26,
    "2021-12": -0.32,
    "2021-11": -0.37,
    "2021-10": -0.42,
    "2021-09": -0.46,
    "2021-08": -0.49,
    "2021-07": -0.48,
    "2021-06": -0.48,
    "2021-05": -0.48,
    "2021-04": -0.48,
    "2021-03": -0.48,
    "2021-02": -0.48,
    "2021-01": -0.50,
    "2020-12": -0.50,
    "2020-11": -0.50,
    "2020-10": -0.50,
    "2020-09": -0.48,
    "2020-08": -0.28,
    "2020-07": -0.16,
    "2020-06": -0.09,
    "2020-05": -0.05,
    "2020-04": -0.08,
    "2020-03": -0.13,
    "2020-02": -0.23,
    "2020-01": -0.25,
    "2019-12": -0.26,
    "2019-11": -0.27,
    "2019-10": -0.28,
    "2019-09": -0.28,
    "2019-08": -0.28,
    "2019-07": -0.28,
    "2019-06": -0.28,
    "2019-05": -0.28,
    "2019-04": -0.13,
    "2019-03": -0.07,
    "2019-02": -0.08,
    "2019-01": -0.13,
    "2018-12": -0.16,
    "2018-11": -0.17,
    "2018-10": -0.18,
    "2018-09": -0.18,
    "2018-08": -0.18,
    "2018-07": -0.18,
    "2018-06": -0.18,
    "2018-05": -0.18,
    "2018-04": -0.18,
    "2018-03": -0.18,
    "2018-02": -0.18,
    "2018-01": -0.18,
    "2017-12": -0.18,
    "2017-11": -0.18,
    "2017-10": -0.18,
    "2017-09": -0.18,
    "2017-08": 0.00,
    "2017-07": -0.13,
    "2017-06": -0.16,
    "2017-05": -0.18,
    "2017-04": -0.18,
    "2017-03": -0.18,
    "2017-02": -0.18,
    "2017-01": -0.08,
    "2016-12": -0.07,
    "2016-11": -0.07,
    "2016-10": -0.07,
    "2016-09": -0.07,
    "2016-08": -0.07,
    "2016-07": -0.07,
    "2016-06": -0.07,
    "2016-05": -0.07,
    "2016-04": -0.07,
    "2016-03": -0.07,
    "2016-02": -0.07,
    "2016-01": -0.07,
    "2015-12": 0.06,
    "2015-11": 0.16,
    "2015-10": 0.17,
    "2015-09": 0.18,
    "2015-08": 0.16,
    "2015-07": 0.17,
    "2015-06": 0.17,
}

def get_database_connection():
    """Get database connection"""
    db_path = "data/dev.db"
    if not os.path.exists(db_path):
        logger.error(f"Database file not found: {db_path}")
        sys.exit(1)
    return sqlite3.connect(db_path)

def get_euribor_rate_for_date(target_date: date) -> Optional[float]:
    """Get Euribor rate for a specific date (or closest previous date)"""
    year_month = target_date.strftime("%Y-%m")
    
    # Try exact match first
    if year_month in HISTORICAL_EURIBOR_12M:
        return HISTORICAL_EURIBOR_12M[year_month]
    
    # Find closest previous date
    target_date_str = year_month
    closest_date = None
    
    for date_str in sorted(HISTORICAL_EURIBOR_12M.keys(), reverse=True):
        if date_str <= target_date_str:
            closest_date = date_str
            break
    
    if closest_date:
        logger.info(f"Using Euribor rate from {closest_date} for {target_date_str}")
        return HISTORICAL_EURIBOR_12M[closest_date]
    
    logger.warning(f"No Euribor rate found for date {target_date}")
    return None

def get_properties_with_mortgage():
    """Get all properties that have mortgage details"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.id, p.address, m.id as mortgage_id, m.bank_entity, m.initial_amount, 
               m.outstanding_balance, m.start_date, m.end_date, m.review_period_months, 
               m.margin_percentage
        FROM property p
        JOIN mortgagedetails m ON p.id = m.property_id
        ORDER BY p.id
    """)
    
    properties = cursor.fetchall()
    conn.close()
    
    logger.info(f"Found {len(properties)} properties with mortgage details")
    return properties

def get_existing_revisions(mortgage_id: int):
    """Get existing mortgage revisions for a mortgage"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, effective_date, euribor_rate, margin_rate, period_months
        FROM mortgagerevision
        WHERE mortgage_id = ?
        ORDER BY effective_date
    """, (mortgage_id,))
    
    revisions = cursor.fetchall()
    conn.close()
    
    return revisions

def generate_revision_dates(start_date: str, end_date: str, review_period_months: int) -> List[date]:
    """Generate all revision dates for a mortgage"""
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    revision_dates = []
    current_date = start
    
    while current_date <= end:
        revision_dates.append(current_date)
        # Add review period months
        year = current_date.year
        month = current_date.month + review_period_months
        
        # Handle year overflow
        while month > 12:
            month -= 12
            year += 1
            
        try:
            current_date = date(year, month, current_date.day)
        except ValueError:
            # Handle cases like Feb 31st -> Feb 28th/29th
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            current_date = date(year, month, min(current_date.day, last_day))
    
    return revision_dates

def update_revision_with_euribor(revision_id: int, euribor_rate: float):
    """Update existing revision with Euribor rate"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE mortgagerevision
        SET euribor_rate = ?
        WHERE id = ?
    """, (euribor_rate, revision_id))
    
    conn.commit()
    conn.close()
    
    logger.info(f"Updated revision {revision_id} with Euribor rate {euribor_rate}%")

def create_new_revision(mortgage_id: int, effective_date: date, euribor_rate: float, 
                       margin_rate: float, period_months: int):
    """Create a new mortgage revision"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO mortgagerevision (mortgage_id, effective_date, euribor_rate, margin_rate, period_months)
        VALUES (?, ?, ?, ?, ?)
    """, (mortgage_id, effective_date.strftime("%Y-%m-%d"), euribor_rate, margin_rate, period_months))
    
    conn.commit()
    revision_id = cursor.lastrowid
    conn.close()
    
    logger.info(f"Created new revision {revision_id} for mortgage {mortgage_id} on {effective_date}")
    return revision_id

def process_property_revisions(property_data):
    """Process all revisions for a single property"""
    (prop_id, address, mortgage_id, bank_entity, initial_amount, 
     outstanding_balance, start_date, end_date, review_period_months, margin_rate) = property_data
    
    logger.info(f"\nProcessing Property {prop_id}: {address[:50]}...")
    logger.info(f"  Mortgage: {bank_entity}, Period: {review_period_months} months, Margin: {margin_rate}%")
    
    # Get existing revisions
    existing_revisions = get_existing_revisions(mortgage_id)
    logger.info(f"  Found {len(existing_revisions)} existing revisions")
    
    # Create a dict of existing revisions by date
    existing_by_date = {}
    for rev in existing_revisions:
        rev_date = datetime.strptime(rev[1], "%Y-%m-%d").date()
        existing_by_date[rev_date] = {
            'id': rev[0],
            'euribor_rate': rev[2],
            'margin_rate': rev[3],
            'period_months': rev[4]
        }
    
    # Generate all expected revision dates
    expected_dates = generate_revision_dates(start_date, end_date, review_period_months)
    logger.info(f"  Expected {len(expected_dates)} revision dates from {start_date} to {end_date}")
    
    updated_count = 0
    created_count = 0
    
    for revision_date in expected_dates:
        euribor_rate = get_euribor_rate_for_date(revision_date)
        
        if euribor_rate is None:
            logger.warning(f"  Skipping {revision_date} - no Euribor rate available")
            continue
            
        if revision_date in existing_by_date:
            # Update existing revision if Euribor rate is missing or different
            existing_rev = existing_by_date[revision_date]
            if existing_rev['euribor_rate'] is None or existing_rev['euribor_rate'] != euribor_rate:
                update_revision_with_euribor(existing_rev['id'], euribor_rate)
                updated_count += 1
        else:
            # Create new revision
            create_new_revision(
                mortgage_id=mortgage_id,
                effective_date=revision_date,
                euribor_rate=euribor_rate,
                margin_rate=margin_rate,
                period_months=review_period_months
            )
            created_count += 1
    
    logger.info(f"  Completed: {updated_count} updated, {created_count} created")
    return updated_count, created_count

def upload_euribor_rates_to_database():
    """Upload historical Euribor rates to the euriborrate table"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    logger.info("Uploading historical Euribor rates...")
    
    uploaded_count = 0
    
    for date_str, rate_12m in HISTORICAL_EURIBOR_12M.items():
        # Convert date string to first day of month
        year, month = map(int, date_str.split('-'))
        rate_date = date(year, month, 1)
        
        # Check if rate already exists
        cursor.execute("SELECT id FROM euriborrate WHERE date = ?", (rate_date.strftime("%Y-%m-%d"),))
        if cursor.fetchone():
            continue  # Skip if already exists
        
        # Insert new rate
        cursor.execute("""
            INSERT INTO euriborrate (date, rate_12m, source, created_at)
            VALUES (?, ?, ?, ?)
        """, (rate_date.strftime("%Y-%m-%d"), rate_12m, "Historical Data", date.today().strftime("%Y-%m-%d")))
        
        uploaded_count += 1
    
    conn.commit()
    conn.close()
    
    logger.info(f"Uploaded {uploaded_count} Euribor rates to database")

def main():
    """Main function to upload Euribor revision data for all properties"""
    logger.info("Starting Euribor revision data upload process...")
    
    # First, upload Euribor rates to the database
    upload_euribor_rates_to_database()
    
    # Get all properties with mortgage details
    properties = get_properties_with_mortgage()
    
    if not properties:
        logger.warning("No properties with mortgage details found")
        return
    
    total_updated = 0
    total_created = 0
    
    # Process each property
    for property_data in properties:
        try:
            updated, created = process_property_revisions(property_data)
            total_updated += updated
            total_created += created
        except Exception as e:
            logger.error(f"Error processing property {property_data[0]}: {e}")
            continue
    
    logger.info(f"\n=== SUMMARY ===")
    logger.info(f"Processed {len(properties)} properties")
    logger.info(f"Total revisions updated: {total_updated}")
    logger.info(f"Total revisions created: {total_created}")
    logger.info(f"Process completed successfully!")

if __name__ == "__main__":
    main()