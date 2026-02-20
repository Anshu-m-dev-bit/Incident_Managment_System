from flask import Flask, render_template, request, redirect, url_for, flash
from db_operations import (
    create_incident,
    list_incidents,
    get_incident_by_id,
    update_status,
    update_description,
    update_severity,
    delete_incident
)

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for flash messages


# -------------------------
# HOME
# -------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        operation = request.form.get('operation')

        if operation == 'create':
            return redirect(url_for('create_page'))

        elif operation in ['view', 'update', 'delete']:
            return redirect(url_for('search', operation=operation))

        else:
            return "Invalid Option", 400

    return render_template('index.html')


# -------------------------
# CREATE
# -------------------------
@app.route('/create', methods=['GET', 'POST'])
def create_page():
    if request.method == 'POST':
        service = request.form.get('service')
        severity = request.form.get('severity')
        description = request.form.get('description')
        status = request.form.get('status')

        try:
            create_incident(service, severity, description, status)
            flash("Incident created successfully.")
            return redirect(url_for('index'))

        except Exception as e:
            return f"Error creating incident: {str(e)}", 500

    return render_template('create.html')


# -------------------------
# SEARCH (for view/update/delete)
# -------------------------
@app.route('/search/<operation>', methods=['GET', 'POST'])
def search(operation):

    if operation not in ['view', 'update', 'delete']:
        return "Invalid operation", 400

    if request.method == 'POST':
        iid = request.form.get('iid')
        return redirect(url_for(operation, iid=iid))

    return render_template('search.html', operation=operation)


# -------------------------
# VIEW
# -------------------------
@app.route('/view/<iid>')
def view(iid):

    incident = get_incident_by_id(iid)

    if not incident:
        return "Incident not found", 404

    return render_template('view.html', incident=incident)


# -------------------------
# UPDATE
# -------------------------
@app.route('/update/<iid>', methods=['GET', 'POST'])
def update(iid):

    incident = get_incident_by_id(iid)

    if not incident:
        return "Incident not found", 404

    if request.method == 'POST':
        field = request.form.get('field')
        value = request.form.get('value')

        if field == 'status':
            ok, msg = update_status(iid, value)
            if not ok:
                return f"Update Failed: {msg}"

        elif field == 'description':
            success = update_description(iid, value)
            if not success:
                return "Update Failed"

        elif field == 'severity':
            success = update_severity(iid, value)
            if not success:
                return "Update Failed"

        else:
            return "Invalid field", 400

        flash("Incident updated successfully.")
        return redirect(url_for('index'))

    return render_template('update.html', incident=incident)


# -------------------------
# DELETE
# -------------------------
@app.route('/delete/<iid>', methods=['GET', 'POST'])
def delete(iid):

    incident = get_incident_by_id(iid)

    if not incident:
        return "Incident not found", 404

    if request.method == 'POST':
        ok, msg = delete_incident(iid)

        if not ok:
            return f"Delete Failed: {msg}"

        flash("Incident deleted successfully.")
        return redirect(url_for('index'))

    return render_template('delete.html', incident=incident)


# -------------------------
# OPTIONAL: LIST ALL INCIDENTS
# -------------------------
@app.route('/list')
def list_all():
    incidents = list_incidents()
    return render_template('list.html', incidents=incidents)


# -------------------------
# RUN APP
# -------------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
