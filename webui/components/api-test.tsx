"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { apiClient } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

export function ApiTest() {
  const [isLoading, setIsLoading] = useState(false)
  const [testResults, setTestResults] = useState<string[]>([])
  const { toast } = useToast()

  const runTests = async () => {
    setIsLoading(true)
    setTestResults([])
    const results: string[] = []

    try {
      // 测试本地存储
      results.push("🔍 测试本地存储...")
      const hasLocalStorage = typeof Storage !== 'undefined'
      results.push(`✅ 本地存储: ${hasLocalStorage ? '支持' : '不支持'}`)
      
      // 测试文件API
      results.push("🔍 测试文件API...")
      const hasFileAPI = typeof File !== 'undefined' && typeof FileReader !== 'undefined'
      results.push(`✅ 文件API: ${hasFileAPI ? '支持' : '不支持'}`)
      
      // 测试URL API
      results.push("🔍 测试URL API...")
      const hasURLAPI = typeof URL !== 'undefined' && typeof URL.createObjectURL !== 'undefined'
      results.push(`✅ URL API: ${hasURLAPI ? '支持' : '不支持'}`)

      results.push("✅ 前端环境检查完成")
      results.push("💡 提示: 现在使用前端本地存储模式")

    } catch (error) {
      results.push(`❌ 测试失败: ${error}`)
    }

    setTestResults(results)
    setIsLoading(false)
    
    toast({
      title: "环境测试完成",
      description: "前端环境检查完成",
    })
  }

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle>前端环境测试</CardTitle>
        <CardDescription>
          测试前端环境是否支持所需功能
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button onClick={runTests} disabled={isLoading} className="w-full">
          {isLoading ? "测试中..." : "开始测试"}
        </Button>
        
        {testResults.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-medium">测试结果:</h4>
            <div className="bg-muted p-4 rounded-lg">
              {testResults.map((result, index) => (
                <div key={index} className="text-sm">
                  {result}
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
