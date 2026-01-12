# GitHub Secrets 配置指南

## 📋 需要配置的 Secrets 列表

在 GitHub 仓库中配置以下 5 个 Secrets：

### 1. QWEN_API_KEY（必填）
- **说明**：通义千问 API Key
- **如何获取**：
  1. 访问 https://dashscope.aliyun.com/
  2. 登录/注册账号
  3. 进入「API-KEY 管理」
  4. 创建新的 API Key
  5. 复制 API Key（格式：sk-xxxxxxxxxxxxx）
- **示例值**：`sk-1234567890abcdef`

### 2. WEBHOOK_URL（必填）
- **说明**：企业微信机器人的 Webhook URL
- **如何获取**：
  1. 登录企业微信管理后台
  2. 进入「应用管理」→「自建应用」→「创建应用」
  3. 或者进入群聊 → 群设置 → 群机器人 → 添加机器人
  4. 复制 Webhook 地址
- **示例值**：`https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### 3. WECHAT2RSS_DOMAIN（必填）
- **说明**：Wechat2RSS 服务域名
- **如何获取**：
  - 如果你使用免费的 Wechat2RSS 服务：`wec.zeabur.app`
  - 如果你自己部署了 Wechat2RSS：填你自己的域名
- **示例值**：`wec.zeabur.app`

### 4. RSS_TOKEN（必填）
- **说明**：Wechat2RSS 访问令牌（Token）
- **如何获取**：
  1. 访问 https://wechat2rss.xlab.app
  2. 登录后查看你的 RSS 订阅链接
  3. 复制 URL 中 `?token=` 后面的部分
- **示例值**：`myPassword123`

### 5. GITHUB_TOKEN（可选）
- **说明**：GitHub Personal Access Token（用于创建 Gist）
- **如何获取**：
  1. 登录 GitHub
  2. 点击右上角头像 → Settings
  3. 左侧菜单最下方 → Developer settings
  4. Personal access tokens → Tokens (classic)
  5. Generate new token (classic)
  6. 勾选 `gist` 权限
  7. 生成并复制 Token
- **示例值**：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **注意**：如果不配置，GitHub Gist 功能将不可用

---

## 📝 配置步骤（图文教程）

### Step 1: 进入仓库设置

1. 打开你的 GitHub 仓库
2. 点击上方标签页的 **Settings**（设置）

### Step 2: 进入 Secrets 配置页面

1. 左侧菜单找到 **Secrets and variables**
2. 点击 **Actions**
3. 你会看到「Repository secrets」部分

### Step 4: 逐个添加 Secrets

点击 **New repository secret** 按钮，重复以下步骤 5 次：

#### 添加 Secret 1：QWEN_API_KEY
- **Name**：`QWEN_API_KEY`
- **Value**：粘贴你的通义千问 API Key
- 点击 **Add secret**

#### 添加 Secret 2：WEBHOOK_URL
- **Name**：`WEBHOOK_URL`
- **Value**：粘贴你的企业微信 Webhook URL
- 点击 **Add secret**

#### 添加 Secret 3：WECHAT2RSS_DOMAIN
- **Name**：`WECHAT2RSS_DOMAIN`
- **Value**：`wec.zeabur.app`（或你自己的域名）
- 点击 **Add secret**

#### 添加 Secret 4：RSS_TOKEN
- **Name**：`RSS_TOKEN`
- **Value**：粘贴你的 Wechat2RSS Token
- 点击 **Add secret**

#### 添加 Secret 5：GITHUB_TOKEN（可选）
- **Name**：`GITHUB_TOKEN`
- **Value**：粘贴你的 GitHub Personal Access Token
- 点击 **Add secret**

---

## ✅ 配置完成后的检查清单

配置完成后，检查以下内容：

- [ ] 5 个 Secrets 全部添加成功
- [ ] Secrets 名称拼写正确（区分大小写）
- [ ] Secrets 值没有多余的空格或换行
- [ ] `QWEN_API_KEY` 以 `sk-` 开头
- [ ] `WEBHOOK_URL` 是完整的 HTTPS URL
- [ ] `GITHUB_TOKEN`（如果配置）以 `ghp_` 开头

---

## 🔍 常见问题

### Q1: Secret 配置后不生效？
**A**：
1. 检查 Secret 名称是否完全匹配（区分大小写）
2. 检查 Secret 值是否有多余的空格
3. 重新触发 GitHub Actions 运行

### Q2: 如何测试 Secret 是否配置正确？
**A**：
1. 进入 Actions 页面
2. 手动运行一次 workflow（Run workflow → Run workflow）
3. 查看运行日志，检查是否有错误

### Q3: GITHUB_TOKEN 可以不配置吗？
**A**：可以。如果不配置，GitHub Gist 功能将不可用，但其他功能正常。

### Q4: 如何更新 Secret？
**A**：
1. 进入 Secrets 配置页面
2. 找到要更新的 Secret
3. 点击 **Update** 更新值
4. 更新后立即生效，无需重启

---

## 🎯 配置示例（参考）

以下是我个人的配置（请替换为你自己的值）：

```
QWEN_API_KEY = sk-07f3f7ea3d4c4b53a0a3f317f398103b
WEBHOOK_URL = https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=541278aa-269c-4c77-b335-576d0a73777f
WECHAT2RSS_DOMAIN = wec.zeabur.app
RSS_TOKEN = myPassword123
GITHUB_TOKEN = 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
```

---

## 📌 注意事项

⚠️ **安全提醒**：
1. Secrets 配置后会被加密存储，只有你能看到
2. 不要将 Secrets 的值提交到代码仓库
3. 定期更换 API Key 和 Token（建议每 3 个月）
4. 如果 Secret 意外泄露，立即撤销并重新生成

⚠️ **GitHub Actions 使用限制**：
- 公开仓库：每月 2000 分钟免费额度
- 私有仓库：每月 2000 分钟免费额度
- 超出后按 $0.008/分钟 计费

---

**配置完成后，你的 WeSum 就可以自动运行了！** 🎉
