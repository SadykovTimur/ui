import allure

from . import Component, ComponentWrapper

__all__ = ['TextField']


class TextFieldWrapper(ComponentWrapper):
    def send_keys(self, text: str, clear: bool = True) -> None:
        if clear:
            with allure.step(f'Clearing {self}'):
                self._el.clear()

        with allure.step(f'Sending {text} to {self}'):
            self._el.send_keys(text)


class TextField(Component):
    def __get__(self, instance, owner) -> TextFieldWrapper:
        return TextFieldWrapper(instance.app, self.find(instance), self._locator)  # type: ignore[arg-type]

    def __set__(self, instance, value) -> None:
        if value is None:
            return

        value = str(value).strip()

        if not value:
            return

        self.__get__(instance, instance.__class__).send_keys(value)
