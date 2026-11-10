#!/usr/bin/python3
"""Emit Halo MCP authentication headers for Codex, reading macOS Keychain."""

import argparse
import json
import subprocess
import sys


SERVICE = "codex.halo.mcp"
ACCOUNT = "halo"


class CredentialError(Exception):
    pass


def load_headers(service=SERVICE, account=ACCOUNT):
    try:
        result = subprocess.run(
            [
                "/usr/bin/security", "find-generic-password",
                "-s", service, "-a", account, "-w",
            ],
            capture_output=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        raise CredentialError("无法读取 Halo 钥匙串凭据，请检查钥匙串是否已解锁。") from None
    if result.returncode != 0:
        raise CredentialError("未能读取 Halo MCP 密钥，请先将密钥保存到登录钥匙串。")
    try:
        # security appends a line ending; embedded whitespace is never valid here.
        token = result.stdout.decode("ascii").rstrip("\r\n")
    except UnicodeDecodeError:
        raise CredentialError("Halo MCP 密钥格式无效，请重新保存。") from None
    if not token or not all(33 <= ord(char) <= 126 for char in token):
        raise CredentialError("Halo MCP 密钥格式无效，请重新保存。")
    return {"Authorization": "Bearer " + token}


def main(argv=()):
    parser = argparse.ArgumentParser(description="Read Halo MCP credentials from macOS Keychain for Codex.")
    parser.add_argument("--service", default=SERVICE)
    parser.add_argument("--account", default=ACCOUNT)
    args = parser.parse_args(argv)
    try:
        headers = load_headers(service=args.service, account=args.account)
    except CredentialError as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps(headers))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
