from config import get_db_connection
from datetime import datetime
from ai_helper import get_ai_analysis


ALLOWED_STATUSES = ["Open", "Investigating", "Mitigated", "Resolved"]
ALLOWED_SEVERITIES = ["SEV1", "SEV2", "SEV3"]


# -------------------------
# ID GENERATION (INC-001)
# -------------------------
def _generate_incident_code(cursor):
    cursor.execute(
        "SELECT incident_code FROM incidents_p ORDER BY id DESC LIMIT 1"
    )
    result = cursor.fetchone()

    if result:
        last_code = result[0]
        last_number = int(last_code.split("-")[1])
        next_number = last_number + 1
    else:
        next_number = 1

    return f"INC-{next_number:03d}"


# -------------------------
# CREATE
# -------------------------
def create_incident(service, severity, description, status):

    if status not in ALLOWED_STATUSES:
        raise ValueError(
            f"Status must be one of: {', '.join(ALLOWED_STATUSES)}"
        )

    if severity not in ALLOWED_SEVERITIES:
        raise ValueError(
            f"Severity must be one of: {', '.join(ALLOWED_SEVERITIES)}"
        )

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        incident_code = _generate_incident_code(cursor)

        ai_response = get_ai_analysis(
            service=service,
            error=description,
            logs=description,
            impact="Not specified",
            severity=severity
        )

        query = """
            INSERT INTO incidents_p
            (incident_code, service, severity, description, status, created_at, ai_analysis)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            incident_code,
            service,
            severity,
            description,
            status,
            datetime.now(),
            ai_response
        )

        cursor.execute(query, values)
        conn.commit()

        return {
            "id": incident_code,
            "service": service,
            "severity": severity,
            "description": description,
            "status": status,
            "created_at": datetime.now().isoformat()
        }

    except Exception as e:
        if conn:
            conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# -------------------------
# READ - LIST
# -------------------------
def list_incidents(status=None, severity=None):

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT incident_code AS id,
                   service,
                   severity,
                   description,
                   status,
                   created_at,
                   ai_analysis
            FROM incidents_p
            WHERE 1=1
        """

        params = []

        if status:
            query += " AND status = %s"
            params.append(status)

        if severity:
            query += " AND severity = %s"
            params.append(severity)

        cursor.execute(query, params)
        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# -------------------------
# READ - SINGLE
# -------------------------
def get_incident_by_id(incident_id):

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT incident_code AS id,
                service,
                severity,
                description,
                status,
                created_at,
                ai_analysis  
            FROM incidents_p
            WHERE incident_code = %s
        """

        cursor.execute(query, (incident_id,))
        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# -------------------------
# UPDATE
# -------------------------
def update_incident(incident_id, service, severity, description, status):

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            UPDATE incidents_p
            SET service = %s,
                severity = %s,
                description = %s,
                status = %s
            WHERE incident_code = %s
        """

        cursor.execute(query, (service, severity, description, status, incident_id))
        conn.commit()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# -------------------------
# UPDATE STATUS
# -------------------------
def update_status(incident_id, new_status):

    if new_status not in ALLOWED_STATUSES:
        return False, f"Status must be one of: {', '.join(ALLOWED_STATUSES)}"

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE incidents_p SET status = %s WHERE incident_code = %s",
            (new_status, incident_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return False, "Not found"

        return True, "Updated"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# -------------------------
# UPDATE DESCRIPTION
# -------------------------
def update_description(incident_id, new_description):

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE incidents_p SET description = %s WHERE incident_code = %s",
            (new_description, incident_id)
        )
        conn.commit()

        return cursor.rowcount > 0

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# -------------------------
# UPDATE SEVERITY
# -------------------------
def update_severity(incident_id, new_severity):

    if new_severity not in ALLOWED_SEVERITIES:
        return False

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE incidents_p SET severity = %s WHERE incident_code = %s",
            (new_severity, incident_id)
        )
        conn.commit()

        return cursor.rowcount > 0

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# -------------------------
# DELETE
# -------------------------
def delete_incident(incident_id):

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            DELETE FROM incidents_p
            WHERE incident_code = %s
        """

        cursor.execute(query, (incident_id,))
        conn.commit()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# -------------------------
# DASHBOARD FUNCTIONS
# -------------------------

def get_total_count():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM incidents_p")
    result = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return result


def get_active_sev1_count():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM incidents_p
        WHERE severity='SEV1' AND status!='Resolved'
    """)

    result = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return result


def get_severity_stats():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT severity, COUNT(*) as count
        FROM incidents_p
        GROUP BY severity
    """)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result


def get_status_stats():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM incidents_p
        GROUP BY status
    """)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result


def get_recent_incidents(limit=5):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT incident_code AS id,
               service,
               severity,
               description,
               status,
               created_at
        FROM incidents_p
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result


def get_open_closed_stats():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            SUM(CASE WHEN status='Open' THEN 1 ELSE 0 END),
            SUM(CASE WHEN status='Resolved' THEN 1 ELSE 0 END)
        FROM incidents_p
    """)

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        "Open": result[0] or 0,
        "Closed": result[1] or 0
    }


def get_incident_trend():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM incidents_p
        GROUP BY DATE(created_at)
        ORDER BY DATE(created_at)
    """)

    results = cursor.fetchall()

    for row in results:
        row['date'] = row['date'].strftime('%Y-%m-%d')

    cursor.close()
    conn.close()

    return results

def regenerate_ai_analysis(incident_id):

    conn = None
    cursor = None

    try:
        # -------- STEP 1: Get incident data --------
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT service, description, severity
            FROM incidents_p
            WHERE incident_code = %s
        """, (incident_id,))

        incident = cursor.fetchone()

        if not incident:
            return False, "Incident not found"

        # ✅ Close DB BEFORE AI call (very important)
        cursor.close()
        conn.close()

        # -------- STEP 2: Call AI (no DB lock) --------
        new_ai = get_ai_analysis(
            service=incident["service"],
            error=incident["description"],
            logs=incident["description"],
            impact="Not specified",
            severity=incident["severity"]
        )

        # -------- STEP 3: Update DB --------
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE incidents_p
            SET ai_analysis = %s
            WHERE incident_code = %s
        """, (new_ai, incident_id))

        conn.commit()

        return True, new_ai   # return AI also (useful)

    except Exception as e:
        if conn:
            conn.rollback()
        return False, str(e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()