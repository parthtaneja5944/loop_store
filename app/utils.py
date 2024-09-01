from datetime import datetime, timedelta,time
from datetime import timezone as tmz
import pytz
from sqlalchemy import and_, asc, func, select, cast, Time
from .models import StoreStatus, BusinessHours, Timezone, ReportStatus
from .extensions import db
import pandas as pd
from collections import defaultdict
from multiprocessing import Pool

def default_business_hours():
    return defaultdict(list)

def get_business_hours():
    business_hours = db.session.execute(select(BusinessHours)).scalars().all()
    business_hours_dict = defaultdict(default_business_hours)
    for hours in business_hours:
        business_hours_dict[hours.store_id][hours.day].append((hours.start_time_local, hours.end_time_local))

    return business_hours_dict

def get_timezone():
    timezone = db.session.execute(select(Timezone)).scalars().all()
    timezone_dict = {}
    for time in timezone:
        timezone_dict[time.store_id] = time.timezone_str
    return timezone_dict

def convert_to_store_timezone(timestamp_utc,timezone):
    store_timezone = pytz.timezone(timezone)
    local_timestamp = timestamp_utc.astimezone(store_timezone)
    return local_timestamp

def calculate_uptime_downtime(store_id,store_data,business_hours,latest_timestamp,start_timestamp,timezone):
    uptime = timedelta()
    downtime = timedelta()
    filtered_store_data = store_data[(store_data['timestamp_utc'] >= start_timestamp) &
                               (store_data['timestamp_utc'] <= latest_timestamp)].copy()
    filtered_store_data.sort_values(by='timestamp_utc', ascending=True, inplace=True)

    start_timestamp = convert_to_store_timezone(start_timestamp,timezone)
    latest_timestamp = convert_to_store_timezone(latest_timestamp,timezone)
    previous_timestamp = start_timestamp


    for _,record in filtered_store_data.iterrows():
        current_timestamp = record['timestamp_utc']
        current_time = convert_to_store_timezone(current_timestamp,timezone)
        current_day = current_time.weekday()
        current_time = current_time.time()
        is_within_business_hours = False
        if current_day in business_hours:
            for start_time,end_time in business_hours[current_day]:
                if start_time <= current_time <=end_time:
                    is_within_business_hours = True
                    break 
        if is_within_business_hours: #or record['status'] == 'active'
            interval = current_timestamp - previous_timestamp                
            if record['status'] == 'active':
                uptime+=interval
            else:
                downtime+=interval

        previous_timestamp = current_timestamp

    final_interval = latest_timestamp - previous_timestamp
    if filtered_store_data.iloc[-1]['status'] == 'active':
        uptime += final_interval
    else:
        downtime += final_interval

    return uptime.total_seconds() / 60, downtime.total_seconds() / 60     


def process_store(store_id,store_data_df,all_store_business_hours,all_store_timezone):

    store_data = store_data_df[store_data_df['store_id'] == store_id]
    if store_data.empty:
        return None
    
    timezone = all_store_timezone.get(store_id, 'America/Chicago')
    business_hours = all_store_business_hours.get(store_id, {
    0: [(time(0, 0), time(23, 59))],
    1: [(time(0, 0), time(23, 59))],
    2: [(time(0, 0), time(23, 59))],
    3: [(time(0, 0), time(23, 59))],
    4: [(time(0, 0), time(23, 59))],
    5: [(time(0, 0), time(23, 59))],
    6: [(time(0, 0), time(23, 59))]
    })
     
    latest_timestamp = store_data['timestamp_utc'].max()
    lasthour_start_timestamp = latest_timestamp - timedelta(hours=1)
    lastday_start_timestamp = latest_timestamp - timedelta(days=1)
    lastweek_start_timestamp = latest_timestamp - timedelta(weeks=1)
    uptime_last_hour, downtime_last_hour = calculate_uptime_downtime(store_id,store_data, business_hours, latest_timestamp, lasthour_start_timestamp,timezone)
    uptime_last_day, downtime_last_day = calculate_uptime_downtime(store_id,store_data, business_hours, latest_timestamp, lastday_start_timestamp,timezone)
    uptime_last_week, downtime_last_week = calculate_uptime_downtime(store_id,store_data, business_hours, latest_timestamp, lastweek_start_timestamp,timezone)
    uptime_last_day = round(uptime_last_day / 60, 2)
    downtime_last_day = round(downtime_last_day / 60, 2)
    uptime_last_week = round(uptime_last_week / 60, 2)
    downtime_last_week = round(downtime_last_week / 60, 2)
    return {
        'store_id': store_id,
        'uptime_last_hour': uptime_last_hour,
        'downtime_last_hour': downtime_last_hour,
        'uptime_last_day': uptime_last_day,
        'downtime_last_day': downtime_last_day,
        'uptime_last_week': uptime_last_week,
        'downtime_last_week': downtime_last_week
    } 

def generate_report(report_id):
    report = ReportStatus.query.filter_by(report_id=report_id).first()
    try:
        store_ids = [store[0] for store in db.session.query(StoreStatus.store_id).distinct().limit(1).all()]

        store_data = db.session.query(
            StoreStatus.store_id,
            StoreStatus.timestamp_utc,
            StoreStatus.status,
        ).order_by(StoreStatus.timestamp_utc.asc()).all()

        store_data_df = pd.DataFrame(store_data, columns=['store_id', 'timestamp_utc', 'status'])
        
        business_hours = get_business_hours()
        timezone = get_timezone()
        with Pool(processes=4) as pool:
            reports = pool.starmap(process_store, [(store_id, store_data_df,business_hours,timezone) for store_id in store_ids])
        #old method
        # reports = []
        # for store_id in store_ids:
        #     result = process_store(store_id, store_data_df, business_hours, timezone)
        #     if result:
        #         reports.append(result)
        
        df = pd.DataFrame(reports)
        df.to_csv(f'app/reports/{report_id}.csv', index=False)
        report.status = "Complete"
        report.generated_at = datetime.now(pytz.utc)
        db.session.commit()        


    except Exception as e:
        report.status = "Failed"
        db.session.commit()
        raise e
