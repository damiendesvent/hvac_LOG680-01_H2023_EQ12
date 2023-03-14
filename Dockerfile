# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-alpine 
# ~18 mb

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /src
COPY . /src

# Creates a non-root user with an explicit UID and adds permission to access the /src folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /src
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "src/main.py"]



# # For more information, please refer to https://aka.ms/vscode-docker-python
# FROM python:3.10-slim as build

# # Keeps Python from generating .pyc files in the container
# ENV PYTHONDONTWRITEBYTECODE=1

# # Turns off buffering for easier container logging
# ENV PYTHONUNBUFFERED=1

# WORKDIR /src

# RUN python -m venv .venv && .venv/bin/pip install --no-cache-dir -U pip setuptools

# # Install pip requirements
# COPY requirements.txt .

# RUN .venv/bin/pip install --no-cache-dir -r requirements.txt


# FROM python:3.10-slim as main

# # Keeps Python from generating .pyc files in the container
# ENV PYTHONDONTWRITEBYTECODE=1


# WORKDIR /src
# COPY --from=build /src /src
# COPY src/main.py /src

# # Creates a non-root user with an explicit UID and adds permission to access the /src folder
# # For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /src
# USER appuser

# ENV PATH="/src/.venv/bin:$PATH"

# # During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# CMD ["python", "main.py"]