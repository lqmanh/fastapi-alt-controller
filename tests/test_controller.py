from typing import Any, ClassVar

from fastapi import APIRouter, Depends, FastAPI
from fastapi.testclient import TestClient
from fastapi_module import controller


def test_controller() -> None:
    router = APIRouter()

    def dependency() -> int:
        return 1

    @controller(router)
    class TestController:
        cx: ClassVar[int] = 1
        cy: ClassVar[int]
        x: int = Depends(dependency)

        def __init__(self, z: int = Depends(dependency)):
            self.y = 1
            self.z = z

        @router.get("/", response_model=int)
        def f(self) -> int:
            return self.cx + self.x + self.y + self.z

        @router.get("/classvar", response_model=bool)
        def g(self) -> bool:
            return hasattr(self, "cy")

    client = TestClient(router)

    assert client.get("/").text == "4"
    assert client.get("/classvar").text == "false"


def test_method_order_preserved() -> None:
    router = APIRouter()

    @controller(router)
    class TestController:
        @router.get("/test")
        def get_test(self) -> int:
            return 1

        @router.get("/{item}")
        def get_item(self, item: str) -> int:  # alphabetically before `get_test`
            return 2

    client = TestClient(router)

    assert client.get("/test").text == "1"
    assert client.get("/other").text == "2"


def test_multiple_decorators() -> None:
    router = APIRouter()

    @controller(router)
    class TestController:
        @router.get("/items/?")
        @router.get("/items/{item_path:path}")
        @router.get("/database/{item_path:path}")
        def root(self, item_path: str = None, item_query: str = None) -> Any:
            if item_path:
                return {"item_path": item_path}
            if item_query:
                return {"item_query": item_query}
            return []

    client = TestClient(router)

    assert client.get("/items").json() == []
    assert client.get("/items/1").json() == {"item_path": "1"}
    assert client.get("/database/abc").json() == {"item_path": "abc"}
