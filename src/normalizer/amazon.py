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

        if "followsAggregate" in data:
            pass
        if "followsTotals" in data:
            follower_count = data["followsTotals"]["total"]
            # TODO what is the date here?
        if "listenersAggregate" in data:
            pass
        if "listenersTotals" in data:
            print("listenersTotals", data["listenersTotals"])
        if "playsAggregate" in data:
            pass
        if "playsTimeSeries" in data:
            for row in data["playsTimeSeries"]:
                k = row["time"][:10]
                by_date[k].stream_count = max(by_date[k].stream_count, row["value"], key=NoneComparator)
        if "playsTotals" in data:
            print("playsTotals", data["playsTotals"])
        if "startsAggregate" in data:
            pass
        if "startsTimeSeries" in data:
            for row in data["startsTimeSeries"]:
                k = row["time"][:10]
                by_date[k].stream_start_count = max(
                    by_date[k].stream_start_count, row["value"], key=NoneComparator
                )
        if "startsTotals" in data:
            print("startsTotals", data["startsTotals"])
