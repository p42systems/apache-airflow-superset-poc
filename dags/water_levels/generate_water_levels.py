import csv
import logging

from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from mimesis import Field, Fieldset, Schema, Datetime
from mimesis.locales import Locale

from airflow.decorators import dag, task

logger = logging.getLogger(__name__)

field = Field(locale=Locale.EN)
fieldset = Fieldset(locale=Locale.EN)

schema = Schema(
    schema=lambda: {
        "measurements": {
            "site_1": field("decimal_number", start=10.0, end=-10.0),
            "site_2": field("decimal_number", start=10.0, end=-10.0),
            "site_3": field("decimal_number", start=10.0, end=-10.0),
            "site_4": field("decimal_number", start=10.0, end=-10.0),
        },
    },
    iterations=24,
)

START_DATE = datetime(2023, 11, 1, 0, 0)

@dag(
    dag_id="import_water_level_data",
    start_date=START_DATE,
    schedule="0 0 * * *",
    default_args={
        "depends_on_past": False,
    }
)
def generate_water_levels_dataset():

    @task(multiple_outputs=True)
    def generate_water_levels(**kwargs):
        date = kwargs.get("logical_date", None)
        assert isinstance(date, datetime), "`date` is not a `datetime` object. `logical_date` not found in `kwargs`."
        logger.info(f"The data logging date is: {date.strftime('%Y-%m-%d %H:%M:%S')}")
        date = date - timedelta(
            hours=date.hour,
            minutes=date.minute,
            seconds=date.second,
            microseconds=date.microsecond,
        )
        logger.info(f"Set the date to mid-night: {date.strftime('%Y-%m-%d %H:%M:%S')}")

        beginning_of_day = date - timedelta(hours=1)
        end_of_day = beginning_of_day + timedelta(hours=23)
        hours = Datetime.bulk_create_datetimes(beginning_of_day, end_of_day, hours=1)

        return { "date": date, "water_level_data": [ { "date": h, **v } for h, v in zip(hours, schema.create())] }

    @task
    def create_csv_file(date: datetime, water_level_data: List):
        csv_file = Path(f"/opt/airflow/datasets/{date.strftime('%Y-%m-%d')}.csv")
        if csv_file.exists():
            logger.warn(f"File [{csv_file}] already exists. Exiting.")
            return

        with open(csv_file, "w+") as fp:
            writer = csv.DictWriter(fp, ["date", "hour", "site_1", "site_2", "site_3", "site_4"])
            writer.writeheader()
            for data in water_level_data:
                logger.info(f"row data: {data}")
                writer.writerow({
                    "date": data["date"].strftime("%Y-%m-%d"),
                    "hour": data["date"].hour,
                    "site_1": data["measurements"]["site_1"],
                    "site_2": data["measurements"]["site_2"],
                    "site_3": data["measurements"]["site_3"],
                    "site_4": data["measurements"]["site_4"],
                })

    data = generate_water_levels()
    create_csv_file(data["date"], data["water_level_data"])

generate_water_levels_dataset()
