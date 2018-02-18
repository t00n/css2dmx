# css2dmx

## Why ?

Because who has never dreamed of controlling DMX512 devices with CSS stylesheets ? I know I did. And now it's here.

## How ?

Describe your hardware, your DOM (DMX Object Model) and your style in three separate files (.hw, .tree and .css).

Run css2dmx and watch the magic happen !

**DISCLAIMER: the project is in early stage, do not expect too much ;)**

## Installation

You will need
 * Open Lighting Architecture (https://www.openlighting.org/ola/) to talk to your DMX512 device
 * Google Protobuf (https://github.com/google/protobuf) v3.1.x because OLA does not work with later versions
 * Python 3

Install python requirements
```bash
pip install -r requirements.txt
```

## Usage

Use OLA to connect your device (https://www.openlighting.org/ola/getting-started/using-ola/).

See the examples to see everything that you can do. There is no docs at the moment as the project is evolving rapidly.

Run with
```bash
python3 css2dmx.py path/to/project/dir
```