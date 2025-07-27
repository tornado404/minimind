from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

# Initialize the tokenizer
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B-Instruct")

# Pass the default decoding hyperparameters of Qwen2.5-7B-Instruct
# max_tokens is for the maximum length for generation.
sampling_params = SamplingParams(temperature=0.7, top_p=0.8, repetition_penalty=1.05, max_tokens=512)

# Input the model name or path. Can be GPTQ or AWQ models.
llm = LLM(model="Qwen/Qwen2.5-3B-Instruct")

# Prepare your prompts
prompt = "Tell me something about large language models."
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": prompt}
]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

# generate outputs
outputs = llm.generate([text], sampling_params)

# Print the outputs.
for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")


#pin_memory=False VLLM_LOGGING_LEVEL=WARNING vllm serve Qwen/Qwen2.5-7B-Instruct --max-model-len=15000 --max-num-seqs=1 --disable-log-requests  --trust-remote-code
#pin_memory=False VLLM_LOGGING_LEVEL=WARNING vllm serve Qwen/Qwen2.5-3B-Instruct --max-model-len=15000 --max-num-seqs=1 --disable-log-requests  --trust-remote-code
#VLLM_LOGGING_LEVEL=WARNING vllm serve internlm/internlm2_5-7b-chat --max-model-len=15000 --max-num-seqs=1 --disable-log-requests --gpu-memory-utilization=0.80 --trust-remote-code