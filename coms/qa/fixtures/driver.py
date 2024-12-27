import logging
from typing import Any, Callable

import allure
import pytest
from _pytest.fixtures import FixtureRequest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

from coms.qa.frontend.constants import (
    DRIVER_HEIGHT,
    DRIVER_RPS,
    DRIVER_WIDTH,
    MOBILE_DRIVER_HEIGHT,
    MOBILE_DRIVER_WIDTH,
    VIDEO_FRAME_RATE,
)


def screen_resolution(device_type: str) -> tuple[int, int]:
    if device_type == 'mobile':
        return MOBILE_DRIVER_WIDTH, MOBILE_DRIVER_HEIGHT

    return DRIVER_WIDTH, DRIVER_HEIGHT


def desired_capabilities(browser: str, enable_video: bool, test_name: str, ignore_certificate: bool) -> dict[str, Any]:
    capabilities = {
        'browserName': browser,
        'bstack:options': {
            'screenResolution': f'{DRIVER_WIDTH}x{DRIVER_HEIGHT}x{DRIVER_RPS}',
            'videoFrameRate': VIDEO_FRAME_RATE,
        },
        'selenoid:options': {'enableVideo': enable_video, 'name': f'coms/{test_name}'},
        'goog:loggingPrefs': {"performance": "ALL"},
    }

    if browser == 'chrome':
        chrome_options = Options()
        chrome_options.add_experimental_option(
            "prefs", {'profile.content_settings.exceptions.clipboard': {'*': {'setting': 1}}}
        )
        capabilities.update(chrome_options.to_capabilities())

    if browser not in ['safari']:
        capabilities['selenoid:options']['enableVNC'] = True  # type: ignore[index]

    if ignore_certificate:
        capabilities['acceptInsecureCerts'] = True  # type: ignore[assignment]

    return capabilities


@pytest.fixture
def make_driver(request: FixtureRequest) -> Callable[..., WebDriver]:
    def make(browser: str, device_type: str) -> WebDriver:
        allure.dynamic.label('browser', browser)
        allure.dynamic.label('device_type', device_type)
        remote_ip: str = request.config.option.remote_ip
        remote_port: str = request.config.option.remote_port
        remote_ui: str = request.config.option.remote_ui
        remote_ui_port: str = request.config.getoption(name='remote_ui_port', default='8080')
        remote_protocol: str = request.config.getoption(name='remote_protocol', default='http')
        wait: int = request.config.option.wait
        enable_video: bool = request.config.option.enable_video
        ignore_certificate: bool = request.config.getoption(name='ignore_certificate', default=False)
        test_name = request.node.name

        capabilities = desired_capabilities(browser, enable_video, test_name, ignore_certificate)

        command_executor = f'{remote_protocol}://{remote_ip}:{remote_port}/wd/hub'
        wd = webdriver.Remote(command_executor=command_executor, desired_capabilities=capabilities)
        session_url = f'{remote_protocol}://{remote_ui}:{remote_ui_port}/#/sessions/{wd.session_id}'
        logging.info('Remote session id: %s', session_url)
        wd.set_window_size(*screen_resolution(device_type))
        wd.implicitly_wait(wait)

        return wd

    return make
