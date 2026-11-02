import { render, screen, fireEvent } from "@testing-library/react"
import { Button } from "./button.js"
import { describe, it, expect, vi } from "vitest"
/// <reference types="@testing-library/jest-dom" />

describe("Button", () => {
  it("renders children", () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole("button", { name: "Click me" })).toBeInTheDocument()
  })

  it("calls onClick when clicked", () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Go</Button>)
    fireEvent.click(screen.getByRole("button", { name: "Go" }))
    expect(onClick).toHaveBeenCalledOnce()
  })

  it("is disabled when disabled prop set", () => {
    render(<Button disabled>Disabled</Button>)
    expect(screen.getByRole("button", { name: "Disabled" })).toBeDisabled()
  })
})
