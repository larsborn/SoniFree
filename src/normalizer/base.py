#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import abc
import logging
from typing import Dict

from lib.model import Response, DataPoint, Provider, ResponseMeta


class NoneComparator:
    def __init__(self, item):
        self.item = item

    def __lt__(self, other):
        if self.item is None:
            return other.item
        if other.item is None:
            return self.item
        return self.item < other.item


class BaseNormalizationStrategy(abc.ABC):
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    @abc.abstractmethod
    def normalize(self, by_date: Dict[str, DataPoint], response: Response):
        raise NotImplementedError()

    @abc.abstractmethod
    def should_apply(self, meta: ResponseMeta):
        raise NotImplementedError()

    @abc.abstractmethod
    def provider(self) -> Provider:
        raise NotImplementedError()
