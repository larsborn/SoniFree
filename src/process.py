#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import os

from lib.chart_js import ChartJsJsonGenerator
from lib.factory import LoggerFactory, KeyFactory
from normalizer.transformer import Transformer
from lib.responses import ResponseManager
from lib.validator import Validator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", "-d", action="store_true")
    parser.add_argument("--meta-dir", default=os.getenv("META_DIR"))
    parser.add_argument("--payload-dir", default=os.getenv("PAYLOAD_DIR"))
    parser.add_argument(
        "--output-strategy",
        default=os.getenv("OUTPUT_STRATEGY", "chartjs"),
        choices=["elastic", "chartjs"],
    )
    parser.add_argument(
        "--json-result-dir",
        default=os.getenv(
            "JSON_RESULT_DIR", os.path.join(os.path.dirname(__file__), "..", "frontend", "src")
        ),
    )
    args = parser.parse_args()

    logger = LoggerFactory.get(args.debug)
    transformer = Transformer(logger)
    char_generator = ChartJsJsonGenerator(transformer)
    validator = Validator(logger)
    response_manager = ResponseManager(args.meta_dir, args.payload_dir)
    by_date = transformer.provider_to_date_flip(transformer.normalize(response_manager.find()))
    validator.validate(by_date)

    if args.output_strategy == "chartjs":

        for file_name, config in [
            (
                "follower_count.json",
                char_generator.generate("Follower Count", by_date, lambda dp: dp.follower_count),
            ),
            (
                "listener_count.json",
                char_generator.generate("Listener Count", by_date, lambda dp: dp.listener_count),
            ),
            (
                "consumption_seconds.json",
                char_generator.generate("Consumption Seconds", by_date, lambda dp: dp.consumption_seconds),
            ),
            (
                "stream_count.json",
                char_generator.generate("Stream Count", by_date, lambda dp: dp.stream_count),
            ),
            (
                "stream_start_count.json",
                char_generator.generate("Stream Starts", by_date, lambda dp: dp.stream_start_count),
            ),
        ]:
            json_file_name = os.path.join(args.json_result_dir, file_name)
            with open(json_file_name, "w") as fp:
                json.dump(config, fp, indent=4)
            logger.info(f"Wrote {json_file_name}.")

    elif args.output_strategy == "elastic":
        for date in sorted(by_date.keys()):
            by_provider = by_date[date]
            for provider, point in by_provider.items():
                data = point.dict
                data["_id"] = KeyFactory.for_state(provider, date)
                data["date"] = date
                print(json.dumps(data, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
