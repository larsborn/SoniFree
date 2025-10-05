#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import os

from lib.chart_js import ChartJsJsonGenerator
from lib.factory import LoggerFactory, KeyFactory
from lib.model import Provider
from lib.repository import (
    FollowerRepository,
    ListenerRepository,
    ConsumptionRepository,
    StreamRepository,
    StreamStartRepository,
    EngagedListenerRepository,
    EventsRepository,
)
from lib.responses import ResponseManager
from lib.validator import Validator
from normalizer.transformer import Transformer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", "-d", action="store_true")
    parser.add_argument("--meta-dir", default=os.getenv("META_DIR"))
    parser.add_argument("--payload-dir", default=os.getenv("PAYLOAD_DIR"))
    parser.add_argument("--event-marker-file-name", default=os.getenv("EVENT_MARKER_FILE_NAME"))
    parser.add_argument(
        "--output-strategy",
        default=os.getenv("OUTPUT_STRATEGY", "chartjs"),
        choices=["elastic", "chartjs"],
    )
    parser.add_argument(
        "--json-result-dir",
        default=os.getenv(
            "JSON_RESULT_DIR", os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "data")
        ),
    )
    args = parser.parse_args()

    logger = LoggerFactory.get(args.debug)
    transformer = Transformer(logger)
    validator = Validator(logger)
    response_manager = ResponseManager(args.meta_dir, args.payload_dir)
    by_provider = transformer.normalize(response_manager.find())
    by_date = transformer.provider_to_date_flip(by_provider)
    validator.validate(by_date)

    event_repository = EventsRepository(args.event_marker_file_name)
    follower_repository = FollowerRepository(by_provider)
    listener_repository = ListenerRepository(by_provider)
    engaged_listener_repository = EngagedListenerRepository(by_provider)
    consumption_repository = ConsumptionRepository(by_provider)
    stream_repository = StreamRepository(by_provider)
    stream_start_repository = StreamStartRepository(by_provider)
    char_generator = ChartJsJsonGenerator(transformer)

    events = event_repository.all()
    if args.output_strategy == "chartjs":
        for file_name, config in [
            (
                "follower_count.json",
                char_generator.generate("Follower Count", follower_repository, events),
            ),
            (
                "listener_count.json",
                char_generator.generate("Listener Count", listener_repository, events),
            ),
            (
                "engaged_listener_count.json",
                char_generator.generate("Engaged Listener Count", engaged_listener_repository, events),
            ),
            (
                "consumption_seconds.json",
                char_generator.generate("Consumption Seconds", consumption_repository, events),
            ),
            (
                "stream_count.json",
                char_generator.generate("Stream Count", stream_repository, events),
            ),
            (
                "stream_start_count.json",
                char_generator.generate("Stream Starts", stream_start_repository, events),
            ),
        ]:
            json_file_name = os.path.join(args.json_result_dir, file_name)
            with open(json_file_name, "w") as fp:
                json.dump(config, fp, indent=4)
            logger.info(f"Wrote {json_file_name}.")

        json_file_name = os.path.join(args.json_result_dir, "aggregates.json")
        with open(json_file_name, "w") as fp:
            aggregates = {
                "sum": {
                    "followers": follower_repository.sum(),
                    "listeners": listener_repository.sum(),
                    "consumed": consumption_repository.sum(),
                    "streams": stream_repository.sum(),
                },
                "by_provider": {},
            }
            for provider in Provider:
                aggregates["by_provider"][provider.value] = {
                    "followers": follower_repository.sum_by_provider(provider),
                    "listeners": listener_repository.sum_by_provider(provider),
                    "engaged_listeners": engaged_listener_repository.sum_by_provider(provider),
                    "consumed": consumption_repository.sum_by_provider(provider),
                    "streams": stream_repository.sum_by_provider(provider),
                    "last_date": follower_repository.last_date_of_provider(provider),
                }
            json.dump(aggregates, fp, indent=4)
        logger.info(f"Wrote {json_file_name}.")

    elif args.output_strategy == "elastic":
        for date in sorted(by_date.keys()):
            for provider, point in by_date[date].items():
                data = point.dict
                data["_id"] = KeyFactory.for_state(provider, date)
                data["date"] = date
                print(json.dumps(data, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
