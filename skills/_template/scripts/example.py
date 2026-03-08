from pathlib import Path


def main() -> None:
    output = Path("tmp/example-output.txt")
    output.write_text("skill template ready\n", encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
