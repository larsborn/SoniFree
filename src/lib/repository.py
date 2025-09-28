#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import abc
from typing import Dict, Callable, Optional

from lib.model import Provider, DataPointStrDict, DataPoint


class AbstractRepository(abc.ABC):
    def __init__(self, data: Dict[Provider, DataPointStrDict]):
        self._data = data

    def sum_field_by(self, provider: Provider, accessor: Callable[[DataPoint], int]):
        dates = self._data[provider].keys()
        if len(dates) == 0:
            return 0
        for date in sorted(dates, reverse=True):
            latest_data_point = self._data[provider][date]
            if accessor(latest_data_point) > 0:
                return accessor(latest_data_point)

        return 0

    def sum_by(self, provider: Provider):
        return self.sum_field_by(provider, self.extract_number)

    def sum(self):
        ret = 0
        for provider in Provider:
            ret += self.sum_by(provider)
        return ret

    def extract_number(self, dp: DataPoint) -> Optional[int]:
        raise NotImplementedError


class FollowerRepository(AbstractRepository):
    def extract_number(self, dp: DataPoint) -> Optional[int]:
        return dp.follower_count


class ListenerRepository(AbstractRepository):
    def extract_number(self, dp: DataPoint) -> Optional[int]:
        return dp.listener_count


class ConsumptionRepository(AbstractRepository):
    def extract_number(self, dp: DataPoint) -> Optional[int]:
        return dp.consumption_seconds


class StreamRepository(AbstractRepository):
    def extract_number(self, dp: DataPoint) -> Optional[int]:
        return dp.stream_count


class StreamStartRepository(AbstractRepository):
    def extract_number(self, dp: DataPoint) -> Optional[int]:
        return dp.stream_start_count
