import os
import sys
import asyncio
from concurrent.futures import ThreadPoolExecutor


class AlreadyExists(Exception): ...


class DirectoryDoesNotExist(Exception): ...


class ArgumentParser:
    path: str
    destination: str

    def __init__(self):
        argument_amount = len(sys.argv) - 1
        if argument_amount == 0:
            self.path = os.getcwd()
            self.destination = os.path.join(self.path, "dist")
        elif argument_amount == 1:
            self.path = sys.argv[1]
            self.check_path(path=self.path)
            self.destination = os.path.join(self.path, "dist")
        elif argument_amount == 2:
            self.path = sys.argv[1]
            self.check_path(path=self.path)
            self.destination = sys.argv[2]

    def check_path(self, path: str):
        if not os.path.exists(path):
            raise DirectoryDoesNotExist(f"Directory {path} does not exist")


class Copyfier:
    def __init__(self, path: str, destination: str) -> None:
        self._path: str = self.__get_clean_path(path=path)
        self._destination: str = self.__get_clean_path(path=destination)
        self.__absolute_paths_of_copying_files: list[str] = []
        self.__inner_paths: dict[str, str] = {}

    def __get_inner_path_for_extention(self, extension: str) -> str:
        if extension not in self.__inner_paths.keys():
            self.__inner_paths[extension] = self.__get_clean_path(
                f"{self._destination}/{extension}"
            )
            os.makedirs(name=self.__inner_paths[extension])
        return self.__inner_paths[extension]

    def __get_clean_path(self, path: str) -> str:
        if path[-1] == "/":
            path = path[:-1]
        return path

    def __get_file_extension(self, filename: str) -> str:
        if "." not in filename:
            return "txt"
        filename = self.__get_clean_path(path=filename)
        return filename[filename.rfind(".") + 1 :]

    def __read_folder(self, path: str) -> None:
        path = self.__get_clean_path(path)
        for file in os.listdir(path=path):
            file_path = f"{path}/{file}"
            if os.path.isfile(path=file_path):
                self.__absolute_paths_of_copying_files.append(file_path)
            else:
                self.__read_folder(path=file_path)

    async def __aget_files_of(self, path: str) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(ThreadPoolExecutor(), self.__read_folder, path)

    def __get_filename(self, path: str) -> str:
        path = self.__get_clean_path(path=path)
        if "/" not in path:
            return path
        return path[path.rfind("/") + 1 :]

    async def __copy_file(self, path: str, destination: str, filename: str):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            ThreadPoolExecutor(), os.popen, f"cp {path} {destination}/{filename}"
        )

    async def execute(self) -> None:
        try:
            if os.path.exists(path=self._destination):
                raise AlreadyExists(f"Directory {self._destination} already exists")
            os.makedirs(name=self._destination)
            await self.__aget_files_of(path=self._path)
            for path in self.__absolute_paths_of_copying_files:
                filename = self.__get_filename(path=path)
                destination = self.__get_inner_path_for_extention(
                    extension=self.__get_file_extension(filename=filename)
                )
                await self.__copy_file(
                    path=path, destination=destination, filename=filename
                )
        except Exception as e:
            print(e)


if __name__ == "__main__":
    try:
        argument_parser = ArgumentParser()
    except Exception as e:
        print(e)
        sys.exit()

    copyfier = Copyfier(
        path=argument_parser.path, destination=argument_parser.destination
    )

    asyncio.run(copyfier.execute())
