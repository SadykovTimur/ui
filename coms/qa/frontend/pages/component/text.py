from . import Component, ComponentWrapper

__all__ = ['Text']


class TextWrapper(ComponentWrapper):
    def text(self) -> str:
        return self._el.text


class Text(Component):
    def __get__(self, instance, owner) -> str:
        return TextWrapper(instance.app, self.find(instance), self._locator).text()  # type: ignore[arg-type]
