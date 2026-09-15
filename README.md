# Yuting Peng — personal academic website

Live site: https://kitepretty.github.io/

A Hugo website based on [Barks](https://github.com/timothygebhard/barks), with a bright yellow accent, a photo on the right of the introduction, a research index, and five project pages. The theme is vendored at commit `99163e05a14047757f95144edcaca492a763157c`; its MIT license is retained in `themes/barks/LICENSE`.

## 修改文字

- 首页：`content/_index.md`
- 研究介绍：`content/research/_index.md`
- 各项目：`content/research/<项目名>/index.md`
- 联系段落：`data/home.json`
- 配色和布局：`assets/css/custom.css`
- CV：`static/files/yuting-peng-cv.pdf`

当前与本地的 `Website_Copy_Editable.md` 同步。修改该主稿后，在本目录运行 `python3 scripts/sync_content.py`，只导入网页正文。内部批注、申请资料和论文全文不会导入。直接在 GitHub 修改 `content/` 后，应将改动同步回本地主稿，以免下一次导入覆盖。

Yoga 的个人分工与发现目前使用根据题名整理的初稿，后续可直接更新对应项目 Markdown。稿件通过公开邮箱人工索取，不使用表单或自动发送附件。

## 本地预览

使用 Hugo **extended 0.145.0**：

```sh
hugo server
```

正式构建与检查：

```sh
hugo --gc --minify
python3 scripts/check_site.py
```

## GitHub Pages 发布

推送至 `main` 后，GitHub Actions 自动构建、检查本地链接并发布到 GitHub Pages。构建失败时不会发布失败版本。GitHub Pages 的 Source 设置为 GitHub Actions。

## Cloudflare Workers 发布

站点使用 Workers Static Assets，配置保存在 `wrangler.jsonc`。无需数据库或服务器代码，发布前自动构建 Hugo 并检查站点。依赖 Node.js 22 或更新版本、Python 3 和 Hugo extended 0.145.0。

```sh
npm ci
npx wrangler login
npm run deploy
```

`npm run preview:workers` 可预览 Cloudflare 的目录跳转和 404 页面。首次部署需要已登录的 Cloudflare 账户；`workers.dev` 地址由账户的子域名决定，部署完成后才能确认。

若通过 Cloudflare 的 GitHub 集成自动部署，选择本仓库的 `main`，根目录为 `/`，部署命令为 `npm run deploy`（其中自动执行构建），构建变量 `HUGO_VERSION=0.145.0`。不要运行 `sync_content.py`：它只用于本地编辑主稿，仓库内的 `content/` 已是可发布的正文。

`yutingpeng.com` 尚未注册，因此配置中暂不绑定该域名。注册并在同一 Cloudflare 账户中激活后，添加自定义域名：

```json
"routes": [{ "pattern": "yutingpeng.com", "custom_domain": true }]
```

届时将 `hugo.toml` 的 `baseURL` 改为 `https://yutingpeng.com/` 后重新发布，以更新搜索引擎和分享链接。也可以在构建时使用 `HUGO_BASEURL` 覆盖。GitHub Actions 仍会单独使用其自身地址构建。

官方说明：[静态网站](https://developers.cloudflare.com/workers/static-assets/routing/static-site-generation/)、[自定义域名](https://developers.cloudflare.com/workers/configuration/routing/custom-domains/)。

## 图片与文件

照片与项目图片由 Yuting Peng 提供。原始照片保存在本地材料文件夹；仓库仅包含网页使用的压缩图片。EHR、Yoga、BC 和 ED 插画仅作为主题封面，不作为已部署系统或研究结果。Rainbow School 图为社区设计的虚拟学校截图。只公开 CV，不公开在审论文或申请材料。

Barks 作者的版权声明仅适用于主题代码；个人文字、照片及研究图片的权利归各自权利人所有。
