#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

// 默认配置
const DEFAULT_CONFIG = {
  sourceDir: "topics", // 源文件目录
  docsDir: "docs", // 文档输出目录
  sidebarName: "_sidebar.md", // 侧边栏文件名
  title: "", // 侧边栏标题
  ignoreFiles: [".DS_Store", "Thumbs.db"], // 忽略的文件
  ignoreDirs: [".git", "node_modules"], // 忽略的目录
  copySource: true, // 是否复制源文件到docs目录
  copyReadme: true, // 是否复制README.md
  listStyle: "*", // 列表样式：* 或 -
};

// 帮助信息
function showHelp() {
  console.log(`
Generate Sidebar for Documentation

Usage: 
  generate-sidebar [options]

Options:
  --source-dir <dir>     Source directory (default: "topics")
  --docs-dir <dir>       Documentation output directory (default: "docs")
  --sidebar-name <name>  Sidebar filename (default: "_sidebar.md")
  --title <title>        Sidebar title (default: "")
  --no-copy-source       Don't copy source files to docs directory
  --no-copy-readme       Don't copy README.md to docs directory
  --list-style <style>   List style (* or -) (default: "*")
  --help                 Show this help message

Example:
  generate-sidebar --source-dir content --docs-dir documentation --title "# My Docs"
`);
  process.exit(0);
}

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const config = { ...DEFAULT_CONFIG };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    switch (arg) {
      case "--help":
        showHelp();
        break;
      case "--source-dir":
        config.sourceDir = args[++i];
        break;
      case "--docs-dir":
        config.docsDir = args[++i];
        break;
      case "--sidebar-name":
        config.sidebarName = args[++i];
        break;
      case "--title":
        config.title = args[++i];
        break;
      case "--no-copy-source":
        config.copySource = false;
        break;
      case "--no-copy-readme":
        config.copyReadme = false;
        break;
      case "--list-style":
        const style = args[++i];
        if (style !== "*" && style !== "-") {
          console.error('List style must be either "*" or "-"');
          process.exit(1);
        }
        config.listStyle = style;
        break;
      default:
        console.error(`Unknown option: ${arg}`);
        showHelp();
    }
  }

  return config;
}

// 构建完整路径
function buildPaths(config) {
  const baseDir = process.cwd();
  return {
    sourceDir: path.join(baseDir, config.sourceDir),
    docsDir: path.join(baseDir, config.docsDir),
    docsSourceDir: path.join(baseDir, config.docsDir, config.sourceDir),
    sidebarPath: path.join(baseDir, config.docsDir, config.sidebarName),
    readmePath: path.join(baseDir, "README.md"),
    docsReadmePath: path.join(baseDir, config.docsDir, "README.md"),
  };
}

// 删除目录
function deleteDir(dir) {
  if (fs.existsSync(dir)) {
    fs.rmSync(dir, { recursive: true });
  }
}

// 复制目录
function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  fs.cpSync(src, dest, { recursive: true });
}

// 复制README文件
function copyReadme(paths) {
  if (fs.existsSync(paths.readmePath)) {
    fs.mkdirSync(path.dirname(paths.docsReadmePath), { recursive: true });
    fs.copyFileSync(paths.readmePath, paths.docsReadmePath);
  }
}

// 格式化文件名为标题
function formatTitle(filename) {
  let title = filename.replace(/\.md$/, "");
  title = title.replace(/-/g, " ").replace(/_/g, " ");
  return title
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

// 格式化目录名为标题
function formatDirTitle(dirname) {
  return dirname.charAt(0).toUpperCase() + dirname.slice(1);
}

// 递归扫描目录并生成侧边栏内容
function scanDirectory(config, dir, relativePath = "", level = 0) {
  let sidebarContent = "";
  const items = fs.readdirSync(dir);
  const indent = "  ".repeat(level);

  // 处理目录
  const directories = items.filter((item) => {
    const itemPath = path.join(dir, item);
    return (
      fs.statSync(itemPath).isDirectory() && !config.ignoreDirs.includes(item)
    );
  });

  // 处理文件
  const files = items.filter((item) => {
    const itemPath = path.join(dir, item);
    return (
      fs.statSync(itemPath).isFile() &&
      path.extname(item) === ".md" &&
      !config.ignoreFiles.includes(item)
    );
  });

  if (directories.length === 0 && files.length === 0) {
    return "";
  }

  // 处理目录
  for (const directory of directories) {
    const dirPath = path.join(dir, directory);
    const dirRelativePath = path.join(relativePath, directory);

    // 检查目录是否包含.md文件
    const hasMdFiles = (function checkForMdFiles(dir) {
      const items = fs.readdirSync(dir);
      for (const item of items) {
        const itemPath = path.join(dir, item);
        if (fs.statSync(itemPath).isFile() && path.extname(item) === ".md") {
          return true;
        }
        if (
          fs.statSync(itemPath).isDirectory() &&
          !config.ignoreDirs.includes(item)
        ) {
          if (checkForMdFiles(itemPath)) {
            return true;
          }
        }
      }
      return false;
    })(dirPath);

    if (hasMdFiles) {
      const dirTitle = formatDirTitle(directory);
      sidebarContent += `${indent}${config.listStyle} ${dirTitle}\n`;
      const subContent = scanDirectory(
        config,
        dirPath,
        dirRelativePath,
        level + 1
      );
      sidebarContent += subContent;
    }
  }

  // 处理文件
  for (const file of files) {
    const fileTitle = formatTitle(file);
    const filePath = path.join(relativePath, file);
    const encodedPath = filePath
      .split("/")
      .map((part) => encodeURIComponent(part))
      .join("/");
    sidebarContent += `${indent}${config.listStyle} [${fileTitle}](${config.sourceDir}/${encodedPath})\n`;
  }

  return sidebarContent;
}

// 主函数
function generateSidebar() {
  console.log("Generating sidebar...");

  try {
    // 解析命令行参数
    const config = parseArgs();
    const paths = buildPaths(config);

    // 创建docs目录
    fs.mkdirSync(paths.docsDir, { recursive: true });

    // 如果启用了源文件复制
    if (config.copySource) {
      deleteDir(paths.docsSourceDir);
      copyDir(paths.sourceDir, paths.docsSourceDir);
    }

    // 如果启用了README复制
    if (config.copyReadme) {
      copyReadme(paths);
    }

    // 复制 dependence 目录（包含 KaTeX 等依赖）
    const dependenceSrc = path.join(process.cwd(), "dependence");
    const dependenceDest = path.join(paths.docsDir, "dependence");
    if (fs.existsSync(dependenceSrc)) {
      copyDir(dependenceSrc, dependenceDest);
    }

    // 生成侧边栏内容
    let sidebarContent = config.title ? config.title + "\n\n" : "";
    sidebarContent += scanDirectory(config, paths.sourceDir);

    // 写入侧边栏文件
    fs.writeFileSync(paths.sidebarPath, sidebarContent);

    // 生成 404 页面
    const notFoundPath = path.join(paths.docsDir, "_404.md");
    const notFoundContent = `# 404 - 页面未找到

抱歉，您访问的页面不存在。

[返回首页](/)
`;
    fs.writeFileSync(notFoundPath, notFoundContent);

    console.log("Sidebar generated successfully!");
  } catch (error) {
    console.error("Error generating sidebar:", error);
    process.exit(1);
  }
}

// 执行主函数
generateSidebar();
