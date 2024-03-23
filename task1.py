import sys
import asyncio

from aiopath import Path
from aioshutil import copyfile
from loguru import logger


class DirectoryDoesNotExist(Exception): ...


class ArgumentParser:
    path: Path
    destination: Path

    @classmethod
    async def init(cls) -> "ArgumentParser":
        parser = ArgumentParser()
        argument_amount = len(sys.argv) - 1
        if argument_amount == 0:
            parser.path = await Path.cwd()
            parser.destination = parser.path / "dist"
        elif argument_amount == 1:
            parser.path = Path(sys.argv[1])
            await parser.check_path(path=parser.path)
            parser.destination = parser.path / "dist"
        elif argument_amount == 2:
            parser.path = Path(sys.argv[1])
            await parser.check_path(path=parser.path)
            parser.destination = Path(sys.argv[2])
            await parser.check_path(parser.destination)
        return parser

    @staticmethod
    async def check_path(path: Path):
        if not await path.is_dir():
            logger.error(DirectoryDoesNotExist(f"Directory {path} does not exist"))
            sys.exit(1)


class Copyfier:
    _path: Path
    _destination: Path
    __absolute_paths_of_copying_files: list[Path]
    __inner_paths: dict[str, Path]

    @classmethod
    async def init(cls, path: Path, destination: Path) -> "Copyfier":
        cofyfier = Copyfier()
        cofyfier._path = await path.resolve()
        cofyfier._destination = await destination.resolve()
        cofyfier.__absolute_paths_of_copying_files = []
        cofyfier.__inner_paths = {}
        return cofyfier

    async def __get_inner_path_for_extension(self, extension: str) -> Path:
        if extension not in self.__inner_paths.keys():
            self.__inner_paths[extension] = self._destination / extension
            await self.__inner_paths[extension].mkdir(parents=True, exist_ok=True)
        return self.__inner_paths[extension]

    @staticmethod
    def __get_file_extension(filename: str) -> str:
        if "." not in filename:
            return "txt"
        return filename[filename.rfind(".") + 1 :]

    async def __read_folder(self, path: Path = None) -> None:
        if not path:
            path = self._path
        async for file in path.iterdir():
            if file._path == self._destination:
                continue
            if await file.is_file():
                self.__absolute_paths_of_copying_files.append(file)
            else:
                await self.__read_folder(file)

    async def execute(self) -> None:
        await self._destination.mkdir(parents=True, exist_ok=True)
        await self.__read_folder()
        for path in self.__absolute_paths_of_copying_files:
            filename = path.name
            destination = await self.__get_inner_path_for_extension(
                extension=self.__get_file_extension(filename=filename)
            )
            await copyfile(path, destination / filename)


async def main():
    logger.remove()
    log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <blue>{level}</blue> | {message}"
    logger.add(sys.stdout, format=log_format, colorize=True, level="ERROR")
    logger.add("file.log", format=log_format, colorize=True, level="ERROR")

    parser = await ArgumentParser.init()
    copyfier = await Copyfier.init(path=parser.path, destination=parser.destination)
    await copyfier.execute()


if __name__ == "__main__":
    asyncio.run(main())
