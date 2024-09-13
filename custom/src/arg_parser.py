import argparse


class ArgParser:
    def __init__(self, show_warnings=True):
        self.show_warnings = show_warnings
        self.parser = argparse.ArgumentParser(description="Process some integers.")

        self.parser.add_argument(
            "--config_file",
            type=str,
            help="Config file path",
        )

    def parse(self):
        return self.parser.parse_args()
