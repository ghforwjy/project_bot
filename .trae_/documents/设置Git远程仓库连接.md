# 设置Git远程仓库连接计划

## 当前状态分析
- 项目根目录和前端目录都已初始化Git仓库
- 存在SSH私钥文件 `~/.ssh/traegithub`，但缺少对应的公钥文件
- SSH连接测试失败：`Permission denied (publickey)`
- 用户提供了公钥片段：`Aw2+ikHLw/6Fjf+iIBw+o1ar4awuJnRVD4FmOl6qUyg`

## 实施步骤

### 1. 从私钥生成公钥

```bash
# 生成公钥文件
ssh-keygen -y -f ~/.ssh/traegithub > ~/.ssh/traegithub.pub

# 查看公钥内容
Get-Content ~/.ssh/traegithub.pub
```

### 2. 配置SSH使用指定密钥

```bash
# 创建或修改SSH配置文件
cat > ~/.ssh/config << 'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/traegithub
  IdentitiesOnly yes
EOF
```

### 3. 测试SSH连接

```bash
# 测试与GitHub的SSH连接
ssh -T git@github.com
```

### 4. 为项目根目录设置远程仓库

```bash
# 在项目根目录执行
cd "e:\mycode\project_bot"

# 设置远程仓库（使用SSH地址）
git remote add origin git@github.com:ghforwjy/project_bot.git

# 验证远程连接
git remote -v

# 创建初始提交
git add .
git commit -m "Initial commit - complete project"

# 推送代码到远程仓库
git push -u origin master
```

### 5. 验证连接和推送

```bash
# 拉取远程仓库更新
git pull

# 测试后续推送
git push
```

## 需要用户确认的事项
1. **SSH公钥添加到GitHub**：需要用户手动在GitHub上添加生成的公钥
2. **远程仓库权限**：确保用户对ghforwjy/project_bot仓库有写入权限

## 预期结果
- 成功建立与GitHub的SSH连接
- 项目代码成功推送到远程仓库
- 本地与远程仓库建立稳定连接
- 后续开发可以正常使用git进行版本控制和协作
