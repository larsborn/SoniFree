#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import time
from typing import Iterable

from selenium.webdriver.common.by import By

from lib.model import AmazonConfig, Response
from lib.scraper import SeleniumFactory, Selenium, Scraper


class Amazon(Selenium, Scraper):
    def __init__(
        self, logger: logging.Logger, selenium_factory: SeleniumFactory, config: AmazonConfig, name: str
    ):
        super().__init__(logger=logger, selenium_factory=selenium_factory, name=name)
        self._config = config

    def prepare(self):
        self._selenium.get(
            "https://www.amazon.com/ap/signin?openid.ns=http://specs.openid.net/auth/2.0&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select&openid.identity=http://specs.openid.net/auth/2.0/identifier_select&pageId=amzn_ziggy_ui&openid.assoc_handle=amzn_podcaster_portal_us&language=en_US&openid.mode=checkid_setup&openid.return_to=https://podcasters.amazon.com/auth/csrf?path=https://podcasters.amazon.com/podcasts"
        )
        login_field = self._selenium.find_element(By.ID, "ap_email")
        self._wait_until(login_field)
        login_field.send_keys(self._config.user_name)

        login_button = self._selenium.find_element(By.ID, "continue")
        self._wait_until(login_button)
        login_button.click()

        password_field = self._selenium.find_element(By.ID, "ap_password")
        self._wait_until(password_field)
        password_field.send_keys(self._config.password)

        login_button = self._selenium.find_element(By.ID, "auth-signin-button")
        self._wait_until(login_button)
        login_button.click()

    def extract_payloads(self) -> Iterable[Response]:
        dropdown_button = self._selenium.find_element(By.CLASS_NAME, "TimeFrame__dropdown-button")
        self._wait_until(dropdown_button)
        dropdown_button.click()

        item = self._selenium.find_element(
            By.CSS_SELECTOR,
            '[data-id="selectTimeFrameAllTime-podcasterAnalyticsOverview"]',
        )
        self._wait_until(item)

        self._flush_performance_log()
        item.click()
        time.sleep(1)

        for message in self._get_performance_log_response_messages():
            url = self._get_performance_log_url(message)
            if "metrics/podcast" not in url:
                continue
            body = self._get_performance_log_body(message)
            if body is None:
                continue
            yield Response.from_dict(body, url)

    def postprocess(self):
        self._selenium.get(
            "https://www.amazon.com/ap/signin?openid.ns=http://specs.openid.net/auth/2.0&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select&openid.identity=http://specs.openid.net/auth/2.0/identifier_select&pageId=amzn_ziggy_ui&openid.assoc_handle=amzn_podcaster_portal_us&language=en_US&openid.mode=logout&openid.return_to=https://podcasters.amazon.com"
        )
