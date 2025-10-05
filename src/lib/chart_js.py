#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Dict, Optional, List, Iterable

from lib.model import PROVIDER_COLORS, Event
from lib.repository import AbstractRepository
from normalizer.transformer import Transformer


class ChartJsJsonGenerator:
    def __init__(self, transformer: Transformer):
        self._transformer = transformer

    def generate(self, chart_label: str, repository: AbstractRepository, events: List[Event]) -> Dict:
        datasets = [
            self._generate_dataset(
                provider.value,
                PROVIDER_COLORS[provider],
                list(repository.find_by_provider(provider)),
            )
            for provider in repository.providers()
        ]
        return self._generate_config(chart_label, repository.get_dates(), datasets, events)

    @staticmethod
    def _generate_dataset(label: str, color: str, data: List[Optional[int]]):
        return {
            "label": label,
            "borderColor": color,
            "pointRadius": 0,
            "borderWidth": 1,
            "backgroundColor": f"transparentize({color}, 0.5)",
            "data": data,
        }

    @staticmethod
    def _generate_config(
        chart_label: str, labels: List[str], datasets: List[Dict], events: List[Event]
    ) -> Dict:
        return {
            "type": "line",
            "data": {
                "labels": labels,
                "datasets": datasets,
            },
            "lineAtIndex": list(ChartJsJsonGenerator._event_indices(labels, events)),
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {
                        "position": "top",
                    },
                    "title": {"display": True, "text": chart_label},
                },
            },
        }

    @staticmethod
    def _event_indices(labels: List[str], events: List[Event]) -> Iterable[Dict]:
        for idx, date in enumerate(labels):
            for event in events:
                if event.date == date:
                    yield {"index": idx, "caption": event.name}
