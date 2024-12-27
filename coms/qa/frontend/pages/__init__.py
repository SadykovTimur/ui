from __future__ import annotations

from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from coms.qa.fixtures.application import Application

__all__ = ['Page']


class Page:
    def __init__(self, app: Application) -> None:
        self.app = app
        self.base_url = f'http://{app.ui}'
        self._el: Optional[WebElement] = None

    @property
    def driver(self) -> WebDriver:
        return self.app.driver

    @property
    def webelement(self) -> Optional[WebElement]:
        return self._el

    def open(self) -> Page:
        self.driver.get(self.base_url)

        return self
