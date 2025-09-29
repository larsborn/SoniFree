#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from typing import Iterable, Optional

from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless
from selenium.webdriver.common.by import By

from lib.model import AppleConfig, Response
from lib.scraper import SeleniumFactory, Selenium, Scraper


class Apple(Selenium, Scraper):
    def __init__(
        self,
        logger: logging.Logger,
        selenium_factory: SeleniumFactory,
        config: AppleConfig,
        recaptcha_solver: Optional[recaptchaV2Proxyless],
        name: str,
    ):
        super().__init__(
            logger=logger, selenium_factory=selenium_factory, recaptcha_solver=recaptcha_solver, name=name
        )
        self._config = config

    def prepare(self):
        self._selenium.get(f"https://idmsa.apple.com/IDMSWebAuth/signin?appIdKey={self._config.app_id_key}")

        iframe = self._selenium.find_element(By.TAG_NAME, "iframe")
        self._selenium.switch_to.frame(iframe)

        login_field = self._selenium.find_element(By.ID, "account_name_text_field")
        self._wait_until(login_field)
        login_field.send_keys(self._config.user_name)

        login_button = self._selenium.find_element(By.ID, "sign-in")
        self._wait_until(login_button)
        login_button.click()

        password_field = self._selenium.find_element(By.ID, "password_text_field")
        self._wait_until(password_field)
        password_field.send_keys(self._config.password)

        login_button.click()
        # TODO 2fa

    def extract_payloads(self) -> Iterable[Response]:
        self._selenium.get(
            f"https://podcastsconnect.apple.com/analytics/show/-/{self._config.podcast_id}/overview"
        )
        # TODO scrape the actual data
        return []
