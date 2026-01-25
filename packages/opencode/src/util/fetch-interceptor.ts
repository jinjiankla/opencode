import { HTTPLog } from "./http-log"

/**
 * 全局 Fetch 拦截器
 * 
 * 用于拦截所有 HTTP 请求并记录日志
 */
export namespace FetchInterceptor {
  let originalFetch: typeof fetch
  let _isInstalled = false

  /**
   * 安装全局 fetch 拦截器
   */
  export function install() {
    if (_isInstalled || !HTTPLog.isEnabled()) {
      return
    }

    // 保存原始 fetch
    originalFetch = globalThis.fetch

    // 替换全局 fetch
    globalThis.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const startTime = Date.now()
      const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
      const method = init?.method || 'GET'

      // 只拦截 AI provider 的请求
      const isAIRequest = 
        url.includes('api.openai.com') ||
        url.includes('api.anthropic.com') ||
        url.includes('generativelanguage.googleapis.com') ||
        url.includes('api.groq.com') ||
        url.includes('api.together.xyz') ||
        url.includes('api.perplexity.ai') ||
        url.includes('api.mistral.ai') ||
        url.includes('api.cohere.ai') ||
        url.includes('api.deepinfra.com') ||
        url.includes('api.cerebras.ai') ||
        url.includes('gateway.ai.cloudflare.com') ||
        url.includes('api.x.ai') ||
        url.includes('bedrock') ||
        url.includes('azure') ||
        url.includes('opencode.ai/api')

      if (!isAIRequest) {
        // 不是 AI 请求,直接调用原始 fetch
        return originalFetch(input, init)
      }

      // 提取 provider 和 model 信息
      const { provider, model } = extractProviderInfo(url, init)

      const headers = init?.headers ? Object.fromEntries(new Headers(init.headers).entries()) : {}
      
      let body: any
      if (init?.body) {
        try {
          body = typeof init.body === 'string' ? JSON.parse(init.body) : init.body
        } catch {
          body = init.body
        }
      }

      // 记录请求
      HTTPLog.logRequest(provider, model, url, method, headers, body)

      try {
        // 执行原始 fetch
        const response = await originalFetch(input, init)
        const duration = Date.now() - startTime

        // 克隆响应以便读取 body
        const clonedResponse = response.clone()
        
        let responseBody: any
        try {
          const contentType = response.headers.get('content-type')
          if (contentType?.includes('application/json')) {
            responseBody = await clonedResponse.json()
          } else if (contentType?.includes('text/') && !contentType?.includes('event-stream')) {
            responseBody = await clonedResponse.text()
          }
        } catch {
          // 无法解析响应体(可能是流式响应)
        }

        // 记录响应
        HTTPLog.logResponse(
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
        HTTPLog.logError(provider, model, error as Error, duration)
        throw error
      }
    }

    _isInstalled = true
  }

  /**
   * 卸载全局 fetch 拦截器
   */
  export function uninstall() {
    if (!_isInstalled) {
      return
    }

    // 恢复原始 fetch
    globalThis.fetch = originalFetch
    _isInstalled = false
  }

  /**
   * 从 URL 和请求中提取 provider 和 model 信息
   */
  function extractProviderInfo(url: string, init?: RequestInit): { provider: string; model: string } {
    let provider = 'unknown'
    let model = 'unknown'

    // 从 URL 推断 provider
    if (url.includes('api.openai.com')) {
      provider = 'openai'
    } else if (url.includes('api.anthropic.com')) {
      provider = 'anthropic'
    } else if (url.includes('generativelanguage.googleapis.com')) {
      provider = 'google'
    } else if (url.includes('api.groq.com')) {
      provider = 'groq'
    } else if (url.includes('api.together.xyz')) {
      provider = 'together'
    } else if (url.includes('api.perplexity.ai')) {
      provider = 'perplexity'
    } else if (url.includes('api.mistral.ai')) {
      provider = 'mistral'
    } else if (url.includes('api.cohere.ai')) {
      provider = 'cohere'
    } else if (url.includes('api.deepinfra.com')) {
      provider = 'deepinfra'
    } else if (url.includes('api.cerebras.ai')) {
      provider = 'cerebras'
    } else if (url.includes('gateway.ai.cloudflare.com')) {
      provider = 'cloudflare'
    } else if (url.includes('api.x.ai')) {
      provider = 'xai'
    } else if (url.includes('bedrock')) {
      provider = 'bedrock'
    } else if (url.includes('azure')) {
      provider = 'azure'
    } else if (url.includes('opencode.ai')) {
      provider = 'opencode'
    }

    // 从请求 body 中提取 model
    if (init?.body) {
      try {
        const body = typeof init.body === 'string' ? JSON.parse(init.body) : init.body
        if (body.model) {
          model = body.model
        }
      } catch {
        // 无法解析 body
      }
    }

    return { provider, model }
  }

  /**
   * 检查是否已安装
   */
  export function isInstalled(): boolean {
    return _isInstalled
  }
}
