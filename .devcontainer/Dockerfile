FROM mcr.microsoft.com/devcontainers/python:3.12

# LaTeX (minimal, for manuscript compilation)
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
       texlive-latex-base \
       texlive-latex-recommended \
       texlive-latex-extra \
       texlive-fonts-recommended \
       texlive-bibtex-extra \
       biber \
       latexmk \
    && rm -rf /var/lib/apt/lists/*

# Python packages for the research workflow
RUN pip install --no-cache-dir \
    marimo \
    mcp \
    torch \
    transformers \
    sentence-transformers \
    headroom-ai \
    sumy \
    nltk \
    llmlingua \
    numpy \
    matplotlib

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt_tab', quiet=True); nltk.download('punkt', quiet=True)"

# Set up workspace
WORKDIR /workspace
COPY . /workspace/

# Default shell
SHELL ["/bin/zsh", "-c"]
