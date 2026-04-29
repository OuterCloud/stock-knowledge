#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

// 默认配置
const DEFAULT_CONFIG = {
  title: "Your Docs Title",
  name: "Your Docs Name",
  description: "Your Docs Description",
  repo: "",
  theme: "vue",
  loadSidebar: true,
  subMaxLevel: 3,
  auto2top: true,
  search: true,
  copyCode: true,
  pagination: true,
  zoomImage: true,
  prismLanguages: ["bash", "php", "javascript", "json", "sql"],
  mermaid: true, // 新增 Mermaid 支持
};

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const config = { ...DEFAULT_CONFIG };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    switch (arg) {
      case "--title":
        config.title = args[++i];
        config.name = args[i]; // 同时更新name
        break;
      case "--description":
        config.description = args[++i];
        break;
      case "--repo":
        config.repo = args[++i];
        break;
      case "--theme":
        config.theme = args[++i];
        break;
      case "--no-sidebar":
        config.loadSidebar = false;
        break;
      case "--sub-max-level":
        config.subMaxLevel = parseInt(args[++i], 10);
        break;
      case "--no-auto2top":
        config.auto2top = false;
        break;
      case "--no-search":
        config.search = false;
        break;
      case "--no-copy-code":
        config.copyCode = false;
        break;
      case "--no-pagination":
        config.pagination = false;
        break;
      case "--no-zoom-image":
        config.zoomImage = false;
        break;
      case "--prism-languages":
        config.prismLanguages = args[++i].split(",");
        break;
      case "--help":
        showHelp();
        process.exit(0);
    }
  }

  return config;
}

// 显示帮助信息
function showHelp() {
  console.log(`
Generate docsify index.html file

Usage:
  generate-index [options]

Options:
  --title <title>           Set document title and name (required)
  --description <desc>      Set document description
  --repo <url>             Set repository URL
  --theme <theme>          Set theme (vue, buble, dark, pure)
  --no-sidebar             Disable sidebar
  --sub-max-level <n>      Set maximum sub-level for TOC
  --no-auto2top           Disable auto scroll to top
  --no-search             Disable search
  --no-copy-code          Disable copy code button
  --no-pagination         Disable pagination
  --no-zoom-image         Disable image zoom
  --prism-languages <list> Set Prism languages (comma-separated)
  --help                  Show this help message

Example:
  generate-index --title "My Docs" --description "My awesome docs" --theme dark
`);
}

