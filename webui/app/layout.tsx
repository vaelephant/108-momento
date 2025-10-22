import type React from "react"
import type { Metadata } from "next/content"
import { Geist, Geist_Mono } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import { AuthProvider } from "@/lib/auth"
import { AdminProvider } from "@/lib/admin-auth"
import "./globals.css"

const _geist = Geist({ subsets: ["latin"] })
const _geistMono = Geist_Mono({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Momento - Your Photo Timeline",
  description: "A modern photo management platform with timeline view, categories, and smart tagging",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="zh-CN" className="light">
      <body className={`font-sans antialiased`}>
        <AuthProvider>
          <AdminProvider>
            {children}
          </AdminProvider>
        </AuthProvider>
        <Analytics />
      </body>
    </html>
  )
}
