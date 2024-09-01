from flask import Blueprint, jsonify, send_file, request,current_app
from app.utils import generate_report
from .extensions import db
import uuid
import threading
from .models import ReportStatus
main = Blueprint('main', __name__)

@main.route('/', methods=['GET','POST'])
def get_rep():
    return "Enter correct route to get report"


@main.route('/trigger_report', methods=['POST'])
def trigger_report():
    report_id = str(uuid.uuid4())
    new_report = ReportStatus(report_id=report_id, status="Running")
    db.session.add(new_report)
    db.session.commit()

    app = current_app._get_current_object()
    thread = threading.Thread(target=generate_report_with_context, args=(report_id, app))
    thread.start()

    return jsonify({'report_id': report_id})

def generate_report_with_context(report_id, app):
    with app.app_context():
        generate_report(report_id)


@main.route('/get_report', methods=['GET'])
def get_report():
    report_id = request.args.get('report_id')
    report = ReportStatus.query.filter_by(report_id=report_id).first()

    if not report:
        return jsonify({'error': 'Invalid report_id'}), 400

    if report.status == "Running":
        return jsonify({'status': 'Running'})
    
    if report.status == "Failed":
        return jsonify({'status': 'Failed', 'error': 'An error occurred during report generation'}), 500
    
    if report.status == "Complete":
        return send_file(f"reports/{report_id}.csv", as_attachment=True)
    