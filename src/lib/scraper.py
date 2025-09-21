#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import abc
import json
import logging
import time
from json import JSONDecodeError
from typing import Iterable, Dict, Optional

from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from lib.model import Response


class SeleniumFactory:
    # https://storage.googleapis.com/chrome-for-testing-public/138.0.7204.184/win64/chromedriver-win64.zip
    def __init__(self, chrome_executable_path: str):
        self._chrome_executable_path = chrome_executable_path

    def produce(self):
        options = Options()
        options.binary_location = self._chrome_executable_path
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        selenium = webdriver.Chrome(options=options)
        selenium.implicitly_wait(5)
        return selenium


class Scraper(abc.ABC):
    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self._name = name

    @property
    def name(self):
        return self._name

    def prepare(self):
        pass

    def extract_payloads(self) -> Iterable[Response]:
        raise NotImplementedError("Scraper not implemented")

    def postprocess(self):
        pass


class Selenium:
    def __init__(self, logger: logging.Logger, selenium_factory: SeleniumFactory, **kwargs):
        super().__init__(**kwargs)
        self._logger = logger
        self._selenium = selenium_factory.produce()

    def _wait_until(self, elem):
        wait = WebDriverWait(self._selenium, timeout=2)
        wait.until(lambda _: elem.is_displayed())
        time.sleep(1)

    def _flush_performance_log(self):
        list(self._selenium.get_log("performance"))

    def _get_performance_log_response_messages(self) -> Iterable[Dict]:
        def unpack_message(entry):
            return json.loads(entry["message"])["message"]

        browser_log = self._selenium.get_log("performance")
        messages = [unpack_message(entry) for entry in browser_log]
        yield from (message for message in messages if message["method"] == "Network.responseReceived")

    @staticmethod
    def _get_performance_log_url(message: Dict) -> str:
        return message["params"]["response"]["url"]

    def _get_performance_log_body(self, message: Dict) -> Optional[Dict]:
        try:
            body = self._selenium.execute_cdp_cmd(
                "Network.getResponseBody", {"requestId": message["params"]["requestId"]}
            )
        except WebDriverException:
            return None
        try:
            return json.loads(body["body"])
        except JSONDecodeError:
            return None
