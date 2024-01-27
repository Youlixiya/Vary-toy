CONTROLLER_HEART_BEAT_EXPIRATION = 30
WORKER_HEART_BEAT_INTERVAL = 15

LOGDIR = "log"

IGNORE_INDEX = -100
# DEFAULT_PAD_TOKEN = "[PAD]"

DEFAULT_PAD_TOKEN = "<|endoftext|>"
DEFAULT_EOS_TOKEN = "</s>"
DEFAULT_BOS_TOKEN = "</s>"
DEFAULT_UNK_TOKEN = "<unk>"
DEFAULT_IMAGE_TOKEN = "<image>"
DEFAULT_BOX_TOKEN = "<box>"

DEFAULT_IMAGE_PATCH_TOKEN = '<imgpad>'

DEFAULT_IM_START_TOKEN = '<img>'
DEFAULT_IM_END_TOKEN = '</img>'


ROOT_PATH = '/data/public/ucaswei/data/'

CONVERSATION_DATA = {

    # pair 4m
    'laion-coco-4m': {
        'images': '',
        'annotations': '',
    }, 

    'llava_v1.5_pretrain': {
        'images': "data/LLaVA-Pretrain/llava_images/",
        'annotations': "data/LLaVA-Pretrain/blip_laion_cc_sbu_558k.json",
    },
    'llava_v1.5_finetune': {
        'images': "data/",
        'annotations': "data/LLaVA-v1.5/llava_v1_5_mix665k.json",
    },
    'refer_coco': {
        'images': "data/refcocos/images/tran2014/",
        'annotations': "data/refcocos/REC_ref3_train.json",
    },
    'pdf': {
        'images': "",
        'annotations': "",
    },

    'docvqa_train': {
        'images': "",
        'annotations': "",
    },

    'chartqa_train': {
        'images': "",
        'annotations': "",
    },



}