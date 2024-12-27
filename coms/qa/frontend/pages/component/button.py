import allure

from . import Component, ComponentWrapper

__all__ = ['Button', 'ButtonWrapper']


class ButtonWrapper(ComponentWrapper):
    def click(self) -> None:
        self.wait_for_clickability()

        with allure.step(f'Clicking on {self}'):
            self._el.click()


class Button(Component):
    def __get__(self, instance, owner) -> ButtonWrapper:
        return ButtonWrapper(instance.app, self.find(instance), self._locator)  # type: ignore[arg-type]
