from brownie import accounts, config


def load_accounts():
    for private_key in get_parsed_private_keys():
        accounts.add(private_key)


def get_parsed_private_keys():
    return config["keys"].split(",")
