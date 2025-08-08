"use client"

import { LoginForm } from "@/components/login-form"
import { useAuth } from "@/lib/auth"
import { useRouter } from "next/navigation"
import * as React from "react"

export default function Page() {
  const { isAuthenticated } = useAuth()
  const router = useRouter()
  React.useEffect(() => {
    if (isAuthenticated) router.replace("/dashboard")
  }, [isAuthenticated, router])
  return (
    <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm">
        <LoginForm />
      </div>
    </div>
  )
}
