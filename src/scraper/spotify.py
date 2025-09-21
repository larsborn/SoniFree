#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import time
import urllib.parse

from selenium.webdriver.common.by import By

from lib.model import SpotifyConfig, Response
from lib.scraper import Selenium, Scraper, SeleniumFactory


class Spotify(Selenium, Scraper):
    def __init__(
        self, logger: logging.Logger, selenium_factory: SeleniumFactory, config: SpotifyConfig, name: str
    ):
        super().__init__(logger=logger, selenium_factory=selenium_factory, name=name)
        self._config = config

    def prepare(self):
        self._login()

    def extract_payloads(self):
        dropdown_element = self._selenium.find_element(
            By.CSS_SELECTOR, "#dropdown-toggle-spotify-stats-chart-date"
        )
        self._wait_until(dropdown_element)

        dropdown_element.click()
        element = self._selenium.find_element(By.CSS_SELECTOR, "#allTime")
        self._wait_until(element)

        self._flush_performance_log()
        element.click()
        time.sleep(1)

        response_messages = self._get_performance_log_response_messages()
        for message in response_messages:
            url = self._get_performance_log_url(message)
            if self._config.podcast_id not in url:
                continue
            body = self._get_performance_log_body(message)
            if body is None:
                continue
            yield Response.from_dict(body, url)

    def postprocess(self):
        self._logout()

    def _login(self):
        podcast_url = f"https://creators.spotify.com/dash/show/{self._config.podcast_id}/analytics/overview"
        self._selenium.get(
            f"https://accounts.spotify.com/en/login"
            f"?login_hint={urllib.parse.quote_plus(self._config.user_name)}"
            f"&allow_password=1"
            f"&continue={urllib.parse.quote_plus(podcast_url)}"
        )

        password_field = self._selenium.find_element(By.ID, "login-password")
        self._wait_until(password_field)
        password_field.send_keys(self._config.password)

        login_button = self._selenium.find_element(By.ID, "login-button")
        self._wait_until(login_button)
        login_button.click()

    def _logout(self):
        self._selenium.get("https://accounts.spotify.com/logout")
