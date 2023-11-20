import argparse
from typing import Optional

from llama_index.llama_pack.download import LLAMA_HUB_URL, download_llama_pack


def handle_download_llama_pack(
    llama_pack_class: Optional[str] = None,
    download_dir: Optional[str] = None,
    llama_hub_url: str = LLAMA_HUB_URL,
    refresh_cache: bool = False,
    **kwargs,
):
    assert llama_pack_class is not None
    assert download_dir is not None

    download_llama_pack(
        llama_pack_class=llama_pack_class,
        download_dir=download_dir,
        llama_hub_url=llama_hub_url,
        refresh_cache=refresh_cache,
    )
    print(f"Successfully downloaded {llama_pack_class} to {download_dir}")


def main():
    parser = argparse.ArgumentParser(description="LlamaIndex CLI tool.")

    # Subparsers for the main commands
    subparsers = parser.add_subparsers(title="commands", dest="command", required=True)

    # download llamapacks command
    llamapack_parser = subparsers.add_parser(
        "download-llamapack", help="Download a llama-pack"
    )
    llamapack_parser.add_argument(
        "llama_pack_class",
        type=str,
        help=(
            "The name of the llama-pack class you want to download, "
            "such as `GmailOpenAIAgentPack`."
        ),
    )
    llamapack_parser.add_argument(
        "download_dir",
        type=str,
        help="Custom dirpath to download the pack into.",
    )
    llamapack_parser.add_argument(
        "--llama-hub-url",
        type=str,
        default=LLAMA_HUB_URL,
        help="URL to llama hub.",
    )
    llamapack_parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help=(
            "If true, the local cache will be skipped and the pack "
            "will be fetched directly from the remote repo."
        ),
    )
    llamapack_parser.set_defaults(
        func=lambda args: handle_download_llama_pack(**vars(args))
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the appropriate function based on the command
    args.func(args)


if __name__ == "__main__":
    main()
