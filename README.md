# Compressor
Because we do not have time to read everything.

![](compressor.jpg)

Compressor is an LLM-based scientific literature / talks summarisation project started by [yobibyte](https://twitter.com/y0b1byte).
It is heavily relying on [llama.cpp](https://github.com/ggerganov/llama.cpp) and [HuggingFace](https://huggingface.co/) models.

Compressor is under active development, you are entering unchartered waters when using it.

I will be happy to any feedback / feature requests, and, please, send PRs.

## Usecases

1. Get arxiv link, summarise.

2. Get all papers submitted to Arxiv at a date (usually published today). Summarise each.

3. Get a pdf, summarise. Not yet implemented.

4. Get an audio of a talk, get a script, summarise. WIP.

5. Summarise all papers accepted to some conference on OpenReview. 

6. Summarise all talks of a particular conference. Future plans.

## Architecture

Crawler -> Compressor -> Reporter

## Big TODOs

* Current version does summarisation based on abstracts only. Add full-text support.
* Better exception handling. Right now, postprocessing LLM outputs might fail from time to time requiring rerunning the compressor.
