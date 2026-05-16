def extract_section(text, section_name):
  """
  Extracts content from a section in the agent response.

  Example:
  section_name = "THOUGHT"
  finds text after:
  THOUGHT:
  """

  # Build the section marker, for example "ACTION"
  marker = f"{section_name}:"

  if marker not in text:
    return None


  start = text.find(marker) + len(marker)

  # These markers define where each ReAct section starts and ends
  section_markers = ["THOUGHT:", "ACTION:", "COMMAND:", "FINAL:"]
  end = len(text)

  # Find the closest next section marker so we only extract the current section
  for next_marker in section_markers:
    next_pos = text.find(next_marker, start)
    if next_pos != -1:
      end = min(end, next_pos)

  return text[start:end].strip()


def parse_react_response(text):
  """
  Parses a ReAct-style response into a dictionary.
  """

  # Return a structured dictionary that main.py can use for control flow
  return {
    "thought": extract_section(text, "THOUGHT"),
    "action": extract_section(text, "ACTION"),
    "command": extract_section(text, "COMMAND"),
    "final": extract_section(text, "FINAL")
  }