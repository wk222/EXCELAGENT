import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { ExcelData, LLMSettings, AnalysisResult, Theme } from '../types'

interface AppState {
  // Theme
  theme: 'light' | 'dark'
  setTheme: (theme: 'light' | 'dark') => void

  // Excel data
  excelData: ExcelData | null
  setExcelData: (data: ExcelData | null) => void
  setCurrentSheet: (sheetName: string) => void

  // LLM settings
  llmSettings: LLMSettings
  updateLLMSettings: (settings: Partial<LLMSettings>) => void

  // Analysis stages
  stage1Result: AnalysisResult | null
  stage2Result: AnalysisResult | null
  stage3Result: AnalysisResult | null
  setStageResult: (stage: 1 | 2 | 3, result: AnalysisResult | null) => void

  // UI state
  sidebarCollapsed: boolean
  setSidebarCollapsed: (collapsed: boolean) => void
  isProcessing: boolean
  setIsProcessing: (processing: boolean) => void

  // Reset functions
  resetAnalysisStages: () => void
  resetAll: () => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Theme
      theme: 'light',
      setTheme: (theme) => set({ theme }),

      // Excel data
      excelData: null,
      setExcelData: (data) => set({ excelData: data }),
      setCurrentSheet: (sheetName) => {
        const { excelData } = get()
        if (excelData) {
          set({
            excelData: {
              ...excelData,
              currentSheet: sheetName,
            },
          })
        }
      },

      // LLM settings
      llmSettings: {
        model: 'gpt-3.5-turbo',
        temperature: 0.7,
        maxTokens: 2000,
        apiKey: '',
        baseUrl: 'https://api.openai.com/v1',
      },
      updateLLMSettings: (settings) =>
        set((state) => ({
          llmSettings: { ...state.llmSettings, ...settings },
        })),

      // Analysis stages
      stage1Result: null,
      stage2Result: null,
      stage3Result: null,
      setStageResult: (stage, result) => {
        const key = `stage${stage}Result` as keyof Pick<AppState, 'stage1Result' | 'stage2Result' | 'stage3Result'>
        set({ [key]: result })
      },

      // UI state
      sidebarCollapsed: false,
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      isProcessing: false,
      setIsProcessing: (processing) => set({ isProcessing: processing }),

      // Reset functions
      resetAnalysisStages: () =>
        set({
          stage1Result: null,
          stage2Result: null,
          stage3Result: null,
        }),
      resetAll: () =>
        set({
          excelData: null,
          stage1Result: null,
          stage2Result: null,
          stage3Result: null,
          isProcessing: false,
        }),
    }),
    {
      name: 'excel-ai-agent-storage',
      partialize: (state) => ({
        theme: state.theme,
        llmSettings: state.llmSettings,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
)