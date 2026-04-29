# Docsify + KaTeX 数学公式渲染解决方案

## 问题描述

在 Docsify 文档中使用 KaTeX 渲染 LaTeX 数学公式时，公式无法正常显示，而是以纯文本形式展现。

### 症状
- 公式显示为原始 LaTeX 代码，如 `\text{MA}_t = ...`
- 浏览器控制台显示 "KaTeX 渲染完成"，但公式未被渲染
- `HTML 内容包含 $$: false` 说明公式分隔符丢失

## 根本原因分析

### 1. Docsify Markdown 解析器破坏 LaTeX 语法

Docsify 使用 `marked` 作为 Markdown 解析器，它会：
- 将 `$$...$$` 当作普通文本处理
- 将 `\[...\]` 中的反斜杠转义掉，变成 `[...]`
- 导致 KaTeX 找不到正确的分隔符

### 2. 脚本加载时机问题

- 使用 `defer` 属性会导致 KaTeX 脚本延迟加载
- `doneEach` 钩子可能在 KaTeX 加载前执行
- 导致 `renderMathInElement` 函数未定义

### 3. 钩子选择错误

- `afterEach` 在 HTML 字符串生成后、插入 DOM 前执行
- `doneEach` 在 DOM 更新完成后触发
- 需要在正确的时机进行内容转换和渲染

## 解决方案

### 核心思路

使用 **代码块语法** + **双钩子机制**：

1. Markdown 中使用 ````math` 代码块包裹公式（不会被破坏）
2. `afterEach` 钩子将 `<pre>` 转换为 `<div>$$...$$</div>`
3. `doneEach` 钩子调用 KaTeX 渲染

### 实现步骤

#### 1. Markdown 文件中的公式语法

**块级公式**：
````markdown
```math
\text{MA}_t = \frac{P_{t} + P_{t-1} + \dots + P_{t-n+1}}{n}
```
````

**行内公式**：
```markdown
其中 $\alpha = \frac{2}{n+1}$
```

#### 2. Docsify 配置（generate-index.js）

```javascript
window.$docsify = {
  // ... 其他配置 ...
  
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
      
      // afterEach: 在 HTML 生成后转换 math 代码块
      hook.afterEach(function (html, next) {
        html = html.replace(/<pre[^>]*data-lang="math"[^>]*><code[^>]*>([\\s\\S]*?)<\\/code><\\/pre>/g, function(match, code) {
          const decoded = code.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
          return '<div>$$' + decoded + '$$</div>';
        });
        next(html);
      });
      
      // doneEach: 在 DOM 更新后调用 KaTeX 渲染
      hook.doneEach(function () {
        mermaid.init(undefined, '.mermaid');
        
        const el = document.querySelector('.markdown-section');
        if (el && typeof renderMathInElement !== 'undefined') {
          renderMathInElement(el, {
            delimiters: [
              {left: "$$", right: "$$", display: true},
              {left: "$", right: "$", display: false}
            ],
            throwOnError: false
          });
        }
      });
    }
  ]
};
```

#### 3. HTML 文件中的脚本加载顺序

```html
<!-- Docsify v4 -->
<script src="//cdn.jsdelivr.net/npm/docsify@4"></script>

<!-- Search 插件必须紧跟 Docsify 之后 -->
<script src="//cdn.jsdelivr.net/npm/docsify/lib/plugins/search.min.js"></script>

<!-- KaTeX JS（移除 defer 属性） -->
<script src="./dependence/katex/katex.min.js"></script>
<script src="./dependence/katex/contrib/auto-render.min.js"></script>

<!-- 其他插件 -->
```

#### 4. 本地 KaTeX 文件部署

在 `generate-sidebar.js` 中添加：

```javascript
// 复制 dependence 目录（包含 KaTeX 等依赖）
const dependenceSrc = path.join(process.cwd(), "dependence");
const dependenceDest = path.join(paths.docsDir, "dependence");
if (fs.existsSync(dependenceSrc)) {
  copyDir(dependenceSrc, dependenceDest);
}
```

## 关键技术点

### 1. 正则表达式转义

在模板字符串中使用正则表达式时，需要双重转义：

```javascript
// ❌ 错误：会导致语法错误
html.replace(/```math\n([\s\S]*?)```/g, ...)

// ✅ 正确：双重转义
html.replace(/<pre[^>]*><code[^>]*>([\\s\\S]*?)<\\/code><\\/pre>/g, ...)
```

### 2. HTML 实体解码

从 `<code>` 标签中提取的内容包含 HTML 实体，需要解码：

```javascript
const decoded = code
  .replace(/&lt;/g, '<')
  .replace(/&gt;/g, '>')
  .replace(/&amp;/g, '&');
