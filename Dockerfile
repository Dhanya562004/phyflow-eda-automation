# PHYFlow Docker Environment for EDA Automation & Custom-Cell Validation
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Install core tools, compilers, Python, Tcl, ngspice, Yosys
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    tcl \
    tcl-dev \
    bash \
    yosys \
    ngspice \
    git \
    make \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3 -m venv /opt/venv

WORKDIR /workspace

# Copy project files
COPY pyproject.toml requirements.txt README.md ./
COPY phyflow/ ./phyflow/
COPY designs/ ./designs/
COPY libs/ ./libs/
COPY scripts/ ./scripts/
COPY configs/ ./configs/
COPY tests/ ./tests/
COPY dashboard/ ./dashboard/

# Install python dependencies and phyflow framework
RUN pip install --upgrade pip && \
    pip install -e .

EXPOSE 8501

CMD ["phyflow", "check-tools"]
