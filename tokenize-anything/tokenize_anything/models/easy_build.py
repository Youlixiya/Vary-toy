# ------------------------------------------------------------------------
# Copyright (c) 2023-present, BAAI. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------
"""Easy model builder."""

from functools import partial
import pickle
from copy import deepcopy
import torch
from torch import nn
from tokenize_anything.modeling import ConceptProjector
from tokenize_anything.modeling import ImageDecoder
from tokenize_anything.modeling import ImageEncoderViT
from tokenize_anything.modeling import ImageTokenizer
from tokenize_anything.modeling import PromptEncoder
from tokenize_anything.modeling import TextDecoder
from tokenize_anything.modeling import TextTokenizer


def get_device(device_index):
    """Create an available device object."""
    if torch.cuda.is_available():
        return torch.device("cuda", device_index)
    return torch.device("cpu")


def load_weights(module, weights_file, strict=True):
    """Load a weights file."""
    if not weights_file:
        return
    if weights_file.endswith(".pkl"):
        with open(weights_file, "rb") as f:
            state_dict = pickle.load(f)
            for k, v in state_dict.items():
                state_dict[k] = torch.as_tensor(v)
    else:
        state_dict = torch.load(weights_file)
    module.load_state_dict(state_dict, strict=strict)


def vit_encoder(depth, embed_dim, num_heads, out_dim, image_size):
    """Build an image encoder with ViT."""
    return ImageEncoderViT(
        depth=depth,
        embed_dim=embed_dim,
        num_heads=num_heads,
        mlp_ratio=4,
        patch_size=16,
        window_size=16,
        image_size=image_size,
        out_dim=out_dim,
    )

def convert_syncbn_to_bn(model):
    """
    Convert nn.SyncBatchNorm to nn.BatchNorm in the given model.

    Args:
    - model (nn.Module): The input model with nn.SyncBatchNorm layers.

    Returns:
    - nn.Module: A new model with nn.BatchNorm layers replacing nn.SyncBatchNorm.
    """
    new_model = deepcopy(model)

    for name, module in model.named_children():
        if isinstance(module, nn.SyncBatchNorm):
            # Create equivalent BatchNorm layer
            bn_module = nn.BatchNorm2d(module.num_features, eps=module.eps, momentum=module.momentum, affine=module.affine)

            # Transfer running statistics
            bn_module.running_mean = module.running_mean.clone()
            bn_module.running_var = module.running_var.clone()

            # Transfer learnable parameters if applicable
            if module.affine:
                bn_module.weight.data = module.weight.data.clone()
                bn_module.bias.data = module.bias.data.clone()

            new_model.add_module(name, bn_module)
        else:
            # Recursively apply the function to sub-modules
            new_model.add_module(name, convert_syncbn_to_bn(module))
    del model
    torch.cuda.empty_cache()

    return new_model
def image_tokenizer(image_encoder, checkpoint=None, device=0, dtype="float16", **kwargs):
    """Build an image tokenizer."""
    image_size = kwargs.get("image_size", 1024)
    prompt_embed_dim = kwargs.get("prompt_embed_dim", 256)
    sem_embed_dim = kwargs.get("sem_embed_dim", 1024)
    text_embed_dim = kwargs.get("text_embed_dim", 512)
    text_decoder_depth = kwargs.get("text_decoder_depth", 12)
    text_seq_len = kwargs.get("text_seq_len", 100)
    text_tokenizer = TextTokenizer()
    model = ImageTokenizer(
        image_encoder=image_encoder(out_dim=prompt_embed_dim, image_size=image_size),
        prompt_encoder=PromptEncoder(embed_dim=prompt_embed_dim, image_size=image_size),
        image_decoder=ImageDecoder(
            depth=2,
            embed_dim=prompt_embed_dim,
            num_heads=prompt_embed_dim // 32,
            num_mask_tokens=4,
            sem_embed_dim=sem_embed_dim,
        ),
        text_tokenizer=text_tokenizer,
        concept_projector=ConceptProjector(),
        text_decoder=TextDecoder(
            depth=text_decoder_depth,
            embed_dim=text_embed_dim,
            num_heads=text_embed_dim // 64,
            mlp_ratio=4,
            prompt_embed_dim=prompt_embed_dim,
            max_seq_len=text_seq_len,
            vocab_size=text_tokenizer.n_words,
        ),
    )
    load_weights(model, checkpoint)
    model = model.to(device=get_device(device))
    model = model.eval() if not kwargs.get("training", False) else model
    model = model.half() if dtype == "float16" else model
    model = model.bfloat16() if dtype == "bfloat16" else model
    model = model.float() if dtype == "float32" else model
    return convert_syncbn_to_bn(model)


vit_b_encoder = partial(vit_encoder, depth=12, embed_dim=768, num_heads=12)
vit_l_encoder = partial(vit_encoder, depth=24, embed_dim=1024, num_heads=16)

model_registry = {
    "tap_vit_b": partial(image_tokenizer, image_encoder=vit_b_encoder),
    "tap_vit_l": partial(image_tokenizer, image_encoder=vit_l_encoder),
}
