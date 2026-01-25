import { Log } from "./log"

/**
 * HTTP 请求日志记录器
 * 
 * 用于打印 LLM 调用的 HTTP 请求和响应详情
 * 
 * 启用方法:
 * export OPENCODE_HTTP_LOG=1
 * 或
 * export OPENCODE_DEBUG=1
 */
export namespace HTTPLog {
  const enabled = process.env.OPENCODE_HTTP_LOG === '1' || process.env.OPENCODE_DEBUG === '1'
  const verbose = process.env.OPENCODE_HTTP_VERBOSE === '1'
  
  const log = Log.create({ service: "http" })

  // 颜色代码
  const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    dim: '\x1b[2m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
  }

  /**
   * 格式化 JSON 输出
   */
  function formatJSON(obj: any, maxLength: number = 1000): string {
    const json = JSON.stringify(obj, null, 2)
    if (json.length > maxLength && !verbose) {
      return json.substring(0, maxLength) + `\n... (truncated, ${json.length - maxLength} more chars)`
    }
    return json
  }

  /**
   * 打印 HTTP 请求
   */
  export function logRequest(
    provider: string,
    model: string,
    url: string,
    method: string,
    headers: Record<string, string>,
    body: any,
  ) {
    if (!enabled) return

    const timestamp = new Date().toISOString()
    
    // 打印到 stderr (不影响正常输出)
    console.error(`\n${colors.cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}`)
    console.error(`${colors.bright}🌐 HTTP REQUEST${colors.reset} ${colors.dim}[${timestamp}]${colors.reset}`)
    console.error(`${colors.cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}`)
    console.error(`${colors.yellow}Provider:${colors.reset} ${provider}`)
    console.error(`${colors.yellow}Model:${colors.reset} ${model}`)
    console.error(`${colors.yellow}Method:${colors.reset} ${method}`)
    console.error(`${colors.yellow}URL:${colors.reset} ${url}`)
    
    // 打印 Headers
    console.error(`\n${colors.magenta}Headers:${colors.reset}`)
    const sanitizedHeaders = sanitizeHeaders(headers)
    for (const [key, value] of Object.entries(sanitizedHeaders)) {
      console.error(`  ${colors.dim}${key}:${colors.reset} ${value}`)
    }
    
    // 打印 Body
    if (body) {
      console.error(`\n${colors.magenta}Body:${colors.reset}`)
      const sanitizedBody = sanitizeBody(body)
      console.error(formatJSON(sanitizedBody))
    }
    
    console.error(`${colors.cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}\n`)

    // 同时写入日志文件
    log.info("http_request", {
      provider,
      model,
      method,
      url,
      headers: JSON.stringify(sanitizedHeaders),
      body: body ? JSON.stringify(sanitizeBody(body)) : undefined,
    })
  }

  /**
   * 打印 HTTP 响应
   */
  export function logResponse(
    provider: string,
    model: string,
    status: number,
    statusText: string,
    headers: Record<string, string>,
    body: any,
    duration: number,
  ) {
    if (!enabled) return

    const timestamp = new Date().toISOString()
    const statusColor = status >= 200 && status < 300 ? colors.green : colors.red
    
    console.error(`\n${colors.cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}`)
    console.error(`${colors.bright}📥 HTTP RESPONSE${colors.reset} ${colors.dim}[${timestamp}]${colors.reset}`)
    console.error(`${colors.cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}`)
    console.error(`${colors.yellow}Provider:${colors.reset} ${provider}`)
    console.error(`${colors.yellow}Model:${colors.reset} ${model}`)
    console.error(`${colors.yellow}Status:${colors.reset} ${statusColor}${status} ${statusText}${colors.reset}`)
    console.error(`${colors.yellow}Duration:${colors.reset} ${duration}ms`)
    
    // 打印 Headers
    console.error(`\n${colors.magenta}Headers:${colors.reset}`)
    for (const [key, value] of Object.entries(headers)) {
      console.error(`  ${colors.dim}${key}:${colors.reset} ${value}`)
    }
    
    // 打印 Body
    if (body) {
      console.error(`\n${colors.magenta}Body:${colors.reset}`)
      console.error(formatJSON(body))
    }
    
    console.error(`${colors.cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}\n`)

    // 同时写入日志文件
    log.info("http_response", {
      provider,
      model,
      status,
      statusText,
      duration,
      headers: JSON.stringify(headers),
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  /**
   * 打印 HTTP 错误
   */
  export function logError(
    provider: string,
    model: string,
    error: Error,
    duration: number,
  ) {
    if (!enabled) return

    const timestamp = new Date().toISOString()
    
    console.error(`\n${colors.red}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}`)
    console.error(`${colors.bright}❌ HTTP ERROR${colors.reset} ${colors.dim}[${timestamp}]${colors.reset}`)
    console.error(`${colors.red}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}`)
    console.error(`${colors.yellow}Provider:${colors.reset} ${provider}`)
    console.error(`${colors.yellow}Model:${colors.reset} ${model}`)
    console.error(`${colors.yellow}Duration:${colors.reset} ${duration}ms`)
    console.error(`${colors.yellow}Error:${colors.reset} ${colors.red}${error.message}${colors.reset}`)
    
    if (error.stack && verbose) {
      console.error(`\n${colors.magenta}Stack:${colors.reset}`)
      console.error(error.stack)
    }
    
    console.error(`${colors.red}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}\n`)

    // 同时写入日志文件
    log.error("http_error", {
      provider,
      model,
      duration,
      error: error.message,
      stack: error.stack,
    })
  }

  /**
   * 打印流式响应的 chunk
   */
  export function logStreamChunk(
    provider: string,
    model: string,
    chunk: any,
    index: number,
  ) {
    if (!enabled || !verbose) return

    console.error(`${colors.dim}📦 Stream Chunk #${index}:${colors.reset}`)
    console.error(formatJSON(chunk, 500))

    log.debug("http_stream_chunk", {
      provider,
      model,
      index,
      chunk: JSON.stringify(chunk),
    })
  }

  /**
   * 脱敏 Headers (隐藏敏感信息)
   */
  function sanitizeHeaders(headers: Record<string, string>): Record<string, string> {
    const sanitized: Record<string, string> = {}
    const sensitiveKeys = ['authorization', 'api-key', 'x-api-key', 'cookie', 'x-opencode-session']
    
    for (const [key, value] of Object.entries(headers)) {
      const lowerKey = key.toLowerCase()
      if (sensitiveKeys.some(k => lowerKey.includes(k))) {
        // 只显示前几个字符
        sanitized[key] = value.substring(0, 10) + '***'
      } else {
        sanitized[key] = value
      }
    }
    
    return sanitized
  }

  /**
   * 脱敏 Body (隐藏敏感信息)
   */
  function sanitizeBody(body: any): any {
    if (typeof body !== 'object' || body === null) {
      return body
    }

    // 深拷贝
    const sanitized = JSON.parse(JSON.stringify(body))

    // 如果消息太长,截断
    if (sanitized.messages && Array.isArray(sanitized.messages) && !verbose) {
      sanitized.messages = sanitized.messages.map((msg: any, index: number) => {
        if (index < 2 || index >= sanitized.messages.length - 2) {
          // 保留前2条和后2条完整消息
          return msg
        } else if (index === 2) {
          // 在中间添加省略标记
          return { role: 'system', content: `... (${sanitized.messages.length - 4} messages omitted) ...` }
        } else {
          // 跳过中间的消息
          return null
        }
      }).filter((msg: any) => msg !== null)
    }

    return sanitized
  }

  /**
   * 创建一个 fetch 拦截器
   */
  export function createFetchInterceptor(
    provider: string,
    model: string,
  ): (input: RequestInfo | URL, init?: RequestInit) => Promise<Response> {
    return async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const startTime = Date.now()
      const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
      const method = init?.method || 'GET'
      const headers = init?.headers ? Object.fromEntries(new Headers(init.headers).entries()) : {}
      
      let body: any
      if (init?.body) {
        try {
          body = typeof init.body === 'string' ? JSON.parse(init.body) : init.body
        } catch {
          body = init.body
        }
      }

      // 打印请求
      logRequest(provider, model, url, method, headers, body)

      try {
        // 执行原始 fetch
        const response = await fetch(input, init)
        const duration = Date.now() - startTime

        // 克隆响应以便读取 body
        const clonedResponse = response.clone()
        
        let responseBody: any
        try {
          const contentType = response.headers.get('content-type')
          if (contentType?.includes('application/json')) {
            responseBody = await clonedResponse.json()
          } else if (contentType?.includes('text/')) {
            responseBody = await clonedResponse.text()
          }
        } catch {
          // 无法解析响应体
        }

        // 打印响应
        logResponse(
          provider,
          model,
          response.status,
          response.statusText,
          Object.fromEntries(response.headers.entries()),
          responseBody,
          duration,
        )

        return response
      } catch (error) {
        const duration = Date.now() - startTime
        logError(provider, model, error as Error, duration)
        throw error
      }
    }
  }

  /**
   * 检查是否启用
   */
  export function isEnabled(): boolean {
    return enabled
  }

  /**
   * 检查是否启用详细模式
   */
  export function isVerbose(): boolean {
    return verbose
  }
}
