#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Dict, Optional, List

from lib.model import DataPoint, Provider, PROVIDER_COLORS
from lib.repository import AbstractRepository
from normalizer.transformer import Transformer


class ChartJsJsonGenerator:
    def __init__(self, transformer: Transformer):
        self._transformer = transformer

    def generate(
        self,
        chart_label: str,
        by_date: Dict[str, Dict[Provider, DataPoint]],
        repository: AbstractRepository,
    ) -> Dict:
        labels = list(by_date.keys())
        by_provider = self._transformer.date_to_provider_flip(by_date)
        datasets = [
            self._generate_dataset(
                provider.value,
                PROVIDER_COLORS[provider],
                [repository.extract_number(dp) for dp in by_date.values()],
            )
            for provider, by_date in by_provider.items()
        ]
        return self._generate_config(chart_label, labels, datasets)

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
    def _generate_config(chart_label: str, labels: List[str], datasets: List[Dict]) -> Dict:
        return {
            "type": "line",
            "data": {
                "labels": labels,
                "datasets": datasets,
            },
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
