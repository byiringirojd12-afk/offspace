DANGEROUS_ACTIONS = {
    "delete_file",
    "modify_system",
    "install_software",
    "network_configuration"
}


def requires_confirmation(action):
    return action in DANGEROUS_ACTIONS
