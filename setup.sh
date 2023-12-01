# Make setup of the environment. Install whisper.cpp and llama.cpp.



pip3 install jax jaxlib pandas tqdm feedparser pyarrow beautifulsoup4 huggingface_hub[cli]

git clone git@github.com:openreview/openreview-py.git ../openreview-py
cd ../openreview-py
pip3 install -e .
cd ../compressor

# Install llama.cpp
git clone git@github.com:ggerganov/llama.cpp.git ../llama.cpp
cd ../llama.cpp
make
# if GPU is available, use this instead. TODO: make a flag for this.
# sudo apt-get install nvidia-cuda-toolkit
# make LLAMA_CUBLAS=1
huggingface-cli download TheBloke/Orca-2-13B-GGUF orca-2-13b.Q8_0.gguf --local-dir ./models --local-dir-use-symlinks False
cd ../compressor



# Install whiisper.cpp
git clone git@github.com:ggerganov/whisper.cpp.git ../whisper.cpp
cd ../whisper.cpp
make

cd ../compressor

