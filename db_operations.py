from config import get_db_connection
from datetime import datetime


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

        query = """
            INSERT INTO incidents_p
            (incident_code, service, severity, description, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            incident_code,
            service,
            severity,
            description,
            status,
            datetime.now()
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
                   created_at
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
                   created_at
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
        cursor = conn.cursor(dictionary=True)

        # Check if exists
        cursor.execute(
            "SELECT status FROM incidents_p WHERE incident_code = %s",
            (incident_id,)
        )
        result = cursor.fetchone()

        if not result:
            return False, "Not found"

        if result["status"] != "Resolved":
            return False, "Can only delete incidents with status 'Resolved'"

        # Delete
        cursor.execute(
            "DELETE FROM incidents_p WHERE incident_code = %s",
            (incident_id,)
        )
        conn.commit()

        return True, "Deleted"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
