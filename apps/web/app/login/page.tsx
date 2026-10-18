"use client"

import { useRouter } from "next/navigation"

import { LoginForm } from "@workspace/ui/components/login-form"
import { startGoogleSignIn } from "@/lib/auth/google"

export default function Page() {
  const router = useRouter()

  const handleSubmit = () => {
    document.cookie = "isLoggedIn=true; path=/; max-age=3600"
    router.push("/dashboard")
  }

  return (
    <div className="flex min-h-svh flex-col items-center justify-center bg-muted p-6 md:p-10">
      <div className="w-full max-w-sm md:max-w-3xl">
        <LoginForm onSubmit={handleSubmit} onGoogleSignIn={startGoogleSignIn} />
      </div>
    </div>
  )
}
