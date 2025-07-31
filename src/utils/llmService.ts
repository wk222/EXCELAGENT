import type { LLMSettings } from '../types'

export class LLMService {
  private settings: LLMSettings

  constructor(settings: LLMSettings) {
    this.settings = settings
  }

  async callLLM(prompt: string, options?: { temperature?: number; maxTokens?: number }): Promise<string> {
    if (!this.settings.apiKey) {
      throw new Error('请先配置API密钥')
    }

    const response = await fetch(`${this.settings.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.settings.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: this.settings.model,
        messages: [
          { role: 'user', content: prompt }
        ],
        temperature: options?.temperature ?? this.settings.temperature,
        max_tokens: options?.maxTokens ?? this.settings.maxTokens,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(`API调用失败: ${response.status} ${errorData.error?.message || response.statusText}`)
    }

    const data = await response.json()
    return data.choices[0]?.message?.content || ''
  }

  async generateDataAnalysis(dataContent: string, question: string): Promise<string> {
    const prompt = `你是一位数据分析专家。请分析以下Excel数据并回答用户问题。

用户问题: ${question}

数据内容:
${dataContent}

请提供：
1. 直接回答用户问题
2. 数据的关键发现和洞察
3. 可能的业务建议
4. 需要注意的数据质量问题

请用清晰、专业的中文回答，避免过于技术性的术语。`

    return this.callLLM(prompt)
  }

  async generateCodeSuggestion(dataContent: string, question: string): Promise<string> {
    const prompt = `作为数据分析专家，请根据以下数据和问题，建议适合的分析方法和可视化类型。

用户问题: ${question}

数据信息:
${dataContent}

请建议：
1. 适合的图表类型 (条形图、折线图、散点图、饼图等)
2. 应该关注的数据列
3. 可能的分析角度
4. 数据预处理建议

请用简洁的中文回答。`

    return this.callLLM(prompt, { maxTokens: 1000 })
  }

  async validateApiKey(): Promise<boolean> {
    try {
      await this.callLLM('测试连接', { maxTokens: 10 })
      return true
    } catch {
      return false
    }
  }
}