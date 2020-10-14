# Changelog
## v1.0.2
Patch release that fixes a few formatting issues in the readme. Also added version tagging to the Docker container.
### Changes
* Added this changelog.
* Docker image now tags version in addition to stable/development tags.
* Changes and corrections in readme.

## v1.0.1
Patch release that fixes a few bugs.
### Fixes
* Fixed an issue where the account regex was not loading from the config file and would instead match all input.
* Fixed an issue where the conversation and message regex did not use the DOTALL flag.

## v1.0.0
This is the initial release of PurpleRelay.
### New Features
* Relay messages from Pidgin or Finch to Discord.
* Added a Docker container available on [DockerHub](https://hub.docker.com/r/nathanls/purplerelay).
