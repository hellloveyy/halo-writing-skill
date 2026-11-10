#!/usr/bin/env python3
"""Install a Keychain reader and print a secret-free Codex MCP config."""

import argparse
import json
import os
from pathlib import Path
import platform
import shlex
import sys
from urllib.parse import urlsplit, urlunsplit


def mcp_endpoint(site):
    site = site.strip()
    try:
        parsed = urlsplit(site)
        _ = parsed.port  # Accessing port also validates its syntax and range.
    except ValueError:
        raise ValueError("站点地址无效。") from None
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username is not None
            or parsed.password is not None or parsed.query or parsed.fragment
            or any(char.isspace() for char in site)):
        raise ValueError("请提供不含凭据、查询参数或片段的 HTTPS 站点地址。")
    path = parsed.path.rstrip("/")
    if not path.endswith("/mcp"):
        path += "/mcp"
    return urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


def install_helper(bin_dir):
    source = Path(__file__).with_name("keychain_headers.py")
    data = source.read_bytes()
    bin_dir = Path(bin_dir).expanduser().resolve()
    bin_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    destination = bin_dir / "halo_writing_keychain_headers.py"
    if destination.is_symlink() or (destination.exists() and destination.read_bytes() != data):
        raise FileExistsError("目标读取器已存在且内容不同，请先检查并备份再更新。")
    if not destination.exists():
        descriptor = os.open(str(destination), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o700)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
    destination.chmod(0o700)
    return destination


def main(argv=None, system=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", required=True, help="HTTPS Halo site or MCP endpoint")
    parser.add_argument("--bin-dir", type=Path, help="Optional stable directory for the credential reader")
    parser.add_argument("--service", help="Optional Keychain service; defaults to a name derived from the site")
    parser.add_argument("--account", default="halo")
    args = parser.parse_args(argv)
    if (system or platform.system()) != "Darwin":
        print("此安装器仅适用于 macOS；其他系统请使用环境变量认证。", file=sys.stderr)
        return 1
    try:
        url = mcp_endpoint(args.site)
        host = urlsplit(url).netloc.lower()
        service = args.service or "codex.halo." + host
        if any(not value or any(ord(char) < 32 for char in value) for value in (service, args.account)):
            raise ValueError("钥匙串服务名和账号格式无效。")
        codex_home = Path(os.environ.get("CODEX_HOME") or str(Path.home() / ".codex"))
        target = install_helper(args.bin_dir if args.bin_dir is not None else codex_home / "bin")
    except (OSError, ValueError) as error:
        message = str(error) if isinstance(error, ValueError) else "无法安装读取器；请检查目标目录权限或已有文件。"
        print(message, file=sys.stderr)
        return 1
    command = shlex.join([sys.executable, str(target), "--service", service, "--account", args.account])
    print("读取器已安装。将以下配置合并到 Codex 的 config.toml；本脚本不会修改配置或保存密钥：")
    print("[mcp_servers.halo]")
    print("url = " + json.dumps(url))
    print("http_headers_helper = " + json.dumps(command))
    print("\n在真实终端执行以下命令，按提示输入 MCP 密钥：")
    print(shlex.join(["/usr/bin/security", "add-generic-password", "-U", "-a", args.account, "-s", service, "-w"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
