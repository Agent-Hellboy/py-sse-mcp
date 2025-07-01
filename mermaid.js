// Mermaid diagram for the FastAPI MCP server and tools integration

const mermaidDiagram = `sequenceDiagram
    participant Client
    participant Server
    participant ToolsPy as "tools.py"
    Client->>Server: Connects to /sse-cursor (SSE)
    Server->>Client: Sends sessionId and endpoint
    loop While session active
        Client->>Server: POST /message?sessionId=... (JSON-RPC)
        alt initialize
            Server->>Client: protocolVersion, capabilities, serverInfo
        else tools/list
            Server->>ToolsPy: Load TOOLS_REGISTRY
            ToolsPy-->>Server: List of tools
            Server->>Client: List of tools
        else tools/call
            Server->>ToolsPy: Call tool function with arguments
            ToolsPy-->>Server: Tool result
            Server->>Client: Tool result
        else notifications/initialized
            Server-->>Client: (No SSE needed)
        else unknown method
            Server->>Client: Error message
        end
    end
    Client-->>Server: Disconnects SSE
`;

// Export or use this string as needed in your rendering setup 