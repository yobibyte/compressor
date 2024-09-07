# Use this as a library to get model predictions
import subprocess
import os

TMP_FNAME = "prompt.txt"
LLAMA_CPP_PATH = "../llama.cpp"


class CompressorModel:
    def __init__(self, name):
        self._name = name
        # TODO: make this configurable.
        self._context_size = 4096

    def get_prompt(self, input: str):
        return input

    def preprocess(self, input: str):
        # To save on compute / debug. Temporarily we crop the inputs. Not ideal.
        # TODO: ^^^ think about the above. Maybe summarise each context size and summaries all the summaries.
        input = input.split()[: self._context_size // 2]
        input = " ".join(input)
        return input

    def postprocess(self, output: str):
        return output

    def run_model(self, payload: str):
        # Communicating via file is the easiest option.
        # I had some problems with quote escaping.
        # TODO think about this more
        with open(TMP_FNAME, "w") as f:
            f.write(payload)

        command = f"{LLAMA_CPP_PATH}/main -m {LLAMA_CPP_PATH}/models/{self._name} --color --temp 0.7 --repeat_penalty 1.1 -n -2 --ctx-size {self._context_size} -e -f {TMP_FNAME} -ngl 20"
        with subprocess.Popen(
            command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as proc:
            out = proc.stdout.read().decode("utf-8")
        os.remove(TMP_FNAME)
        return out

    def go(self, input: str, full_summary: bool = False):
        raw_out = self.run_model(self.get_prompt(input, full_summary=full_summary))
        return self.postprocess(raw_out)


class OrcaModel(CompressorModel):
    def __init__(self):
        super().__init__("orca-2-13b.Q8_0.gguf")

    def get_prompt(self, input: str, full_summary: bool = False):
        input = self.preprocess(input)
        return f"### System:\nYou are a scientist and a great communicator. You read papers and summarize them concisely using clear language.\n\n### User:\nSummarize the following text in one {'paragraph' if full_summary else 'sentence'}.\n\n### Input:\n{input}\n\n### Response:\n"

    def postprocess(self, output: str):
        return output.strip().split("### Response:\n")[1]


class MistralModel(CompressorModel):
    def __init__(self):
        super().__init__("openinstruct-mistral-7b.Q6_K.gguf")

    def get_prompt(self, input: str, full_summary: bool = False):
        input = self.preprocess(input)
        return f"Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\nSummarise the following text in one sentence. Very concise, it should fit one {'paragraph' if full_summary else 'sentence'}.\n{input}\n\n### Response:"

    def postprocess(self, output):
        return output.strip().split("### Response:")[1]


MODEL_MENU = {"orca": OrcaModel, "mistral7b": MistralModel}
