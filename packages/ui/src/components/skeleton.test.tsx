import { render } from "@testing-library/react"
import { Skeleton } from "./skeleton.js"
import { describe, it, expect } from "vitest"
/// <reference types="@testing-library/jest-dom" />

describe("Skeleton", () => {
  it("renders", () => {
    const { container } = render(<Skeleton className="h-4 w-4" />)
    expect(container.firstChild).toBeInTheDocument()
  })
})
