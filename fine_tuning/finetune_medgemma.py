"""
MedGemma Fine-tuning Script for irAE Detection

Uses LoRA (Low-Rank Adaptation) for efficient fine-tuning on T4 GPU.
This approach allows fine-tuning a 4B parameter model with limited VRAM.
"""

import os
import json
import torch
from typing import Optional
from dataclasses import dataclass

# Training configuration
@dataclass
class FineTuningConfig:
    """Configuration for MedGemma fine-tuning."""
    
    # Model settings
    base_model: str = "google/medgemma-4b-it"
    output_dir: str = "./medgemma-irae-finetuned"
    
    # LoRA settings (efficient fine-tuning)
    lora_r: int = 16  # Rank of the update matrices
    lora_alpha: int = 32  # LoRA scaling factor
    lora_dropout: float = 0.05
    target_modules: list = None  # Will be set in __post_init__
    
    # Training hyperparameters
    num_epochs: int = 3
    batch_size: int = 1  # Small for T4 GPU memory
    gradient_accumulation_steps: int = 4  # Effective batch size = 4
    learning_rate: float = 2e-4
    warmup_ratio: float = 0.1
    max_seq_length: int = 2048
    
    # Memory optimization
    gradient_checkpointing: bool = True
    fp16: bool = True  # Mixed precision for T4
    optim: str = "paged_adamw_8bit"
    
    def __post_init__(self):
        if self.target_modules is None:
            # Target attention layers for LoRA
            self.target_modules = [
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ]


def prepare_dataset(training_file: str = "training_data.jsonl"):
    """Load and prepare the training dataset."""
    from datasets import Dataset
    
    data = []
    with open(training_file, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    
    # Convert to HuggingFace dataset
    def format_for_training(example):
        """Format as chat template."""
        messages = example['messages']
        # Combine into single text for training
        text = f"<start_of_turn>user\n{messages[0]['content']}<end_of_turn>\n"
        text += f"<start_of_turn>model\n{messages[1]['content']}<end_of_turn>"
        return {"text": text}
    
    dataset = Dataset.from_list(data)
    dataset = dataset.map(format_for_training)
    
    return dataset


def setup_model_and_tokenizer(config: FineTuningConfig):
    """Load model with quantization for efficient fine-tuning."""
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    
    # 4-bit quantization config for T4 GPU
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    
    print(f"Loading {config.base_model}...")
    model = AutoModelForCausalLM.from_pretrained(
        config.base_model,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )
    
    tokenizer = AutoTokenizer.from_pretrained(
        config.base_model,
        trust_remote_code=True,
    )
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    # Prepare model for k-bit training
    model = prepare_model_for_kbit_training(model)
    
    # Setup LoRA
    lora_config = LoraConfig(
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=config.target_modules,
        bias="none",
        task_type="CAUSAL_LM",
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    return model, tokenizer


def train(
    config: Optional[FineTuningConfig] = None,
    training_file: str = "training_data.jsonl",
    push_to_hub: bool = False,
    hub_model_id: str = None,
):
    """
    Fine-tune MedGemma on irAE detection data.
    
    Args:
        config: Fine-tuning configuration
        training_file: Path to JSONL training data
        push_to_hub: Whether to push to HuggingFace Hub
        hub_model_id: Model ID for HuggingFace Hub
    """
    from transformers import TrainingArguments
    from trl import SFTTrainer
    
    if config is None:
        config = FineTuningConfig()
    
    # Load dataset
    print("Preparing dataset...")
    dataset = prepare_dataset(training_file)
    print(f"Training on {len(dataset)} examples")
    
    # Load model
    model, tokenizer = setup_model_and_tokenizer(config)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=config.output_dir,
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        warmup_ratio=config.warmup_ratio,
        fp16=config.fp16,
        optim=config.optim,
        logging_steps=10,
        save_strategy="epoch",
        gradient_checkpointing=config.gradient_checkpointing,
        report_to="none",  # Disable wandb for simplicity
        push_to_hub=push_to_hub,
        hub_model_id=hub_model_id,
    )
    
    # Create trainer
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=training_args,
        max_seq_length=config.max_seq_length,
        dataset_text_field="text",
    )
    
    # Train
    print("Starting fine-tuning...")
    trainer.train()
    
    # Save final model
    print(f"Saving model to {config.output_dir}")
    trainer.save_model()
    tokenizer.save_pretrained(config.output_dir)
    
    if push_to_hub:
        print(f"Pushing to HuggingFace Hub: {hub_model_id}")
        trainer.push_to_hub()
    
    return trainer


def merge_and_export(
    adapter_path: str,
    output_path: str,
    push_to_hub: bool = False,
    hub_model_id: str = None,
):
    """
    Merge LoRA weights with base model and export.
    
    This creates a standalone model that doesn't need the PEFT library.
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    
    print("Loading base model...")
    base_model = AutoModelForCausalLM.from_pretrained(
        "google/medgemma-4b-it",
        torch_dtype=torch.float16,
        device_map="auto",
    )
    
    print("Loading LoRA adapter...")
    model = PeftModel.from_pretrained(base_model, adapter_path)
    
    print("Merging weights...")
    model = model.merge_and_unload()
    
    print(f"Saving merged model to {output_path}")
    model.save_pretrained(output_path)
    
    tokenizer = AutoTokenizer.from_pretrained("google/medgemma-4b-it")
    tokenizer.save_pretrained(output_path)
    
    if push_to_hub:
        print(f"Pushing merged model to Hub: {hub_model_id}")
        model.push_to_hub(hub_model_id)
        tokenizer.push_to_hub(hub_model_id)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fine-tune MedGemma for irAE detection")
    parser.add_argument("--training-file", default="training_data.jsonl", help="Training data file")
    parser.add_argument("--output-dir", default="./medgemma-irae-finetuned", help="Output directory")
    parser.add_argument("--epochs", type=int, default=3, help="Number of epochs")
    parser.add_argument("--push-to-hub", action="store_true", help="Push to HuggingFace Hub")
    parser.add_argument("--hub-model-id", default=None, help="HuggingFace model ID")
    
    args = parser.parse_args()
    
    config = FineTuningConfig(
        output_dir=args.output_dir,
        num_epochs=args.epochs,
    )
    
    train(
        config=config,
        training_file=args.training_file,
        push_to_hub=args.push_to_hub,
        hub_model_id=args.hub_model_id,
    )