// 生成index.html内容
function generateIndexHtml(config) {
  return `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>${config.title}</title>
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
    <meta name="description" content="${config.description}" />
    <meta
      name="viewport"
      content="width=device-width, initial-scale=1.0, minimum-scale=1.0"
    />
    <link
      rel="stylesheet"
      href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/${config.theme}.css"
    />
    <!-- KaTeX CSS -->
    <link rel="stylesheet" href="./dependence/katex/katex.min.css">
    ${
      config.mermaid
        ? '<link rel="stylesheet" href="//unpkg.com/mermaid/dist/mermaid.min.css" />'
        : ""
    }
    ${
      config.mermaid
        ? '<script type="text/javascript" src="//unpkg.com/mermaid/dist/mermaid.min.js"></script>'
        : ""
    }
  </head>
  <body>
    <div id="app"></div>
    <script>
      window.$docsify = {
        name: ${JSON.stringify(config.name)},
        repo: ${JSON.stringify(config.repo)},
        loadSidebar: ${config.loadSidebar},
        alias: {
          '/_sidebar.md': '/_sidebar.md',
          '/topics/_sidebar.md': '/_sidebar.md',
          '/topics/*/_sidebar.md': '/_sidebar.md'
        },
        auto2top: ${config.auto2top},
        markdown: {
          renderer: {
            code: function (code, lang) {
              if (code.match(/^sequenceDiagram/) || code.match(/^graph/) || code.match(/^gantt/)) {
                return '<div class="mermaid">' + code + '</div>';
              }
              // 如果是 math 代码块，保护 LaTeX 内容
              if (lang === 'math' || lang === 'latex') {
                return '<div>$$' + code + '$$</div>';
              }
              var hl = Prism.highlight(code, Prism.languages[lang] || Prism.languages.markup);
              return '<pre v-pre data-lang="' + lang + '"><code class="lang-' + lang + '">' + hl + '</code></pre>';
            }
          }
        },
        plugins: [
          function (hook, vm) {
            hook.ready(function () {
              mermaid.initialize({ startOnLoad: false });
            });
            hook.afterEach(function (html, next) {
              // 在 HTML 生成后，将 <code class="lang-math"> 转换为 $$
              html = html.replace(/<pre[^>]*data-lang="math"[^>]*><code[^>]*>([\\s\\S]*?)<\\/code><\\/pre>/g, function(match, code) {
                // 解码 HTML 实体
                const decoded = code.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
                return '<div>$$' + decoded + '$$</div>';
              });
              next(html);
            });
            hook.doneEach(function () {
              mermaid.init(undefined, '.mermaid');
              // KaTeX 渲染 - 在 DOM 更新完成后触发
              const el = document.querySelector('.markdown-section');
              if (el && typeof renderMathInElement !== 'undefined') {
                console.log('开始 KaTeX 渲染...');
                console.log('HTML 内容包含 $$:', el.innerHTML.includes('$$'));
                console.log('HTML 内容:', el.innerHTML.substring(0, 500));
                renderMathInElement(el, {
                  delimiters: [
                    {left: "$$", right: "$$", display: true},
                    {left: "$", right: "$", display: false}
                  ],
                  throwOnError: false
                });
                console.log('KaTeX 渲染完成');
              } else {
                console.error('renderMathInElement 未加载！');
              }
            });
          }
        ],
        ${
          config.search
            ? `search: {
          maxAge: 86400000,
          paths: "auto",
          placeholder: "Type to search",
          noData: "No Results!",
          depth: 6,
        },`
            : ""
        }
        ${
          config.pagination
            ? `pagination: {
          previousText: "Previous",
          nextText: "Next",
          crossChapter: true,
          crossChapterText: true,
        },`
            : ""
        }
      };
    </script>
    ${
      config.mermaid
        ? "<script>mermaid.initialize({ startOnLoad: true });</script>"
        : ""
    }
    <!-- Docsify v4 -->
    <script src="//cdn.jsdelivr.net/npm/docsify@4"></script>
    ${
      config.search
        ? '<!-- Search -->\n    <script src="//cdn.jsdelivr.net/npm/docsify/lib/plugins/search.min.js"></script>'
        : ""
    }
    <!-- KaTeX JS (移除 defer，确保在 doneEach 前加载) -->
    <script src="./dependence/katex/katex.min.js"></script>
    <!-- KaTeX auto-render -->
    <script src="./dependence/katex/contrib/auto-render.min.js"></script>
    ${
      config.copyCode
        ? '<!-- Copy to Clipboard -->\n    <script src="//cdn.jsdelivr.net/npm/docsify-copy-code/dist/docsify-copy-code.min.js"></script>'
        : ""
    }
    ${
      config.pagination
        ? '<!-- Pagination -->\n    <script src="//cdn.jsdelivr.net/npm/docsify-pagination/dist/docsify-pagination.min.js"></script>'
        : ""
    }
    ${
      config.zoomImage
        ? '<!-- Zoom image -->\n    <script src="//cdn.jsdelivr.net/npm/docsify/lib/plugins/zoom-image.min.js"></script>'
        : ""
    }
    ${
      config.prismLanguages.length > 0
        ? "<!-- Prism syntax highlighting -->"
        : ""
    }
${config.prismLanguages
  .map(
    (lang) =>
      `    <script src="//cdn.jsdelivr.net/npm/prismjs@1/components/prism-${lang}.min.js"></script>`
  )
  .join("\n")}
  </body>
</html>
`;
}

// 主函数
function main() {
  try {
    const config = parseArgs();
    const indexPath = path.join(process.cwd(), "docs", "index.html");

    // 确保docs目录存在
    fs.mkdirSync(path.dirname(indexPath), { recursive: true });

    // 生成并写入index.html
    const content = generateIndexHtml(config);
    fs.writeFileSync(indexPath, content);

    console.log("Successfully generated docs/index.html");
  } catch (error) {
    console.error("Error:", error.message);
    process.exit(1);
  }
}

// 执行主函数
main();
