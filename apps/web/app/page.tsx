"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function Page() {
  const router = useRouter()

  useEffect(() => {
    const isLoggedIn = document.cookie.includes("isLoggedIn=true") || localStorage.getItem("isLoggedIn") === "true"
    if (isLoggedIn) {
      router.push("/dashboard")
    } else {
      router.push("/login")
    }
  }, [router])

  return null
}
