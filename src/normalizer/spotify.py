# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from typing import Dict

from lib.model import DataPoint, Response, Provider, ResponseMeta
from normalizer.base import BaseNormalizationStrategy, NoneComparator


class Spotify(BaseNormalizationStrategy):
    def should_apply(self, meta: ResponseMeta):
        return "spotify" in meta.url

    def provider(self) -> Provider:
        return Provider.SPOTIFY

    def normalize(self, by_date: Dict[str, DataPoint], response: Response) -> None:
        api_route = "/".join(response.meta.url.split("/")[7:]).split("?")[0]
        if any(
            api_route == s
            for s in ["metadata", "seamless_switch", "onboarding", "followersDelta", "onSpotifyOverview"]
        ):
            return
        if api_route.endswith("/latest") or api_route.endswith("/total"):
            return

        data = json.loads(response.data.decode("utf-8"))
        if api_route == "consumption/daily":
            for row in data["consumptionTimes"]:
                k = row["date"]
                by_date[k].consumption_seconds = max(
                    by_date[k].consumption_seconds,
                    int(row["totalConsumptionHours"] * 60 * 60),
                    key=NoneComparator,
                )
                by_date[k].foreground_consumption_seconds = max(
                    by_date[k].foreground_consumption_seconds,
                    int(row["foregroundConsumptionHours"] * 60 * 60),
                    key=NoneComparator,
                )
        elif api_route == "followers":
            for row in data["counts"]:
                k = row["date"]
                by_date[k].follower_count = max(
                    by_date[k].follower_count,
                    row["count"],
                    key=NoneComparator,
                )
        elif api_route == "listeners":
            for row in data["counts"]:
                k = row["date"]
                by_date[k].listener_count = max(
                    by_date[k].listener_count,
                    row["count"],
                    key=NoneComparator,
                )
        elif api_route == "detailedStreams":
            for row in data["detailedStreams"]:
                k = row["date"]
                by_date[k].stream_start_count = max(
                    by_date[k].stream_start_count,
                    row["starts"],
                    key=NoneComparator,
                )
                by_date[k].stream_count = max(
                    by_date[k].stream_count,
                    row["streams"],
                    key=NoneComparator,
                )
        else:
            self._logger.warning(
                f"Unknown API route {api_route} (keys={data.keys}): {json.dumps(data)[:200]}"
            )

        return
