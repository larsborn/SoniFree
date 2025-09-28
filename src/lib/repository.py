#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import abc
from typing import Dict, Optional, List, Iterator

from lib.model import Provider, DataPointStrDict, DataPoint


class AbstractRepository(abc.ABC):
    def __init__(self, data: Dict[Provider, DataPointStrDict]):
        self._data = data

    def providers(self) -> List[Provider]:
        return list(set(self._data.keys()))

    def get_dates(self) -> List[str]:
        ret = set()
        for provider, by_date in self._data.items():
            ret.update(by_date.keys())
        return sorted(list(ret))

    def sum_by_provider(self, provider: Provider):
        dates = self.get_dates()
        if len(dates) == 0:
            return 0
        for date in sorted(dates, reverse=True):
            try:
                latest_data_point = self._data[provider][date]
            except KeyError:
                continue
            if self.extract_number(latest_data_point) is not None:
                return self.extract_number(latest_data_point)

        return 0

    def sum(self):
        ret = 0
        for provider in Provider:
            ret += self.sum_by_provider(provider)
        return ret

    def find_by_provider(self, provider: Provider) -> Iterator[Optional[int]]:
        dates = self.get_dates()
        prev = 0
        for date in sorted(dates):
            try:
                prev = self.extract_number(self._data[provider][date])
            except KeyError:
                pass
            yield prev

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
