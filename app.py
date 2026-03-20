from flask import Flask, render_template, request, redirect, url_for, flash, Response
from db_operations import (
    create_incident,
    list_incidents,
    get_incident_by_id,
    update_incident,
    delete_incident,
    get_total_count,
    get_active_sev1_count,
    get_severity_stats,
    get_status_stats,
    get_recent_incidents,
    get_open_closed_stats,
    get_incident_trend,
    regenerate_ai_analysis
)
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for flash messages

# Example metric
REQUEST_COUNT = Counter('app_requests_total', 'Total number of requests')


@app.before_request
def before_request():
    REQUEST_COUNT.inc()

@app.route('/metrics', methods=['GET', 'POST'])
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)



# -------------------------
# HOME
# -------------------------
@app.route('/')
def dashboard():

    total = get_total_count()
    active_sev1 = get_active_sev1_count()
    severity_stats = get_severity_stats()
    status_stats = get_status_stats()
    recents = get_recent_incidents()
    open_closed = get_open_closed_stats()
    trend = get_incident_trend()

    return render_template(
        'dashboard.html',
        total=total,
        active_sev1=active_sev1,
        severity_stats=severity_stats,
        open_closed=open_closed,
        trend=trend,
        recents=recents
    )
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

        if not all([service, severity, description, status]):
            flash("All fields are required")
            return redirect(url_for('create_page'))
        try:
            create_incident(service, severity, description, status)
            flash("Incident created successfully.")
            return redirect(url_for('dashboard'))

        except Exception as e:
            return f"Error creating incident: {str(e)}", 500


    # -------- Get current incident data --------
    incidents = list_incidents()

    sev_counts = {
        "SEV1": 0,
        "SEV2": 0,
        "SEV3": 0
    }

    stat_counts = {
        "Open": 0,
        "Investigating": 0,
        "Mitigated": 0,
        "Resolved": 0
    }

    for inc in incidents:
        sev_counts[inc["severity"]] += 1
        stat_counts[inc["status"]] += 1


    return render_template(
        'create.html',
        sev_counts=sev_counts,
        stat_counts=stat_counts
    )



# -------------------------
# SEARCH (for view/update/delete)
# -------------------------
@app.route('/search')
def search():

    # Get incidents using your db_operations function
    incidents = list_incidents()

    sev_counts = {
        "SEV1": 0,
        "SEV2": 0,
        "SEV3": 0
    }

    stat_counts = {
        "Open": 0,
        "Investigating": 0,
        "Mitigated": 0,
        "Resolved": 0
    }

    for inc in incidents:
        sev_counts[inc["severity"]] += 1
        stat_counts[inc["status"]] += 1

    return render_template(
        "search.html",
        sev_counts=sev_counts,
        stat_counts=stat_counts
    )

# -------------------------
# VIEW
# -------------------------
# View all incidents
@app.route('/view')
def view_all():

    incidents = list_incidents()

    return render_template('view.html', incidents=incidents)


# View single incident
@app.route('/view/<iid>')
def view_incident(iid):

    incident = get_incident_by_id(iid)

    if not incident:
        return "Incident not found", 404

    return render_template('view_incident.html', incident=incident)


# -------------------------
# UPDATE
# -------------------------
@app.route('/update/<iid>', methods=['GET','POST'])
def update_page(iid):

    if request.method == 'POST':

        service = request.form.get('service')
        severity = request.form.get('severity')
        description = request.form.get('description')
        status = request.form.get('status')

        update_incident(iid, service, severity, description, status)

        flash("Incident updated successfully")

        return redirect(url_for('view_incident', iid=iid))

    incident = get_incident_by_id(iid)

    return render_template("update.html", incident=incident)


# -------------------------
# DELETE
# -------------------------
@app.route('/delete/<iid>')
def delete(iid):

    delete_incident(iid)

    flash("Incident deleted successfully")

    return redirect(url_for('view_all'))


@app.route('/regenerate_ai/<iid>', methods=['POST'])
def regenerate_ai(iid):

    success, result = regenerate_ai_analysis(iid)

    if success:
        flash("AI analysis regenerated successfully")
    else:
        flash(f"Error: {result}")

    return redirect(url_for('update_page', iid=iid))


# -------------------------
# OPTIONAL: LIST ALL INCIDENTS
# -------------------------
@app.route('/list')
def list_all():
    incidents = list_incidents()
    return render_template('list.html', incidents=incidents)


@app.route('/incidents')
def list_incidents_route():
    incidents = list_incidents()
    return render_template('list.html', incidents=incidents)


# -------------------------
# RUN APP
# -------------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)