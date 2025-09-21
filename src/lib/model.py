#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import enum
import hashlib
import json
from dataclasses import dataclass
from typing import Optional, Dict, Union, DefaultDict


@dataclass
class ResponseMeta:
    sha256: str
    timestamp: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
    url: Optional[str] = None


@dataclass
class Response:
    meta: ResponseMeta
    data: bytes

    @staticmethod
    def from_dict(d: Dict, url: Optional[str] = None):
        dumped = json.dumps(d, sort_keys=False).encode("utf-8")

        return Response(
            meta=ResponseMeta(sha256=hashlib.sha256(dumped).hexdigest(), url=url),
            data=dumped,
        )


@dataclass
class SpotifyConfig:
    user_name: str
    password: str
    podcast_id: str


@dataclass
class AppleConfig:
    user_name: str
    password: str
    podcast_id: str
    app_id_key: str


@dataclass
class AmazonConfig:
    user_name: str
    password: str


class Provider(enum.Enum):
    SPOTIFY = "Spotify"
    APPLE = "Apple"
    AMAZON = "Amazon"


PROVIDER_COLORS = {
    Provider.SPOTIFY: "rgb(30 215 96)",
    Provider.APPLE: "rgb(125, 125, 125",
    Provider.AMAZON: "rgb(255, 153, 0)",
}


@dataclass
class DataPoint:
    provider: Optional[Provider] = None
    follower_count: Optional[int] = None
    listener_count: Optional[int] = None
    consumption_seconds: Optional[int] = None
    foreground_consumption_seconds: Optional[int] = None
    stream_count: Optional[int] = None
    stream_start_count: Optional[int] = None

    @property
    def no_data_set(self):
        return (
            self.follower_count is None
            and self.listener_count is None
            and self.consumption_seconds is None
            and self.foreground_consumption_seconds is None
            and self.stream_count is None
            and self.stream_start_count is None
        )

    @property
    def dict(self):
        return {
            "scraper": self.provider.value or 0,
            "follower_count": self.follower_count or 0,
            "listener_count": self.listener_count or 0,
            "consumption_seconds": self.consumption_seconds or 0,
            "foreground_consumption_seconds": self.foreground_consumption_seconds or 0,
            "stream_count": self.stream_count or 0,
            "stream_start_count": self.stream_start_count or 0,
        }

    def duplicate(self):
        return DataPoint(
            self.provider,
            self.follower_count,
            self.listener_count,
            self.consumption_seconds,
            self.foreground_consumption_seconds,
            self.stream_count,
            self.stream_start_count,
        )


DataPointStrDict = Union[DefaultDict[str, DataPoint], Dict[str, DataPoint]]
