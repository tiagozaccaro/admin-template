import { render, screen } from "@testing-library/react"
import { describe, it, expect } from "vitest"
import { LoadingState, ErrorState, EmptyState } from "@/components/states"

describe("states", () => {
  it("loading", () => {
    render(<LoadingState label="Loading data" />)
    expect(screen.getByText("Loading data")).toBeTruthy()
  })
  it("error", () => {
    render(<ErrorState message="boom" />)
    expect(screen.getByText("boom")).toBeTruthy()
  })
  it("empty", () => {
    render(<EmptyState title="No items" description="add one" />)
    expect(screen.getByText("No items")).toBeTruthy()
    expect(screen.getByText("add one")).toBeTruthy()
  })
})
