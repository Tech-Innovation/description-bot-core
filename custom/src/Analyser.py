import re

import torch
from PIL import Image

from llava.constants import (
    DEFAULT_IM_END_TOKEN,
    DEFAULT_IM_START_TOKEN,
    DEFAULT_IMAGE_TOKEN,
    IMAGE_PLACEHOLDER,
    IMAGE_TOKEN_INDEX,
)
from llava.conversation import conv_templates, SeparatorStyle
from llava.mm_utils import (
    get_model_name_from_path,
    process_images,
    tokenizer_image_token,
    KeywordsStoppingCriteria,
    get_frame_from_vcap,
)
from llava.model.builder import load_pretrained_model


class Analyser:
    # CONVERSATION_CHOICE = (
    #     "auto",
    #     "default",
    #     "hermes-2",
    #     "llama_3",
    #     "v0",
    #     "v1",
    #     "vicuna_v1",
    #     "vicuna_v1_nosys",
    #     "llama_2",
    #     "mistral",
    #     "plain",
    #     "v0_plain",
    #     "llava_v0",
    #     "v0_mmtag",
    #     "llava_v1",
    #     "v1_mmtag",
    #     "llava_llama_2",
    #     "mpt",
    # )

    DEFAULT_CONVERSATION_TYPE = "llava_v0"

    def __init__(self, model, query, conversation_mode=DEFAULT_CONVERSATION_TYPE) -> None:
        self.model_path = model
        self.query = query
        self.image_token_se = DEFAULT_IM_START_TOKEN + DEFAULT_IMAGE_TOKEN + DEFAULT_IM_END_TOKEN
        self.conversation_mode = conversation_mode
        self.temperature = 0.2
        self.num_beams = 1
        self.max_new_tokens = 512
        self.top_p = None
        self.load_pretrained_model()

    def load_pretrained_model(self):
        self.model_name = get_model_name_from_path(self.model_path)
        self.tokenizer, self.model, self.image_processor, _ = load_pretrained_model(self.model_path, self.model_name)

    def set_conversation_mode(self):
        if "llama-2" in self.model_name.lower():
            conversation_mode = "llava_llama_2"
        elif "v1" in self.model_name.lower():
            conversation_mode = "llava_v1"
        elif "mpt" in self.model_name.lower():
            conversation_mode = "mpt"
        else:
            conversation_mode = "llava_v0"

        if self.conversation_mode is not None and conversation_mode != self.conversation_mode:
            print(
                f"[WARNING] the auto inferred conversation mode is {conversation_mode}, while DEFAULT_CONVERSATION_TYPE is {self.conversation_mode}"
            )
        else:
            self.conversation_mode = conversation_mode

    def set_conversation(self):
        self.set_conversation_mode()

        self.conversation = conv_templates[self.conversation_mode].copy()
        self.conversation.append_message(self.conversation.roles[0], self.query)
        self.conversation.append_message(self.conversation.roles[1], None)
        self.prompt = self.conversation.get_prompt()

    def handle_image_token_in_query(self):
        if IMAGE_PLACEHOLDER in self.query:
            if self.model.config.mm_use_im_start_end:
                self.query = re.sub(IMAGE_PLACEHOLDER, self.image_token_se, self.query)
            else:
                self.query = re.sub(IMAGE_PLACEHOLDER, DEFAULT_IMAGE_TOKEN, self.query)
        else:
            if DEFAULT_IMAGE_TOKEN not in self.query:
                print("no <image> tag found in input. Automatically append one at the beginning of text.")
                # do not repeatively append the prompt.
                if self.model.config.mm_use_im_start_end:
                    self.query = (self.image_token_se + "\n") + self.query
                else:
                    self.query = (DEFAULT_IMAGE_TOKEN + "\n") + self.query

    def analyse(self, frame):
        self.handle_image_token_in_query()
        self.set_conversation()

        working_frame = frame.copy()
        working_frame = Image.fromarray(working_frame)
        image_tensor = process_images([working_frame], self.image_processor, self.model.config).to(
            self.model.device, dtype=torch.float16
        )
        input_ids = (
            tokenizer_image_token(
                self.prompt,
                self.tokenizer,
                IMAGE_TOKEN_INDEX,
                return_tensors="pt",
            )
            .unsqueeze(0)
            .cuda()
        )
        stop_str = (
            self.conversation.sep if self.conversation.sep_style != SeparatorStyle.TWO else self.conversation.sep2
        )
        keywords = [stop_str]
        stopping_criteria = KeywordsStoppingCriteria(keywords, self.tokenizer, input_ids)

        with torch.inference_mode():
            output_ids = self.model.generate(
                input_ids,
                images=[
                    image_tensor,
                ],
                do_sample=True if self.temperature > 0 else False,
                temperature=self.temperature,
                top_p=self.top_p,
                num_beams=self.num_beams,
                max_new_tokens=self.max_new_tokens,
                use_cache=True,
                stopping_criteria=[stopping_criteria],
            )

        outputs = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0]
        outputs = outputs.strip()
        if outputs.endswith(stop_str):
            outputs = outputs[: -len(stop_str)]
        outputs = outputs.strip()
        return outputs
