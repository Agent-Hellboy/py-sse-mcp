# A Simple Framework for Creating an MCP Server

**Note:** Tested only with Cursor.

This project was created after encountering several issues with [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk). The basic setup was inspired by [b3nelof0n/node-mcp-server](https://github.com/b3nelof0n/node-mcp-server/blob/main/server.js).


```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>MCP Server Sequence Diagram</title>
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    import { mermaidDiagram } from './mermaid.js';
    mermaid.initialize({ startOnLoad: true });
    document.addEventListener('DOMContentLoaded', () => {
      document.getElementById('diagram').innerHTML = `<pre class='mermaid'>${mermaidDiagram}</pre>`;
      mermaid.run();
    });
  </script>
</head>
<body>
  <h2>MCP Server Sequence Diagram</h2>
  <div id="diagram"></div>
</body>
</html>
```

