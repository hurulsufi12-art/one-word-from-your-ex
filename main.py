"""One Word From Your Ex — entry program.

Writes exactly one word (1-24 chars) to /output/entry.txt: the word an ex
would use to describe the entrant — funniest and most painfully honest.
Stdlib only, deterministic.
"""
import os

TEXT = "Ghoster"


def check_gate(text, max_chars=24):
    """Enforce the scorer's gate (RULES.txt) plus the task's own rule.

    Gate: UTF-8 text of 1-max_chars characters, not whitespace-only.
    Task: exactly ONE word an ex would use to describe the entrant,
    nothing else. Returns the text unchanged when it passes; raises
    SystemExit with a specific reason when it does not, so a bad entry
    fails loudly instead of being written.
    """
    if not isinstance(text, str):
        raise SystemExit("entry text is not a string")
    if not 1 <= len(text) <= max_chars:
        raise SystemExit(f"entry text violates the 1-{max_chars} char gate")
    if not text.strip() or text != text.strip() or "\n" in text:
        raise SystemExit("entry text is blank, padded or multi-line")
    if len(text.split()) != 1 or not text.isalpha():
        raise SystemExit("entry text is not exactly one word")
    return text


def main():
    text = check_gate(TEXT)
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # Write atomically: a crash mid-write must never leave a truncated
    # entry.txt for the grader to read. Write to a temp file in the same
    # directory, flush it to disk, then rename over the target.
    # Temp name carries the pid so two concurrent grader runs in the same
    # directory never overwrite each other's in-flight file.
    tmp_path = os.path.join(out_dir, f".entry.txt.tmp.{os.getpid()}")
    final_path = os.path.join(out_dir, "entry.txt")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, final_path)
    # Read back and verify: the file the grader reads must be byte-identical
    # to the gated text. Fail loudly instead of shipping a corrupt entry.
    with open(final_path, encoding="utf-8") as f:
        if f.read() != text:
            raise SystemExit("entry.txt read-back mismatch after atomic write")


if __name__ == "__main__":
    main()
