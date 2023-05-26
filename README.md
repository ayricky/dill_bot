# Dill Bot
Dill Bot is a custom Discord bot developed specifically for the Dill Do server.

## Getting Started
These instructions will help you get a copy of the project up and running on your local machine for development and testing purposes.

## Prerequisites
- Python 3.11
- Docker
- Poetry (Python package manager)

## Installation
1. Clone this repository: git clone https://github.com/ayricky/dill_bot.git
2. Navigate to the project directory: cd dill_bot
3. Install dependencies with Poetry: poetry install

## Running the Tests
After installing the dependencies, you can run the tests with the following command:
```
# TODO: Add command to run tests
```

## Deployment
This project is configured with a CI/CD pipeline using GitHub Actions. When changes are pushed to the main branch, the pipeline automatically:

- Sets up the latest Python environment
- Installs project dependencies
- Builds a Docker image
- Pushes the Docker image to Docker Hub

To manually deploy the bot, build the Docker image and run it:

```sh
docker build . --file Dockerfile --tag dill_bot
docker run --name dill_bot_instance dill_bot
``` 

## Built With
- Python
- Docker
- GitHub Actions

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning
We use SemVer for versioning. For the versions available, see the tags on this repository.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.

## Acknowledgments
Thanks to the Discord API for making this possible.
And to GitHub Actions for seamless CI/CD workflow.
