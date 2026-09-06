FROM python:3.11.9-slim-bookworm

WORKDIR /repo

COPY repo/ /repo/
COPY constraints.txt /tmp/constraints.txt

RUN pip install --no-cache-dir -e /repo -c /tmp/constraints.txt \
    && pip install --no-cache-dir -c /tmp/constraints.txt pytest

# Grader mounts tests at runtime (preferably read-only).
CMD ["bash"]
