---
title: Fine-tuning & LoRA
description: Adapt pre-trained models to your data — OpenAI fine-tuning, LoRA, QLoRA and PEFT
---

# Fine-tuning & LoRA <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>🤖 AI Track · Level 5</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="llm-apis/">LLM APIs</a>, PyTorch basics</span>
  </div>
</div>

---

## When to fine-tune vs prompt engineering

| Approach | Best for | Cost |
|---|---|---|
| **Prompt engineering** | Most tasks, quick iteration | Low (API calls) |
| **RAG** | Grounding in your data | Medium |
| **Fine-tuning** | Specific style/format, domain expertise | High (compute) |
| **LoRA** | Efficient fine-tuning with limited GPU | Medium |

Fine-tune when: consistent output format, domain-specific jargon, reducing prompt size, improving latency.

---

## OpenAI fine-tuning

```python
from openai import OpenAI
import json

client = OpenAI()

# Step 1: Prepare training data (JSONL format)
training_data = [
    {"messages": [
        {"role": "system", "content": "You are a Python code reviewer."},
        {"role": "user", "content": "Review: def f(x): return x*2"},
        {"role": "assistant", "content": "Score: 3/10. Issues: No docstring, single-char variable name, no type hints."}
    ]},
    {"messages": [
        {"role": "system", "content": "You are a Python code reviewer."},
        {"role": "user", "content": "Review: def calculate_area(radius: float) -> float:\n    \"\"\"Calculate circle area.\"\"\"\n    return 3.14159 * radius ** 2"},
        {"role": "assistant", "content": "Score: 8/10. Good: Clear name, docstring, type hints. Suggestion: Use math.pi instead of hardcoded value."}
    ]},
    # ... 50-100+ examples for good results
]

# Save as JSONL
with open("training_data.jsonl", "w") as f:
    for entry in training_data:
        f.write(json.dumps(entry) + "\n")

# Step 2: Upload file
file = client.files.create(file=open("training_data.jsonl", "rb"), purpose="fine-tune")

# Step 3: Create fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file=file.id,
    model="gpt-4o-mini-2024-07-18",
    hyperparameters={"n_epochs": 3},
)
print(f"Job ID: {job.id}")

# Step 4: Monitor
while True:
    status = client.fine_tuning.jobs.retrieve(job.id)
    print(f"Status: {status.status}")
    if status.status in ("succeeded", "failed"):
        break
    import time; time.sleep(60)

# Step 5: Use the fine-tuned model
response = client.chat.completions.create(
    model=status.fine_tuned_model,   # "ft:gpt-4o-mini:org:custom-name:id"
    messages=[
        {"role": "system", "content": "You are a Python code reviewer."},
        {"role": "user", "content": "Review: x = lambda a,b: a+b"},
    ],
)
print(response.choices[0].message.content)
```

---

## LoRA (Low-Rank Adaptation)

LoRA freezes the base model and trains small adapter matrices — 1000x fewer parameters.

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset
from trl import SFTTrainer

# Load base model
model_name = "meta-llama/Llama-3-8B"
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto", device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Configure LoRA
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,                    # rank (higher = more capacity, more memory)
    lora_alpha=32,           # scaling factor
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],  # which layers to adapt
)

# Apply LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# trainable params: 4,194,304 || all params: 8,030,261,248 || trainable%: 0.05%

# Training
dataset = load_dataset("json", data_files="training_data.jsonl")

training_args = TrainingArguments(
    output_dir="./lora-output",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    logging_steps=10,
    save_steps=100,
    fp16=True,
)

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    tokenizer=tokenizer,
    max_seq_length=512,
)

trainer.train()
model.save_pretrained("./my-lora-adapter")
```

### Load and use the adapter:

```python
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
model = PeftModel.from_pretrained(base_model, "./my-lora-adapter")

# Inference
inputs = tokenizer("Review this Python code:", return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

---

## QLoRA (Quantized LoRA) — fit on consumer GPUs

```python
from transformers import BitsAndBytesConfig
import torch

# 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# Load model in 4-bit (fits 70B model on single 24GB GPU!)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3-70B",
    quantization_config=bnb_config,
    device_map="auto",
)

# Apply LoRA on top of quantized model
model = get_peft_model(model, lora_config)
# Now train with same SFTTrainer as above
```

---

## Practice Exercises

1. **Fine-tune GPT-4o-mini** on 100 examples for a specific task (code review, email writing, etc.).
2. **Train a LoRA adapter** on a local model for domain-specific Q&A.
3. **Compare** fine-tuned model vs base model + few-shot prompting on the same task.
4. **Use QLoRA** to fine-tune a 7B model on a single consumer GPU.
5. **Evaluate fine-tuning quality** — create a test set and measure improvement.
6. **Merge LoRA weights** into the base model for faster inference without adapter overhead.
