# Firegex

Initialization script and config for [Firegex](https://github.com/Pwnzer0tt1/firegex).

## Usage

Edit the `config.json` file and set:

- the server **IP**,
- the **interface** to listen on,
- the **challenges** with port

Edit the `rules.json` file and add any default rules you would like to be created for every service.

Run the `python setup.py` script, this should start firegex with a default password and some default rules.

The password is read from the `password` file, if present, otherwise it's randomly generated and saved to the `password` file.
The `password` file is never deleted on it's own.

After starting firegex with `python setup.py` you can use:

- `python start.py stop`: stop firegex
- `python start.py --build`: start firegex applying any changes locally made to the firegex source code
- `docker volume rm firegex_firegex_data`: delete the volume containing the rules
