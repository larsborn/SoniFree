#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import abc
from typing import Dict, Callable

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
        raise NotImplementedError

    def sum(self):
        ret = 0
        for provider in Provider:
            ret += self.sum_by(provider)
        return ret


class FollowerRepository(AbstractRepository):
    def sum_by(self, provider: Provider):
        def acc(p: DataPoint):
            return p.follower_count

        return self.sum_field_by(provider, acc)


class ListenerRepository(AbstractRepository):
    def sum_by(self, provider: Provider):
        def acc(p: DataPoint):
            return p.listener_count

        return self.sum_field_by(provider, acc)


class ConsumptionRepository(AbstractRepository):
    def sum_by(self, provider: Provider):
        def acc(p: DataPoint):
            return p.consumption_seconds

        return self.sum_field_by(provider, acc)


class StreamRepository(AbstractRepository):
    def sum_by(self, provider: Provider):
        def acc(p: DataPoint):
            return p.stream_count

        return self.sum_field_by(provider, acc)
