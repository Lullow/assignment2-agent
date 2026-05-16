import shlex

BLOCKED_COMMANDS = {
    "rm",
    "sudo",
    "shutdown",
    "reboot",
    "mkfs",
    "dd",
    "chmod",
    "chown",
}

BLOCKED_PATTERNS = {
    "rm -rf",
    ":(){",
    "curl | bash",
    "wget | bash",
    "> /dev/sda",
    "/dev/sda",
    "/dev/nvme",
}


def is_command_safe(command):
    """
    Checks if a bash command is allowed to run

    Returns:
    {
      "safe": bool,
      "reason": str
    }
    """

    if not command or not command.strip():
        return {
            "safe": False,
            "reason": "Command is empty.",
        }

    command_lower = command.lower().strip()

    for pattern in BLOCKED_PATTERNS:
        if pattern in command_lower:
            return {
                "safe": False,
                "reason": f"Command contains blocked pattern: {pattern}",
            }

    try:
        parts = shlex.split(command)
    except ValueError as e:
        return {
            "safe": False,
            "reason": f"Command could not be parsed safley: {e}",
        }

    if not parts:
        return {
            "safe": False,
            "reason": "Command is empty after parsing.",
        }

    base_command = parts[0]

    if base_command in BLOCKED_COMMANDS:
        return {
            "safe": False,
            "reason": f"Command is blocked: {base_command}",
        }

    return {"safe": True, "reason": "Command passed saftey checks."}
