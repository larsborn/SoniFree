#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from collections import defaultdict
from typing import Iterable, Dict

from lib.model import Response, DataPoint, Provider, DataPointStrDict
from normalizer.amazon import Amazon
from normalizer.spotify import Spotify


class Transformer:
    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._state = {}
        self._strategies = [
            Spotify(self._logger),
            Amazon(self._logger),
        ]

    def normalize(self, responses: Iterable[Response]) -> Dict[Provider, DataPointStrDict]:
        by_provider = defaultdict(lambda: defaultdict(DataPoint))
        for response in responses:
            for strategy in self._strategies:
                if strategy.should_apply(response.meta):
                    strategy.normalize(by_provider[strategy.provider()], response)
                    break
            else:
                raise ValueError(f"Cannot route response: {response}")

        for provider in by_provider.keys():
            if provider in [Provider.SPOTIFY, Provider.AMAZON]:
                by_provider[provider] = self._normalize_to_cumulative(by_provider[provider])
            by_provider[provider] = self._populate_provider(provider, by_provider[provider])
            by_provider[provider] = self._filter_all_none(by_provider[provider])

        for empty_key in [k for k, v in by_provider.items() if len(v) == 0]:
            del by_provider[empty_key]

        return by_provider

    @staticmethod
    def _normalize_to_cumulative(by_date: DataPointStrDict) -> DataPointStrDict:
        if len(by_date) == 0:
            return {}

        cumulative_data_point = DataPoint(next(iter(by_date.values())).provider, 0, 0, 0, 0, 0, 0)
        ret = {}
        for k, v in by_date.items():
            if v.no_data_set:
                continue
            cumulative_data_point.follower_count = v.follower_count or 0
            cumulative_data_point.listener_count += v.listener_count or 0
            cumulative_data_point.consumption_seconds += v.consumption_seconds or 0
            cumulative_data_point.foreground_consumption_seconds += v.foreground_consumption_seconds or 0
            cumulative_data_point.stream_count += v.stream_count or 0
            cumulative_data_point.stream_start_count += v.stream_start_count or 0
            ret[k] = cumulative_data_point.duplicate()

        return ret

    @staticmethod
    def provider_to_date_flip(
        by_provider: Dict[Provider, DataPointStrDict],
    ) -> Dict[str, Dict[Provider, DataPoint]]:
        ret = {}
        dates = set()
        for provider, by_date in by_provider.items():
            dates.update(by_date.keys())
        dates = sorted(list(dates))

        for provider, by_date in by_provider.items():
            for date in dates:
                if date not in ret:
                    ret[date] = {}
                point = by_date.get(date, DataPoint(provider=provider))
                ret[date][provider] = point

        return ret

    @staticmethod
    def date_to_provider_flip(
        by_date: Dict[str, Dict[Provider, DataPoint]],
    ) -> Dict[Provider, DataPointStrDict]:
        ret = {}
        for date, by_provider in by_date.items():
            for provider, point in by_provider.items():
                if provider not in ret:
                    ret[provider] = {}
                ret[provider][date] = point

        return ret

    @staticmethod
    def _filter_all_none(by_date: DataPointStrDict) -> DataPointStrDict:
        ret = dict()
        for key, val in by_date.items():
            if val.no_data_set:
                continue
            ret[key] = val

        return ret

    @staticmethod
    def _populate_provider(provider: Provider, by_date: DataPointStrDict) -> DataPointStrDict:
        for val in by_date.values():
            if val.provider is None:
                val.provider = provider
            elif val.provider != provider:
                raise ValueError(
                    f"Previously populated provider {val.provider:r} not equal to {provider:r}: {val}"
                )
        return by_date
