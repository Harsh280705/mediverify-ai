class OCRParser:
    @staticmethod
    def parse_lines(lines: list[str]) -> str:
        """
        Takes a list of raw text lines and formats them into a single raw text string.
        """
        return "\n".join(lines).strip()
