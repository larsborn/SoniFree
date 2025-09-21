#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import logging
from typing import Dict

from lib.factory import DateFactory
from lib.model import DataPoint, Provider


class Validator:
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def validate(self, by_date: Dict[str, Dict[Provider, DataPoint]]):
        dates = DateFactory.list_of_dates(by_date.keys())
        current = min(dates)
        while current < max(dates):
            current += datetime.timedelta(days=1)
            if current.strftime("%Y-%m-%d") not in by_date.keys():
                self._logger.warning(f"Date {current} missing.")

        self._logger.info(
            f"Validated {len(by_date)} rows ({int((max(dates) - min(dates)).total_seconds() / 60 / 60 / 24)} day(s))."
        )

        for date, by_provider in by_date.items():
            for data_point in by_provider.values():
                if data_point.provider is None:
                    raise ValueError(f"Expected provider to be set on {data_point}")
                if not isinstance(data_point.provider, Provider):
                    raise ValueError(f"Expected provider to be an enum on {data_point}")
