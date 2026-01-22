from .pixel import PixelRenderer
from .block import BlockRenderer
from .ascii import ASCIIRenderer

class RendererRegistry:
    _renderers = {}

    @classmethod
    def register(cls, name: str, renderer_class):
        cls._renderers[name] = renderer_class

    @classmethod
    def get_renderer(cls, name: str):
        return cls._renderers.get(name, cls._renderers["pixel"])

    @classmethod
    def list_renderers(cls):
        return list(cls._renderers.keys())


# Auto-register all renderers
RendererRegistry.register("pixel", PixelRenderer)
RendererRegistry.register("block", BlockRenderer)
RendererRegistry.register("ascii", ASCIIRenderer)


def get_renderer(name: str):
    return RendererRegistry.get_renderer(name)
