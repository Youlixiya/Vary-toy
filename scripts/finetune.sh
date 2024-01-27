# --model_name_or_path ./ckpts/llava-opt-v1.0-125m-pretrain\ \

deepspeed   --include "localhost:0,2,3,4" vary/train/train_opt.py\
            --deepspeed zero_config/zero3.json\
            --model_name_or_path facebook/opt-125m \
            --conversation_version conversation\
            --freeze_vision_tower True\
            --freeze_lm_model False\
            --use_im_start_end True\
            --bf16 True\
            --per_device_eval_batch_size 1\
            --gradient_accumulation_steps 4\
            --evaluation_strategy "no"\
            --save_strategy "steps"\
            --save_steps 5000\
            --save_total_limit 1\
            --weight_decay 0.\
            --warmup_ratio 0.03\
            --lr_scheduler_type "cosine"\
            --logging_steps 1\
            --tf32 True\
            --model_max_length 4096\
            --gradient_checkpointing True\
            --dataloader_num_workers 4\
            --report_to none\
            --per_device_train_batch_size 4\
            --num_train_epochs 1\
            --learning_rate 5e-5\
            --datasets  llava_v1.5_finetune\
            --output_dir ./ckpts/llava-opt-v1.0-125m