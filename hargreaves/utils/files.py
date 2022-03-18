from os import path


class FileHelper:
    @staticmethod
    def write_file(file_path: str, contents: str, mode='w') -> int:
        with open(file_path, mode=mode) as file:
            output = file.write(contents)
        return output

    @staticmethod
    def read_file_contents(file_path: str):
        if not path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' does not exist!")

        with open(file_path, mode='r') as file:
            contents = file.read()

        return contents
