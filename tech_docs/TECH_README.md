# 项目背景

利用 AI 构造文章生态闭环：股票用户常见问题收集->专业提示词模版构造->提示词生成->专业性文章生成->自动发文->渠道自动推文（引流获客）

## 🛠️ 结构

本仓库的组织结构如下：

```
code_knowledge/
├── topics/         # 各类话题
├── tools/          # 项目工具
└── resources/      # 资源文件
```

## 🚀 快速开始

1. 克隆本仓库：

   ```bash
   git clone <当前仓库地址>
   ```

2. 进入目录：

   ```bash
   cd stock_knowledge
   ```

3. 安装 docsify-cli 并部署服务：

   ```bash
   sudo npm i docsify-cli -g
   sudo npm i http-server -g
   which docsify
   ```

4. 启动服务：

   ```bash
   bash tools/init-docs.sh
   npm run docs
   ```

## 📄 许可证

本仓库采用 [MIT 许可证](LICENSE)。

## 🔔 更新计划

不断扩充各类股票知识和常见问题。

## 附录

下面是一些本项目所用到的其他资源：

- [Docsify 画图建模 Mermaid 插件支持](https://leader.js.cool/basic/md/docsify/)
