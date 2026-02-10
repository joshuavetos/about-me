import re

class ScalpelEngine:
    @staticmethod
    def insert(source_code, anchor_text, new_code, position='after'):
        """
        Performs a surgical code insertion with indentation preservation.
        """
        if not anchor_text or anchor_text not in source_code:
            raise ValueError(f"Anchor text '{anchor_text}' not found in source.")

        lines = source_code.splitlines()
        indent = ""
        for line in lines:
            if anchor_text in line:
                # Capture the exact leading whitespace of the anchor line
                indent = line[:len(line) - len(line.lstrip())]
                break

        # Apply the detected indentation to every line of the new payload
        indented_lines = [(f"{indent}{l}" if l.strip() else l) for l in new_code.splitlines()]
        indented_block = "\n".join(indented_lines)

        pattern = re.escape(anchor_text)
        if position == 'after':
            replacement = f"{anchor_text}\n{indented_block}"
        else:
            replacement = f"{indented_block}\n{anchor_text}"

        # count=1 ensures we only operate on the first match (surgical precision)
        return re.sub(pattern, replacement, source_code, count=1)