```

### 3. 钩子执行顺序

```
beforeEach → afterEach → (DOM 插入) → doneEach
```

- `beforeEach`: 处理 Markdown 原始内容
- `afterEach`: 处理生成的 HTML 字符串
- `doneEach`: 操作已渲染的 DOM

### 4. 禁用自动格式化

在 `.vscode/settings.json` 中：

```json
{
  "editor.formatOnSave": false,
  "[markdown]": {
    "editor.formatOnSave": false,
    "editor.defaultFormatter": null
  }
}
```

防止编辑器自动将 `_` 替换为 `*`。

## 调试技巧

### 1. 检查 KaTeX 加载状态

```javascript
console.log('KaTeX loaded:', typeof katex);
console.log('renderMathInElement loaded:', typeof renderMathInElement);
```

### 2. 查看 HTML 内容

```javascript
const el = document.querySelector('.markdown-section');
console.log('HTML 内容包含 $$:', el.innerHTML.includes('$$'));
console.log('HTML 前 500 字符:', el.innerHTML.substring(0, 500));
```

### 3. 查看原始 Markdown

```javascript
fetch('/topics/股票/MA.md').then(r => r.text()).then(console.log)
```

### 4. 手动触发渲染

在控制台执行：

```javascript
renderMathInElement(document.querySelector('.markdown-section'))
```

## 常见问题

### Q1: 公式仍然不渲染

**检查清单：**
- [ ] KaTeX CSS 和 JS 是否正确加载（Network 面板查看）
- [ ] 控制台是否显示 "HTML 内容包含 $$: true"
- [ ] Markdown 文件是否使用了 ````math` 代码块语法
- [ ] 是否移除了脚本的 `defer` 属性

### Q2: `_` 被自动替换为 `*`

**解决方案：**
- 禁用 Markdown 自动格式化
- 检查 Prettier/Typora 等工具的设置

### Q3: Search 插件报错 "$docsify is not defined"

**解决方案：**
- 将 Search 插件的 `<script>` 标签放在 Docsify 主脚本之后
- 确保插件加载顺序正确

### Q4: KaTeX 不支持 `\text{}` 内的中文

**问题现象：**
- 公式中使用 `\text{收盘价}` 等中文文本无法渲染
- 控制台可能显示 KaTeX 错误

**解决方案：**
- 将中文说明移到公式代码块外面
- 使用简洁的数学符号（如 $H$, $L$, $C$ 等）
- 在公式下方用列表说明符号含义

**示例：**

❌ 错误写法：
````markdown
```math
\text{RSV} = \frac{\text{收盘价} - \text{最低价}}{\text{最高价} - \text{最低价}} \times 100
```
````

✅ 正确写法：
````markdown
```math
RSV = \frac{C - L}{H - L} \times 100
```

其中：
- $C$ = 收盘价
- $L$ = 最低价
- $H$ = 最高价
````

### Q5: 修改 Markdown 后公式仍显示旧内容

**问题现象：**
- 更新了 `.md` 文件中的公式
- 重新生成了文档
- 浏览器中仍显示旧的公式

**解决方案：**

1. **硬刷新浏览器**（清除缓存）：
   - **Windows/Linux**: `Ctrl + Shift + R`
   - **macOS**: `Cmd + Shift + R`

2. **清除浏览器缓存**：
   - Chrome: 开发者工具 (F12) → Network 标签 → 勾选 "Disable cache"
   - 或访问 `chrome://settings/clearBrowserData` 清除缓存

3. **在控制台强制刷新**：
   ```javascript
   location.reload(true)  // 强制重新加载，忽略缓存
   ```

4. **直接访问 Markdown 文件验证**：
   ```
   http://127.0.0.1:3000/topics/股票/文件名.md
   ```
   查看是否是最新内容

> 💡 **提示**：Docsify 会缓存已访问的 Markdown 文件，修改后务必硬刷新浏览器。

## 最终效果

✅ 块级公式正常渲染  
✅ 行内公式正常渲染  
✅ 本地 KaTeX 文件加载  
✅ 无控制台错误  
✅ Markdown 语法不被破坏  

## 参考资源

- [KaTeX 官方文档](https://katex.org/)
- [Docsify 插件开发](https://docsify.js.org/#/plugins)
- [Auto-render Extension](https://katex.org/docs/autorender.html)

---

**最后更新：** 2025年12月17日  
**解决时长：** 约 2 小时  
**关键突破点：** 使用代码块 + afterEach 钩子转换
