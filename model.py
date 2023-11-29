# Use this as a library to get model predictions
import subprocess
import os

TMP_FNAME = "prompt.txt"
LLAMA_CPP_PATH = "../llama.cpp"


class CompressorModel:
    def __init__(self, name):
        self._name = name

    def get_prompt(self, input: str):
        return input

    def postprocess(self, output: str):
        return output

    def run_model(self, payload: str):
        # Communicating via file is the easiest option.
        # I had some problems with quote escaping.
        with open(TMP_FNAME, "w") as f:
            f.write(payload)

        command = f"{LLAMA_CPP_PATH}/main -m {LLAMA_CPP_PATH}/models/{self._name} --color -c 2048 --temp 0.7 --repeat_penalty 1.1 -n -2 --ctx-size 4096 -e -f {TMP_FNAME}"
        with subprocess.Popen(
            command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as proc:
            out = proc.stdout.read().decode("utf-8")
        os.remove(TMP_FNAME)
        return out

    def go(self, input: str):
        raw_out = self.run_model(self.get_prompt(input))
        return self.postprocess(raw_out)


class OrcaModel(CompressorModel):
    def __init__(self):
        super().__init__("orca-2-13b.Q8_0.gguf")

    def get_prompt(self, input: str):
        return f"### System:\nYou are a scientist and a great communicator. You read papers and summarize them concisely using clear language.\n\n### User:\nSummarize the following paragraph of text in one sentence.\n\n### Input:\n{input}\n\n### Response:\n"

    def postprocess(self, output: str):
        return output.strip().split("### Response:\n")[1]


class MistralModel(CompressorModel):
    def __init__(self):
        super().__init__("openinstruct-mistral-7b.Q6_K.gguf")

    def get_prompt(self, input: str):
        return f"Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\nSummarise the following paragraph in one sentence. Very concise, it should fit one tweet.\n{input}\n\n### Response:"

    def postprocess(self, output):
        return output.strip().split("### Response:")[1]


MODEL_MENU = {"orca": OrcaModel, "mistral7b": MistralModel}
