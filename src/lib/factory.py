#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import logging
from typing import List, Iterable

from lib.model import Provider


class LoggerFactory:
    @staticmethod
    def get(debug: bool) -> logging.Logger:
        logger = logging.getLogger()
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG if debug else logging.INFO)

        return logger


class DateFactory:
    @staticmethod
    def list_of_dates(lst: Iterable[str]) -> List[datetime.date]:
        return [datetime.datetime.strptime(d, "%Y-%m-%d") for d in lst]


class KeyFactory:
    @staticmethod
    def for_state(provider: Provider, date: str):
        return f"{provider.value}-{date}"
