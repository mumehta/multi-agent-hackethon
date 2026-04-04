from textwrap import dedent


def main() -> None:
    message = dedent(
        """
        Multi-Agent DevOps Incident Analysis Suite

        [OK] uv project scaffold is ready.
        Next steps:
          1. Copy `.env.example` to `.env`
          2. Run `uv sync --dev`
          3. Start building the FastAPI/Streamlit UI and LangGraph agents

        See `README.md` for setup and workflow details.
        """
    ).strip()
    print(message)


if __name__ == "__main__":
    main()
