from .extensions import db

class StoreStatus(db.Model):
    __tablename__ = 'store_status'
    id = db.Column(db.Integer,primary_key=True)
    store_id = db.Column(db.String(50), nullable=False)
    timestamp_utc = db.Column(db.DateTime(timezone=True), nullable=False)
    status = db.Column(db.String(10),nullable = False)


class BusinessHours(db.Model):
    __tablename__ = 'business_hours'
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.String(50), nullable=False)
    day = db.Column(db.Integer, nullable=False)
    start_time_local = db.Column(db.Time, nullable=False)
    end_time_local = db.Column(db.Time, nullable=False)

class Timezone(db.Model):
    __tablename__ = 'timezone'
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.String(50), nullable=False)
    timezone_str = db.Column(db.String(50), nullable=False)    


class ReportStatus(db.Model):
    __tablename__ = 'report_status'
    report_id = db.Column(db.String(36), primary_key=True)
    status = db.Column(db.String(20), nullable=False)
    generated_at = db.Column(db.DateTime, nullable=True)