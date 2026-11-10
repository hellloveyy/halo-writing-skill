# 跨电脑使用与插件选择

## 从 GitHub 安装

源码仓库为 [hellloveyy/halo-writing-skill](https://github.com/hellloveyy/halo-writing-skill)，技能在其中的 `halo-writing/` 子目录。它可以独立于博客项目安装，不依赖原电脑路径或作者站点。

新电脑上优先让 Codex 使用内置 `skill-installer` 安装链接 `https://github.com/hellloveyy/halo-writing-skill/tree/main/halo-writing`。固定初始发布版本时使用 `tree/v0.1.0/halo-writing`。安装器通常安装到 `$CODEX_HOME/skills/halo-writing`，默认 `~/.codex/skills/halo-writing`；以实际返回路径为准。

也可参照仓库 README，用 Git 克隆后将 `halo-writing/` 链接到 `~/.agents/skills/halo-writing`；或放进某个项目的 `.agents/skills/` 使其仅对该项目可用。Codex 支持技能目录符号链接，但移动源目录会使链接失效。避免在同一机器安装多个同名副本。

安装后可使用自然语言「用 halo写文……」或 `$halo-writing`。若新技能未出现在选择器中，重新打开聊天或重启客户端。安装完成仅表示技能文件就绪，不表示 MCP 认证已配置或文章已同步。

## 文章另行同步

技能、文章、配图、续写记录和发布状态是不同的文件。只重新安装技能不能恢复上次文章或聊天；使用用户选择的私有 Git 仓库或文件同步方式保存后四类文件。不要把正在写的文章提交到这个公开技能仓库。

续写前定位当前写作工作区，读取原稿、图片和交接记录。只存在远程草稿时，可在已获读取授权的情况下通过 Halo MCP 恢复；未上传内容仍需从用户的文件来源取得。

## 凭据单独配置

首选连接是部署在用户 Halo 站点上的官方 MCP Server；安装一次服务端，各电脑配置同一站点的连接即可。具体配置见 [halo-mcp.md](halo-mcp.md)，包括可直接运行的 macOS 安装器。每台电脑可使用独立的 MCP 访问密钥，便于单独管理。

`HALO_URL` 是站点配置；MCP 的 `HALO_MCP_TOKEN` 和备用 REST 的 `HALO_TOKEN` 是不同的机密。每台电脑通过环境变量或 macOS 钥匙串配置所需密钥，不把密钥或含密钥的 `.env`、浏览器会话、SSH 私钥同步到技能或文章仓库。可以同步不含密钥的 MCP 配置模板，但不能复制整个个人配置文件来同步。

换电脑后只有写作文件、没有令牌，也能继续讨论、写作和配图；发布前再检查凭据。已有授权的 Halo 远程草稿和已发布文章可通过 MCP 读取恢复；尚未上传的草稿、配图与聊天素材仍需同步本地文件。不能承诺同一账号登录就会自动带来本机技能、稿件和环境变量。

## 何时封装插件

- 主要在两台电脑的 Codex 中使用：从 GitHub 分别安装技能，再连接 Halo 官方远程 MCP 即可。若需要插件安装入口或分发多个技能，可以把同一技能打包成插件。
- 还希望在 ChatGPT 网页版、手机或不下载项目的环境中使用：评估可安装插件是否能接入现有 Halo 官方远程 MCP，让技能负责写作流程，Halo 负责其支持的远程草稿、附件和发布；不要默认重新开发一套 Halo 发布服务。
- 插件能够包含技能，因此不是重写另一套工作流。已有本地技能可以作为插件的内容核心。插件的导入、安装和分发能力受产品界面、账号及工作区设置影响，接入前核实。
- 只有本地脚本的插件并不等于云端服务；浏览器或手机环境不能据此自动获得电脑文件、Python 环境或环境变量。要实现不依赖原电脑的发布，需要支持该环境的远程连接与认证。

不要因为用户问起插件就创建公网服务、开放发布端点或把令牌上传到服务器。先确定使用界面及分发方式；在需要实现远程连接时再设计最小能力，例如保存草稿、上传附件、发布指定文章和读取状态。发布仍保留用户最终确认这一边界。

## 官方参考

- [技能创建、发现路径与分发](https://learn.chatgpt.com/docs/build-skills)
- [技能和 MCP 在插件中的分工](https://developers.openai.com/plugins/concepts/plugins)
- [插件打包与本地市场](https://developers.openai.com/plugins/build/plugins)
