#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from typing import Dict

from lib.model import DataPoint, Response, Provider, ResponseMeta
from normalizer.base import BaseNormalizationStrategy, NoneComparator


class Amazon(BaseNormalizationStrategy):
    def should_apply(self, meta: ResponseMeta):
        return "amazon" in meta.url

    def provider(self) -> Provider:
        return Provider.AMAZON

    def normalize(self, by_date: Dict[str, DataPoint], response: Response) -> None:
        """
        rows look like this:

            {"time": "2025-07-30T00:00:00.000Z", "value": 3.0}
        """
        data = json.loads(response.data.decode("utf-8"))["data"]

        # the total or aggregate counts are not useful, the scraper needs to be extended to cover series as well
        if "followsAggregate" in data:
            pass
        if "followsTotals" in data:
            pass
        if "listenersAggregate" in data:
            pass
        if "listenersTotals" in data:
            pass
        if "playsAggregate" in data:
            pass
        if "playsTotals" in data:
            pass
        if "startsAggregate" in data:
            pass
        if "playsTimeSeries" in data:
            for row in data["playsTimeSeries"]:
                k = row["time"][:10]
                by_date[k].stream_count = max(by_date[k].stream_count, row["value"], key=NoneComparator)
        if "startsTimeSeries" in data:
            for row in data["startsTimeSeries"]:
                k = row["time"][:10]
                by_date[k].stream_start_count = max(
                    by_date[k].stream_start_count, row["value"], key=NoneComparator
                )
        if "listenersTimeSeries" in data:
            for row in data["listenersTimeSeries"]:
                k = row["time"][:10]
                by_date[k].listener_count = max(by_date[k].listener_count, row["value"], key=NoneComparator)
        if "followsTimeSeries" in data:
            for row in data["followsTimeSeries"]:
                k = row["time"][:10]
                by_date[k].follower_count = max(by_date[k].follower_count, row["value"], key=NoneComparator)
        if "engagedListenersTimeSeries" in data:
            for row in data["engagedListenersTimeSeries"]:
                k = row["time"][:10]
                by_date[k].engaged_listener_count = max(
                    by_date[k].engaged_listener_count, row["value"], key=NoneComparator
                )
        if "startsTotals" in data:
            pass
