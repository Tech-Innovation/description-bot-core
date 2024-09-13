from arg_parser import ArgParser
from configuration.config import Config

from clients.streaming import StreamingClient
from processor import Processor


parser = ArgParser()
args = parser.parse()
config_file = args.config_file
config = Config(config_file)

processor = Processor(
    inputs=config.inputs,
    streaming_client=StreamingClient(config.streaming),
    params=config.params,
)
