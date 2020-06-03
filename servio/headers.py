from collections import defaultdict
import typing

HeadersDict = typing.Dict[str, typing.List[str]]
HeadersGenerator = typing.Generator[typing.Tuple[str, str], None, None]


class Headers:
    def __init__(self) -> None:
        self._headers: typing.Mapping[str, list] = defaultdict(list)

    def __getitem__(self, name: str) -> typing.List[str]:
        return self._headers[name.lower()]

    def add(self, name: str, value: str) -> None:
        self._headers[name.lower()].append(value)

    def get_all(self, name: str) -> typing.List[str]:
        return self.__getitem__(name)

    def get(
        self, name: str, default: typing.Optional[str] = None
    ) -> typing.Optional[str]:
        try:
            return self.get_all(name)[-1]
        except IndexError:
            return default

    def __iter__(self) -> HeadersGenerator:
        for name, values in self._headers.items():
            for value in values:
                yield name, value
