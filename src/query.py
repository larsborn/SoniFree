#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os

from lib.factory import LoggerFactory
from lib.model import Provider
from lib.repository import (
    FollowerRepository,
    ListenerRepository,
    ConsumptionRepository,
    StreamRepository,
    StreamStartRepository,
    EngagedListenerRepository,
)
from lib.responses import ResponseManager
from lib.validator import Validator
from normalizer.transformer import Transformer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", "-d", action="store_true")
    parser.add_argument("--meta-dir", default=os.getenv("META_DIR"))
    parser.add_argument("--payload-dir", default=os.getenv("PAYLOAD_DIR"))
    parser.add_argument(
        "--provider",
        default=os.getenv("PROVIDER", Provider.SPOTIFY.value),
        choices=[p.value for p in Provider],
        type=Provider,
    )
    parser.add_argument(
        "--type",
        default=os.getenv("TYPE", "follower"),
        choices=["follower", "listener", "engaged_listener", "consumption", "stream", "stream_start"],
    )
    args = parser.parse_args()

    logger = LoggerFactory.get(args.debug)
    transformer = Transformer(logger)
    validator = Validator(logger)
    response_manager = ResponseManager(args.meta_dir, args.payload_dir)
    by_provider = transformer.normalize(response_manager.find())
    by_date = transformer.provider_to_date_flip(by_provider)
    validator.validate(by_date)

    follower_repository = FollowerRepository(by_provider)
    listener_repository = ListenerRepository(by_provider)
    engaged_listener_repository = EngagedListenerRepository(by_provider)
    consumption_repository = ConsumptionRepository(by_provider)
    stream_repository = StreamRepository(by_provider)
    stream_start_repository = StreamStartRepository(by_provider)
    repositories = {
        "follower": follower_repository,
        "listener": listener_repository,
        "engaged_listener": engaged_listener_repository,
        "consumption": consumption_repository,
        "stream": stream_repository,
        "stream_start": stream_start_repository,
    }
    repository = repositories[args.type]
    dates = list(repository.get_dates())
    numbers = list(repository.find_by_provider(args.provider))
    for date, num in zip(dates, numbers):
        print(date, num)


if __name__ == "__main__":
    main()
