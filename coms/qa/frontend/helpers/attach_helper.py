import http
from typing import Optional

import allure
import requests
from _pytest.fixtures import FixtureRequest
from allure_commons.types import AttachmentType
from selenium.webdriver.remote.webelement import WebElement

from coms.qa.core.helpers import wait_for
from coms.qa.fixtures.application import Application


def screenshot_attach(
    app: Application,
    name: str,
    attachment_type: AttachmentType = allure.attachment_type.PNG,
    webelement: Optional[WebElement] = None,
) -> None:
    if webelement:
        screen = webelement.screenshot_as_png
    else:
        screen = app.driver.get_screenshot_as_png()

    allure.attach(
        name=name,
        body=screen,
        attachment_type=attachment_type,
    )


def video_attach(
    app: Application, request: FixtureRequest, name: str, attachment_type: AttachmentType = allure.attachment_type.MP4
) -> None:
    if request.config.option.enable_video:
        session_id = app.driver.session_id

        app.driver.quit()

        remote_ip = request.config.option.remote_ip
        remote_port = request.config.option.remote_port

        def condition() -> bytes:
            path = f'http://{remote_ip}:{remote_port}/video/{session_id}.mp4'
            r = requests.get(path)

            assert r.status_code == http.HTTPStatus.OK

            return r.content

        response = wait_for(condition, msg='Wait for video file')
        allure.attach(
            name=f'{name}.mp4',
            body=response,
            attachment_type=attachment_type,
        )
