import time

from selenium.common.exceptions import NoSuchElementException

__all__ = [
    'ElementExist',
    'ClassNameExist',
    'InnerTextInElement',
    'ExactTextInElement',
    'AttributeExist',
    'ElementValueIs',
    'AnimationComplete',
    'VisibilityOfAnyElements',
    'ElementToBeClickable',
    'ElementEnabled',
]


class ElementExist:
    """
    An expectation for checking that an element exist.
    @locator - used to find the element
    @returns the WebElement once it exist
    """

    def __init__(self, locator=None) -> None:
        self.locator = locator

    def __call__(self, driver):
        try:
            element = driver.find_element(*self.locator)
        except NoSuchElementException:
            return False

        return element


class ClassNameExist:
    """
    An expectation for checking that an element has a particular css class.
    @element - WebElement
    @locator - used to find the element
    @css_class - used to find class in css
    @returns the WebElement once it has the particular css class
    """

    def __init__(self, element=None, locator=None, css_class=None) -> None:
        self.locator = locator
        self.css_class = css_class
        self.element = element

    def __call__(self, driver):
        if self.element is None:
            self.element = driver.find_element(*self.locator)
        if self.css_class in self.element.get_attribute("class"):
            return self.element

        return False


class InnerTextInElement:
    """
    An expectation for checking that an element has a particular inner text.
    @element - WebElement
    @locator - used to find the element
    @text - used to find class in css
    @returns the WebElement once it has the particular text
    """

    def __init__(self, element=None, locator=None, text=None) -> None:
        self.locator = locator
        self.text = text
        self.element = element

    def __call__(self, driver):
        if self.element is None:
            self.element = driver.find_element(*self.locator)
        if self.text in self.element.text:
            return self.element

        return False


class ExactTextInElement:
    """
    An expectation for checking that an element has a particular exact text.
    @element - WebElement
    @locator - used to find the element
    @text - used to find class in css
    @returns the WebElement once it has the particular text
    """

    def __init__(self, element=None, locator=None, text=None) -> None:
        self.locator = locator
        self.text = text
        self.element = element

    def __call__(self, driver):
        element = self.element if self.element else driver.find_element(*self.locator)

        if self.text == element.text:
            return True

        return False


class AttributeExist:
    """
    An expectation for checking that an element has a particular html attribute.
    @element - WebElement
    @locator - used to find the element
    @attribute - used to find attribute in html
    @returns the WebElement once it has the particular html attribute
    """

    def __init__(self, element=None, locator=None, attribute=None) -> None:
        self.locator = locator
        self.attribute = attribute
        self.element = element

    def __call__(self, driver):
        if self.element is None:
            self.element = driver.find_element(*self.locator)
        elif self.element.get_attribute(self.attribute) is None:
            return False

        return self.element


class ElementValueIs:
    """
    An expectation for checking that an element has a particular html attribute.
    @element - WebElement
    @locator - used to find the element
    @expected_value - used for waiting specific value
    @returns the WebElement once it has the particular html attribute
    """

    def __init__(self, element=None, locator=None, expected_value=None) -> None:
        self.locator = locator
        self.expected_value = expected_value
        self.element = element

    def __call__(self, driver):
        if self.element is None:
            self.element = driver.find_element(*self.locator)
        if self.expected_value in self.element.get_attribute("value"):
            return self.element

        return False


class AnimationComplete:
    """
    An expectation for checking that an element has a particular html attribute.
    @element - WebElement
    @locator - used to find the element
    @duration_type - type of css property to wait for
    """

    def __init__(self, element=None, locator=None, duration_type=None) -> None:
        self.locator = locator
        self.duration_type = duration_type
        self.element = element

    def __call__(self, driver):
        try:
            if self.element is None:
                self.element = driver.find_element(*self.locator)
        except NoSuchElementException as e:
            raise e

        durations = self.element.value_of_css_property(self.duration_type)
        transaction_duration = float(durations.split(',')[0].replace("s", ""))
        time.sleep(transaction_duration)

        return True


class VisibilityOfAnyElements:
    """
    An expectation for checking that an element has a particular html attribute.
    @locators - used to find the elements
    @returns the first visible WebElement
    """

    def __init__(self, locators=None) -> None:
        self.locators = locators

    def __call__(self, driver):
        for locator in self.locators:
            elements = driver.find_elements(*locator)

            if len(elements) > 0:
                if elements[0].is_displayed():
                    return elements[0]

        return False


class ElementToBeClickable:
    """
    An Expectation for checking an element is visible and enabled such that
    you can click it.
    @element - WebElement
    @locator - used to find the element
    """

    def __init__(self, element=None, locator=None) -> None:
        self.element = element
        self.locator = locator

    def __call__(self, driver):
        if self.element is None:
            self.element = driver.find_element(*self.locator)
        if self.element.is_displayed() and self.element.is_enabled():
            return self.element

        return False


class ElementEnabled:
    def __init__(self, locator=None) -> None:
        self.locator = locator

    def __call__(self, driver):
        element = driver.find_element(*self.locator)

        if element.is_enabled():
            return True

        return False
