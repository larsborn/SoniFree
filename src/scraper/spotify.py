#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import time
import urllib.parse
from typing import Optional

from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from lib.model import SpotifyConfig, Response
from lib.scraper import Selenium, Scraper, SeleniumFactory, ScraperException


class Spotify(Selenium, Scraper):
    def __init__(
        self,
        logger: logging.Logger,
        selenium_factory: SeleniumFactory,
        config: SpotifyConfig,
        recaptcha_solver: Optional[recaptchaV2Proxyless],
        name: str,
    ):
        super().__init__(
            logger=logger, selenium_factory=selenium_factory, name=name, recaptcha_solver=recaptcha_solver
        )
        self._config = config

    def prepare(self):
        self._login()

    def extract_payloads(self):
        self._logger.info(f"{self.__class__.__name__} ➤ Switch to all time chart...")
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

        self._logger.info(f"{self.__class__.__name__} ➤ Capturing responses...")
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
        self._logger.info(f"{self.__class__.__name__} ➤ Logging in...")
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
        time.sleep(2)

        if self._recaptcha_verification():
            self._logger.info(f"{self.__class__.__name__} ➤ Checking for human validation...")
            if self._recaptcha_solver:
                sitekey = self._selenium.find_element(By.CLASS_NAME, "g-recaptcha").get_attribute(
                    "data-sitekey"
                )
                for iframe_no, iframe in enumerate(self._selenium.find_elements(By.TAG_NAME, "iframe")):
                    self._logger.debug(f"{self.__class__.__name__} ➤ checking iframe {iframe_no}")
                    try:
                        if not iframe.get_property("src").startswith("https://www.google.com/recaptcha/"):
                            continue
                    except NoSuchElementException as e:
                        self._logger.debug(
                            f"{self.__class__.__name__} ➤ iframe {iframe_no} doesn't have a src attribute"
                        )
                        continue

                    self._selenium.switch_to.frame(iframe)

                    captcha_response_fields = self._selenium.find_elements(By.ID, "g-recaptcha-response")
                    checkboxs = self._selenium.find_elements(By.CLASS_NAME, "rc-anchor-content")
                    if len(captcha_response_fields) != 1 and len(checkboxs) != 1:
                        captcha_response_field = captcha_response_fields[0]
                        checkbox = checkboxs[0]
                        self._recaptcha_solver.set_website_url(podcast_url)
                        self._recaptcha_solver.set_website_key(sitekey)

                        # captcha_response = self._recaptcha_solver.solve_and_return_solution()
                        # if captcha_response == 0:
                        #     raise ScraperException(
                        #         f"Got error from anti-captcha ({self._recaptcha_solver.error_code}): "
                        #         f"{self._recaptcha_solver.err_string}"
                        #     )

                        self._selenium.execute_script(
                            "document.getElementById('g-recaptcha-response').style.display = '';"
                        )
                        import IPython

                        IPython.embed()
                        captcha_response_field.send_keys(self._config.password)

                        self._wait_until(checkbox)
                        checkbox.click()
                        self._selenium.switch_to.default_content()
                        break
                else:
                    raise ScraperException("Expected reCaptcha to exist but couldn't find it")
            else:
                self._logger.info(
                    f"{self.__class__.__name__} ➤ No anti-captcha API key supplied, waiting for manual solve..."
                )
                while self._recaptcha_verification():
                    time.sleep(1)

    def _recaptcha_verification(self) -> bool:
        body = self._selenium.find_element(By.TAG_NAME, "body")
        return "We need to make sure that you're a human" in body.text

    def _logout(self):
        self._selenium.get("https://accounts.spotify.com/logout")
