#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import json
import os.path
import pathlib
from collections.abc import Iterable
from dataclasses import asdict
from typing import Dict

from lib.model import Response, ResponseMeta
from scraper.spotify import Scraper


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()

        return None


class ResponseManager:
    def __init__(self, meta_dir: str, payload_directory: str):
        if not os.path.exists(meta_dir) or not os.path.isdir(meta_dir):
            raise ValueError(f"Meta dir path {repr(meta_dir)} not a directory.")
        if not os.path.exists(payload_directory) or not os.path.isdir(payload_directory):
            raise ValueError(f"Payload dir path {repr(payload_directory)} not a directory.")
        self._meta_dir = meta_dir
        self._payload_directory = payload_directory

    def _meta_path(self, scraper_name: str, meta: ResponseMeta) -> str:
        ts = meta.timestamp
        dir_path = os.path.join(self._meta_dir, str(ts.year), f"{ts.month:02d}")
        self._ensure_dir(dir_path)

        return os.path.join(
            dir_path, f"{ts.strftime('%Y%m%d-%H%M%S')}-{scraper_name}-{meta.sha256[:10]}.json"
        )

    def _payload_path(self, sha256: str) -> str:
        dir_path = os.path.join(self._payload_directory, sha256[0:2], sha256[2:4], sha256[4:6])
        self._ensure_dir(dir_path)

        return os.path.join(dir_path, sha256)

    @staticmethod
    def _ensure_dir(d: str):
        if os.path.exists(d):
            if os.path.isdir(d):
                pass
            else:
                raise RuntimeError(f"Path {d:r} exists but is not a directory.")
        else:
            pathlib.Path(d).mkdir(parents=True, exist_ok=True)

    def store(self, scraper: Scraper, response: Response):
        meta_path = self._meta_path(scraper.name, response.meta)
        meta_exists = os.path.exists(meta_path)
        payload_path = self._payload_path(response.meta.sha256)
        payload_exists = os.path.exists(payload_path)

        if not meta_exists:
            with open(meta_path, "w") as fp:
                d = asdict(response.meta)
                json.dump(d, fp, sort_keys=True, cls=CustomEncoder)
        if not payload_exists:
            with open(payload_path, "wb") as fp:
                fp.write(response.data)

    def find(self) -> Iterable[Response]:
        for root, _, file_names in os.walk(self._meta_dir):
            for file_name in file_names:
                with open(os.path.join(root, file_name), "r") as fp:
                    yield self._hydrate(json.load(fp))

    def _hydrate(self, d: Dict) -> Response:
        meta = ResponseMeta(
            sha256=d["sha256"],
            url=d["url"],
            timestamp=datetime.datetime.fromisoformat(d["timestamp"]),
        )
        payload_path = self._payload_path(meta.sha256)
        with open(payload_path, "rb") as fp:
            return Response(meta=meta, data=fp.read())
