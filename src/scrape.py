#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os

from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless

from lib.factory import LoggerFactory
from lib.model import SpotifyConfig, AmazonConfig
from lib.responses import ResponseManager
from lib.scraper import SeleniumFactory
from scraper.amazon import Amazon
from scraper.spotify import Spotify


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", "-d", action="store_true")
    parser.add_argument("--chrome-executable-path", default=os.getenv("CHROME_EXECUTABLE_PATH"))
    parser.add_argument("--meta-dir", default=os.getenv("META_DIR"))
    parser.add_argument("--payload-dir", default=os.getenv("PAYLOAD_DIR"))
    parser.add_argument("--filter-scraper")
    parser.add_argument("--spotify-user-name", default=os.getenv("SPOTIFY_USER_NAME"))
    parser.add_argument("--spotify-password", default=os.getenv("SPOTIFY_PASSWORD"))
    parser.add_argument("--spotify-podcast-id", default=os.getenv("SPOTIFY_PODCAST_ID"))
    parser.add_argument("--apple-user-name", default=os.getenv("APPLE_USER_NAME"))
    parser.add_argument("--apple-password", default=os.getenv("APPLE_PASSWORD"))
    parser.add_argument("--apple-podcast-id", default=os.getenv("APPLE_PODCAST_ID"))
    parser.add_argument("--amazon-user-name", default=os.getenv("AMAZON_USER_NAME"))
    parser.add_argument("--amazon-password", default=os.getenv("AMAZON_PASSWORD"))
    args = parser.parse_args()
    logger = LoggerFactory.get(args.debug)
    response_manager = ResponseManager(args.meta_dir, args.payload_dir)
    selenium_factory = SeleniumFactory(args.chrome_executable_path)
    anticaptcha_api_key = os.getenv("ANTICAPTCHA_API_KEY")
    if anticaptcha_api_key:
        recaptcha_solver = recaptchaV2Proxyless()
        recaptcha_solver.set_verbose(1)
        recaptcha_solver.set_key(anticaptcha_api_key)
    else:
        recaptcha_solver = None
    scraper_configs = [
        (Spotify, SpotifyConfig(args.spotify_user_name, args.spotify_password, args.spotify_podcast_id)),
        # (Apple, AppleConfig(args.apple_user_name, args.apple_password, args.apple_podcast_id)),
        (Amazon, AmazonConfig(args.amazon_user_name, args.amazon_password)),
    ]

    logger.info(f"Found {len(scraper_configs)} configured scraper(s)")
    scraper_filter = args.filter_scraper
    if scraper_filter:
        logger.info(f"This is a filtered run: {scraper_filter}")
    for scraper_cls, scraper_config in scraper_configs:
        scraper_name = scraper_cls.__name__
        logger.info(f"Running {scraper_name}...")
        if scraper_filter and scraper_filter != scraper_name:
            logger.info(f"Skipping {scraper_name}.")
            continue
        scraper = scraper_cls(
            logger=logger,
            selenium_factory=selenium_factory,
            config=scraper_config,
            recaptcha_solver=recaptcha_solver,
            name=scraper_cls.__name__,
        )
        scraper.prepare()
        responses = list(scraper.extract_payloads())
        scraper.postprocess()
        logger.info(f"Got {len(responses)} response(s)")
        for response in responses:
            response_manager.store(scraper, response)
    logger.info("Scraping completed, shutting down...")


if __name__ == "__main__":
    main()
