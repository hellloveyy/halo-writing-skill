# halo写文

一个用于 Codex 的写作技能：把灵感和聊天整理成 Markdown 文章，生成配图，供你审阅，在你明确确认后通过 Halo 官方 MCP 发布。

**灵感聊天 → 成稿 → 配图 → 审阅 → 确认发布**

技能名为 `halo-writing`，界面名称为「halo写文」。本项目是独立的社区技能，使用 [Halo 官方 MCP Server](https://www.halo.run/store/apps/app-ybv96zol) 连接你的站点。

## 安装到另一台电脑

### 方法一：让 Codex 安装（推荐）

在新电脑的 Codex 中发送：

```text
请使用 skill-installer 安装这个技能：
https://github.com/hellloveyy/halo-writing-skill/tree/main/halo-writing
```

安装完成后，技能将在后续聊天中可用；若选择器中没有显示，重新打开聊天或重启 Codex。需要固定版本时，将链接中的 `main` 换成 `v0.1.0`。

### 方法二：Git 安装

下面是 macOS/Linux 的用户级安装方式，在新电脑终端执行：

```sh
mkdir -p "$HOME/.local/share" "$HOME/.agents/skills"
git clone https://github.com/hellloveyy/halo-writing-skill.git "$HOME/.local/share/halo-writing-skill"
ln -s "$HOME/.local/share/halo-writing-skill/halo-writing" "$HOME/.agents/skills/halo-writing"
```

两种安装方式选择一种即可。同名技能已经存在时，先确认旧版本位置，避免重复安装。Git 方式更新时执行：

```sh
git -C "$HOME/.local/share/halo-writing-skill" pull --ff-only
```

## 连接自己的 Halo

写作和配图可以先开始；要读取或发布到站点，需要完成 MCP 配置。前提是 Halo 2.26.0+、生产站点使用 HTTPS，并有可用的图像生成工具来完成自动配图。

### 1. 配置 Halo 服务端

1. 在 Halo 后台应用市场安装并启用发布者为 Halo 的 **MCP Server**。
2. 超级管理员进入「工具 → MCP 服务」，为这台电脑创建访问密钥。
3. 选择文章查询、读取、创建、更新、发布，以及需要的分类/标签查询和附件上传工具。
4. 复制后台提供的 MCP 地址，通常为 `https://你的站点/mcp`。

访问密钥保存在本机，不发到聊天，也不提交到本仓库。

### 2. macOS：重启后自动认证（推荐）

安装技能后，可以直接对 Codex 说：

```text
按照 halo写文 的配置说明，帮我用 macOS 钥匙串配置 Halo MCP。
我的站点是 https://我的域名。
密钥由我在终端中输入，不发给你。
```

Codex 应读取 [完整接入说明](halo-writing/references/halo-mcp.md)，运行技能自带的安装器，并只合并 Halo 的配置段落。

如果使用上面的 Git 安装方式，也可以手动运行（将示例域名换成你的站点）：

```sh
python3 "$HOME/.local/share/halo-writing-skill/halo-writing/scripts/install_macos_helper.py" \
  --site https://blog.example.com
```

需要 Python 3.9+。安装器只安装读取器并输出配置与保存密钥的命令，**不会读取密钥、修改 TOML 或发布文章**：

1. 将输出的 `[mcp_servers.halo]` 段落合并到 `~/.codex/config.toml`；使用自定义 `CODEX_HOME` 时则是其中的 `config.toml`。已有 Halo 段落时编辑原段落，保留其他服务器配置。
2. 使用输出的 `http_headers_helper`，移除该 Halo 段落旧的 `bearer_token_env_var` 或静态 Authorization 配置，避免旧凭据优先。
3. 在真实终端执行输出的 `security add-generic-password ... -w` 命令，按提示输入密钥。`-w` 应放在最后，输入不会显示，也不会被写进命令历史。
4. 完全退出并重新打开 Codex，让它做一次只读的文章和附件查询。

密钥保存在 macOS 登录钥匙串中，重启后仍可读取；密钥到期、撤销或轮换后需更新。更换电脑时重新完成本机配置。

### 3. 环境变量方式（可选）

不使用 macOS 钥匙串时，将密钥配置到 **Codex 进程可读取的** `HALO_MCP_TOKEN` 环境变量，并合并以下配置：

```toml
[mcp_servers.halo]
url = "https://blog.example.com/mcp"
bearer_token_env_var = "HALO_MCP_TOKEN"
```

`bearer_token_env_var` 填变量名，不能填密钥值。已经运行的桌面客户端不一定能看到终端刚设置的变量；持久化方式按操作系统配置，重启客户端后再验证。

## 使用

```text
用 halo写文：我突然想到，AI 让产品经理更需要判断力，我们先聊聊。
```

```text
把刚才聊的整理成文章，配好图给我审阅。
```

```text
确认发布这篇文章到我的 Halo。
```

默认先保存在工作区 `articles/<slug>/`，包括 Markdown 原稿、图片、续写记录和已核实的发布状态。用户已有目录约定时沿用它。

“不错”“先这样”不会触发发布。你明确要求“换一张更简洁的图，然后发布”时，技能会完成这次已授权修改再发布，不重复确认每个中间步骤。

## 换电脑时需要带走什么

- **技能**：从这个仓库重新安装即可。
- **连接**：在新电脑配置 MCP 地址及本机密钥；Halo 服务端无需重复安装。
- **正在写的文章**：单独同步原稿、图片和续写记录。安装技能不等于恢复本地文章或历史聊天；已上传的远程草稿可经 MCP 读取。

## 验证与贡献

在仓库根目录运行，不需要真实密钥，也不会访问 Halo：

```sh
python3 -m unittest discover -s tests -v
```

测试覆盖凭据输出、读取失败时的保密、异常输入、按站点选择钥匙串记录、含空格路径、重复安装及已有文件保护。欢迎提交 issue 或 PR。

采用 [MIT License](LICENSE)。
