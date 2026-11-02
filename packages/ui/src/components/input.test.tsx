import { render, screen, fireEvent } from "@testing-library/react"
import { Input } from "./input.js"
import { describe, it, expect, vi } from "vitest"
/// <reference types="@testing-library/jest-dom" />

describe("Input", () => {
  it("renders with placeholder", () => {
    render(<Input placeholder="name" />)
    expect(screen.getByPlaceholderText("name")).toBeInTheDocument()
  })

  it("calls onChange when typed", () => {
    const onChange = vi.fn()
    render(<Input onChange={onChange} />)
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "abc" } })
    expect(onChange).toHaveBeenCalled()
  })

  it("is disabled when disabled prop set", () => {
    render(<Input disabled />)
    expect(screen.getByRole("textbox")).toBeDisabled()
  })
})
