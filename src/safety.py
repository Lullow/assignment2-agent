import shlex

# Commands in this set are blocked completley because they can modify, delete or damage the system
BLOCKED_COMMANDS = {
    "rm",
    "sudo",
    "shutdown",
    "reboot",
    "mkfs",
    "dd",
    "chmod",
    "chown",
    "curl",
    "wget",
    "ssh",
    "scp",
}

# Patterns catch dangerous combinations even when the base command is not enough.
BLOCKED_PATTERNS = {
    "rm -rf",
    ":(){",
    "curl | bash",
    "wget | bash",
    "> /dev/sda",
    "/dev/sda",
    "/dev/nvme",
}

# Block shell operators that could chain commands, redirect output, or run nested commands.
BLOCKED_OPERATORS = {
    ";",
    "&&",
    "||",
    "|",
    ">",
    ">>",
    "<",
    "$(",
    "`",
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

    # Normalize the command to make pattern checks case-insensetive
    command_lower = command.lower().strip()

    # Block operators that contains dangerous shell operators
    for operator in BLOCKED_OPERATORS:
      if operator in command_lower:
        return {
          "safe": False,
          "reason": f"Command contains blocked shell operator {operator}"
        }

    # Block commands that contains known dangerous patterns
    for pattern in BLOCKED_PATTERNS:
        if pattern in command_lower:
            return {
                "safe": False,
                "reason": f"Command contains blocked pattern: {pattern}",
            }


    # Parse the command safely so we can inspect the base command
    try:
        parts = shlex.split(command)
    except ValueError as e:
        return {
            "safe": False,
            "reason": f"Command could not be parsed safely: {e}",
        }

    if not parts:
        return {
            "safe": False,
            "reason": "Command is empty after parsing.",
        }

    # The first token is the actual command, for example "ls" in "ls -la"
    base_command = parts[0]

    # Block commands that are considered unsafe by default
    if base_command in BLOCKED_COMMANDS:
        return {
            "safe": False,
            "reason": f"Command is blocked: {base_command}",
        }

    return {"safe": True, "reason": "Command passed safety checks."}
