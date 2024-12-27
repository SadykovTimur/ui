import http
import json
import time
from typing import Callable, Dict, List, Optional, Tuple

import allure
import pytest
import requests
from _pytest.fixtures import FixtureRequest
from selenium.common.exceptions import InvalidSessionIdException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from coms.qa.core.helpers import wait_for

__all__ = ['Application']


class Application:
    def __init__(self, browser: str, device_type: str) -> None:
        self.browser: str = browser
        self.device_type: str = device_type
        self._driver: Optional[WebDriver] = None
        self._ui: str = ''

    @property
    def driver(self) -> WebDriver:
        if self._driver is None:
            raise RuntimeError('Driver not initialized')

        return self._driver

    @driver.setter
    def driver(self, value: WebDriver) -> None:
        self._driver = value

    @property
    def ui(self) -> str:
        return self._ui

    @ui.setter
    def ui(self, value: str) -> None:
        self._ui = value

    def set_implicitly_wait(self, wait: int = 30) -> None:
        self.driver.implicitly_wait(wait)

    def restore_implicitly_wait(self) -> None:
        self.set_implicitly_wait()

    def destroy(self) -> None:
        self.driver.quit()

    def is_mobile(self) -> bool:
        return self.device_type == 'mobile'

    def move_to_element(
        self, element: Optional[WebElement] = None, locator: Optional[Tuple[By, str]] = None
    ) -> WebElement:
        if element is None:
            assert locator is not None, 'Both parameters are None(element, locator), incorrect call'

            element = self.driver.find_element(*locator)

        actions = ActionChains(self.driver)  # type: ignore[no-untyped-call]
        actions.move_to_element(element).perform()  # type: ignore[no-untyped-call]
        time.sleep(1)

        return element

    def scroll_to_element(
        self, element: Optional[WebElement] = None, locator: Optional[Tuple[By, str]] = None
    ) -> WebElement:
        if element is None:
            assert locator is not None, 'Both parameters are None(element, locator), incorrect call'

            element = self.driver.find_element(*locator)

        self.driver.execute_script(  # type: ignore[no-untyped-call]
            'arguments[0].scrollIntoView({block: "center"})', element
        )
        time.sleep(1)

        return element

    def is_element_exists(
        self,
        locator: Tuple[By, str],
        element: Optional[WebElement] = None,
    ) -> bool:
        self.set_implicitly_wait(1)
        is_exists = False

        try:
            if element:
                element.find_element(*locator)
            else:
                self.driver.find_element(*locator)

            is_exists = True

        except NoSuchElementException:
            pass

        self.restore_implicitly_wait()

        return is_exists

    def get_network_messages(self) -> List[Dict]:
        return self.driver.execute_script(  # type: ignore[no-untyped-call]
            "var performance = window.performance || window.mozPerformance || "
            "window.msPerformance || window.webkitPerformance || {};"
            " var network = performance.getEntries() || {};"
            " return network;"
        )

    # pylint: disable=protected-access
    def send_command(self, command: str, params: Dict) -> str:
        resource = f'/session/{self.driver.session_id}/chromium/send_command_and_get_result'
        url = self.driver.command_executor._url + resource
        body = json.dumps({'cmd': command, 'params': params})
        response = self.driver.command_executor._request('POST', url, body)

        if 'status' in response.keys() and response['status']:
            raise Exception(response.get('value'))

        return response.get('value')


# pylint: disable=unused-argument
@pytest.fixture
def make_app(request: FixtureRequest, make_driver: Callable[..., WebDriver]) -> Callable[..., Application]:
    def make(browser: str, device_type: str) -> Application:
        fixture = Application(browser, device_type)
        fixture.ui = request.config.option.ui_url
        fixture.driver = make_driver(browser, device_type)
        failed_before = request.session.testsfailed
        session_id = fixture.driver.session_id
        remote_ip = request.config.option.remote_ip
        remote_port = request.config.option.remote_port

        def fin() -> None:
            if is_driver_alive(fixture):
                if failed_before != request.session.testsfailed:
                    try:
                        allure.attach(
                            name='Screenshot',
                            body=fixture.driver.get_screenshot_as_png(),
                            attachment_type=allure.attachment_type.PNG,
                        )
                    except TypeError:
                        pass

                fixture.destroy()

                if request.config.option.enable_video and failed_before != request.session.testsfailed:

                    def condition() -> bytes:
                        path = f'http://{remote_ip}:{remote_port}/video/{session_id}.mp4'
                        r = requests.get(path)

                        assert r.status_code == http.HTTPStatus.OK

                        return r.content

                    response = wait_for(condition, msg='Wait for video file')
                    allure.attach(
                        name=f'{session_id}.mp4',
                        body=response,
                        attachment_type=allure.attachment_type.MP4,
                    )

                if request.config.option.enable_video:

                    def condition_delete() -> bool:
                        path = f'http://{remote_ip}:{remote_port}/video/{session_id}.mp4'
                        response = requests.delete(path)

                        return response.status_code == http.HTTPStatus.OK

                    wait_for(condition_delete, msg='Wait for delete video file')

        request.addfinalizer(fin)

        return fixture

    return make


def is_driver_alive(app: Application) -> bool:
    try:
        assert app.driver.get_screenshot_as_png()

        return True
    except InvalidSessionIdException:
        return False
