# SheriffBot

[![Build Status](https://github.com/42musaev/ChitBot/actions/workflows/.deploy.yml/badge.svg)](https://github.com/42musaev/ChitBot/actions/workflows/.deploy.yml)

<p align="center">
  <img src="https://i.imgur.com/a06cFCU.jpeg" alt="Bot Image" style="width: 70%; height: 70%">
</p>

## Description

SheriffBot is designed to enhance safety and maintain law and order in ChitCom County. It allows users to report
incidents, track crime statistics, and promptly respond to emergencies.

## Local Setup Instructions

To run this project locally, follow these steps:

1. **Create `.env` file**: Create a file named `.env` in the root directory of your project.

2. **Add environment variables**: Inside `.env`, add the following environment variables:
   ```plaintext
   bot_token=<your token>
   debug=True

3. Install project dependencies.

```shell
poetry install
```

4. Run.

```shell
python3 bot.py
```

5. Install the git hook scripts

```shell
pre-commit install
```

6. Run ruff and isort

```shell
pre-commit run --all-files
```
