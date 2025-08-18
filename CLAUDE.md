## CLAUDE.md

This project is Home Assistant custom integration, aim to integrate with "sHome" system (직방 홈 IoT).
"sHome" system is based on REST API stack.

Due to limitation of Home Assistant, modules, classes, functions from this project should import via relative import. (ex. `from .dto.credential import Credential`)
