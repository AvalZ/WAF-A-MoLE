import os


def type_check(object_to_check, type_to_check, param_name):
    if not isinstance(object_to_check, type_to_check):
        raise TypeError(
            "{} is not {} but {}".format(
                param_name, type_to_check, type(object_to_check)
            )
        )


def file_exists(filepath: str):
    if not os.path.isfile(filepath):
        raise FileNotFoundError("{} not exists".format(filepath))
