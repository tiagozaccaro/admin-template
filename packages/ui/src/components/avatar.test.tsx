import { render, screen } from "@testing-library/react"
import { Avatar, AvatarFallback } from "./avatar.js"
import { describe, it, expect } from "vitest"
/// <reference types="@testing-library/jest-dom" />

describe("Avatar", () => {
  it("renders fallback", () => {
    render(
      <Avatar>
        <AvatarFallback>AB</AvatarFallback>
      </Avatar>
    )
    expect(screen.getByText("AB")).toBeInTheDocument()
  })
})
