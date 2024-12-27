from __future__ import annotations

from typing import List, Tuple, Union

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from coms.qa.fixtures.application import Application
from coms.qa.frontend.constants import WEB_DRIVER_WAIT
from coms.qa.frontend.helpers.custom_wait_conditions import ElementToBeClickable

__all__ = ['Component', 'Components', 'ComponentWrapper', 'LOCATOR_MAP']


LOCATOR_MAP = {
    'class_name': By.CLASS_NAME,
    'css': By.CSS_SELECTOR,
    'id': By.ID,
    'link_text': By.LINK_TEXT,
    'name': By.NAME,
    'partial_link_text': By.PARTIAL_LINK_TEXT,
    'tag': By.TAG_NAME,
    'xpath': By.XPATH,
    'dat': By.CSS_SELECTOR,
    'datc': By.CSS_SELECTOR,
}


class ComponentWrapper:
    def __init__(
        self,
        app: Application,
        element: WebElement,
        locator: Tuple[By, str],
    ) -> None:
        self.app = app
        self.wait = WebDriverWait(self.driver, WEB_DRIVER_WAIT)
        self._el: WebElement = element
        self._locator: Tuple[By, str] = locator
        self.mask_template: str = 'data-autotest'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}'

    def __getattr__(self, attr) -> str:
        return getattr(self._el, attr)

    @property
    def driver(self) -> WebDriver:
        return self.app.driver

    @property
    def webelement(self) -> WebElement:
        return self._el

    @property
    def enabled(self) -> bool:
        return self._el.is_enabled()

    @property
    def disabled(self) -> bool:
        return not self.enabled

    @property
    def value(self) -> str:
        return self._el.get_attribute('value')

    @property
    def visible(self) -> bool:
        return self._el.is_displayed()

    def wait_for_visibility(self) -> ComponentWrapper:
        with allure.step(f'Waiting for {self} visibility'):
            if self._el is None:
                self.wait.until(ec.visibility_of_element_located(self._locator))
            else:
                self.wait.until(ec.visibility_of(self._el))  # type: ignore[no-untyped-call]

            return self

    def wait_for_invisibility(self) -> ComponentWrapper:
        with allure.step(f'Waiting for {self} invisibility'):
            if self._el is None:
                self.wait.until(ec.invisibility_of_element_located(self._locator))
            else:
                self.wait.until(ec.invisibility_of_element(self._el))  # type: ignore[no-untyped-call]

            return self

    def wait_for_clickability(self) -> ComponentWrapper:
        with allure.step(f'Waiting for {self} clickability'):
            self.wait.until(ElementToBeClickable(element=self._el))

            return self


class Component:
    def __init__(self, **locators) -> None:
        self.mask_template: str = 'data-autotest'

        if not locators:
            raise ValueError('Please specify a locator')

        for key, value in locators.items():
            if key == 'dat':
                value = f'[{self.mask_template}={value}]'
            elif key == 'datc':
                value = f'[{self.mask_template}*={value}]'

            self._locator = (LOCATOR_MAP[key], value)

    def find(self, instance) -> WebElement:
        parent_element: Union[WebElement, WebDriver]
        parent_element = instance.webelement if instance.webelement is not None else instance.app.driver

        return parent_element.find_element(*self._locator)

    def __get__(self, instance, owner):
        return ComponentWrapper(instance.app, self.find(instance), self._locator)

    def __set__(self, instance, value):
        pass


class Components(Component):
    def finds(self, instance) -> List[WebElement]:
        parent_element: Union[WebElement, WebDriver]
        parent_element = instance.webelement if instance.webelement is not None else instance.app.driver

        return parent_element.find_elements(*self._locator)

    def __get__(self, instance, owner):
        ret: List[ComponentWrapper] = []

        for webelement in self.finds(instance):
            ret.append(ComponentWrapper(instance.app, webelement, self._locator))

        return ret

    def __set__(self, instance, value):
        pass
