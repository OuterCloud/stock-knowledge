#!/bin/bash

# 自定义变量
title="股票知识库"
description="股票知识库，记录股票相关问题及解决方案。"
theme="vue"

# 检查是否已经存在 docs 目录
if [ -d "docs" ]; then
  echo "The 'docs' directory already exists. Remove it..."
  rm -rf docs
fi

# 创建 docs 目录
echo "Creating 'docs' directory..."
mkdir -p docs

# 生成 index.html
chmod +x tools/generate-index.js
node tools/generate-index.js \
  --title "$title" \
  --description "$description" \
  --theme "$theme"

# 生成侧边栏和复制文件
chmod +x tools/generate-sidebar.js
node tools/generate-sidebar.js
echo "Documentation initialized successfully!"

# 通过 docsify 启动服务不支持指定 host
# docsify serve docs
NODE_NO_WARNINGS=1 http-server ./docs -p 3000 --fallback index.html
