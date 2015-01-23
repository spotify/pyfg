import ast
import logging


def string_to_dict(string):
    if string is not None:
        try:
            return ast.literal_eval(string)
        except ValueError:
            return string
        except SyntaxError:
            return string
    else:
        return None


def set_logging(log_path, log_level):
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    if log_path is not None:
        handler = logging.FileHandler(log_path)
    else:
        handler = logging.NullHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.getLevelName(log_level))
    logger.name = 'fortios:'
    logger.addHandler(handler)
    return logger


def save_text_generator_to_file(file_name, text):
    with open(file_name, "w") as text_file:
        for line in text:
            text_file.write('%s\n' % line)