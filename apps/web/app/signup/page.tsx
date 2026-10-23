"use client"

import { useRouter } from "next/navigation"

import { SignupForm } from "@workspace/ui/components/signup-form"

export default function Page() {
  const router = useRouter()

  const handleSubmit = async (data: { email: string; password: string; display_name?: string }) => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? ""}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      alert("Registration failed")
      return
    }
    router.push("/login")
  }

  return (
    <div className="flex min-h-svh flex-col items-center justify-center bg-muted p-6 md:p-10">
      <div className="w-full max-w-sm md:max-w-3xl">
        <SignupForm onSubmit={handleSubmit} />
      </div>
    </div>
  )
}
